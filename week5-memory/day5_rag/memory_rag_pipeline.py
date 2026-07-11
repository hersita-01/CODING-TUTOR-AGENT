"""
memory_rag_pipeline.py

Week 5 / Day 5 - Memory + RAG Integration
------------------------------------------
This is the orchestration layer for Day 5. It wires together:

    Student message
        -> Load learner profile        (MemoryManager.get_or_create)
        -> Run existing tools           (caller's responsibility; result passed in)
        -> Retrieve documentation       (rag_context_builder.build_rag_context)
        -> Build personalized context   (learning_context_builder.build_learning_context)
        -> Generate Socratic response   (caller-supplied generator function)
        -> Update learner memory        (MemoryManager methods)
        -> Save profile                 (MemoryManager persistence)

Rather than importing a concrete LLM-calling function from Week 4 (which
would create a circular import, since Week 4 needs to import *this*
module), `MemoryRAGPipeline` accepts a `response_generator` callable at
construction time. This keeps Day 5 fully decoupled from Week 4's prompt
templates while still letting `week4_mini_tutor.py` drive the whole flow
through a single call.

Only these `MemoryManager` methods are used, per the Day 5 spec:
    - get_or_create()
    - update_from_run_result()
    - append_interaction()
    - record_topic()
    - mark_mastered()
    - mark_struggling()

No other MemoryManager, ChromaManager, or EmbeddingManager APIs are
touched or modified.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path bootstrap: make sibling Week 5 modules importable (hyphenated dirs)
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WEEK5_DIR = os.path.dirname(_THIS_DIR)  # .../week5-memory
_DAY1_DIR = os.path.join(_WEEK5_DIR, "day1-learner-memory")

if _DAY1_DIR not in sys.path:
    sys.path.insert(0, _DAY1_DIR)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

try:
    from memory_manager import MemoryManager  # type: ignore
except ImportError as exc:  # pragma: no cover - defensive import guard
    logger.error(
        "Could not import MemoryManager from %s. Error: %s", _DAY1_DIR, exc
    )
    MemoryManager = None  # type: ignore

from learning_context_builder import build_learning_context
from rag_context_builder import build_rag_context
from learner_profile import LearnerProfile

# Type alias for the caller-supplied generation function. It receives the
# fully assembled prompt context and returns the tutor's text response.
ResponseGenerator = Callable[[str, "TutorPromptContext"], str]

# Maximum characters allowed when serializing large payloads (e.g. tool
# results) for logging/transmission. Kept as module-level constant so it's
# easy to tune without hunting through method bodies.
_MAX_SERIALIZED_CHARS = 2000


def safe_json_dumps(data: Any, max_chars: int = _MAX_SERIALIZED_CHARS) -> str:
    """Serialize `data` to JSON, truncating safely if it's too large.

    Naively slicing a JSON string (e.g. `dumped[:2000]`) can cut in the
    middle of a value and produce invalid JSON. This instead serializes
    first, and if the result is too long, wraps a *valid* JSON object
    around a truncated preview so the output always parses.

    Args:
        data: Any JSON-serializable object (falls back to `str()` for
            non-serializable values via `default=str`).
        max_chars: Maximum length of the returned string before falling
            back to the truncated-preview format.

    Returns:
        A valid JSON string, either the full serialization or a
        `{"truncated": true, "preview": ...}` wrapper.
    """
    serialized = json.dumps(data, indent=2, default=str)
    if len(serialized) <= max_chars:
        return serialized

    return json.dumps(
        {
            "truncated": True,
            "preview": serialized[:max_chars],
        },
        indent=2,
    )


@dataclass
class TutorPromptContext:
    """All context assembled for a single tutoring turn.

    Attributes:
        student_id: Identifier for the learner.
        student_message: The raw incoming message from the student.
        learning_context: Formatted summary of the learner's history.
        rag_context: Formatted, retrieved documentation relevant to the message.
        tool_results: Raw results from any tools already run this turn
            (e.g. sandbox code execution), passed through unchanged so the
            generator can reference them if needed.
    """

    student_id: str
    student_message: str
    learning_context: str
    rag_context: str
    tool_results: Optional[Dict[str, Any]] = field(default=None)

    def as_prompt_block(self) -> str:
        """Combine learning + RAG context (and tool results, if any) into
        a single injectable block.

        Returns:
            A single string containing the context sections, ready to be
            appended to (or interpolated into) the tutor's system prompt.
        """
        sections = [
            self.learning_context,
            self.rag_context,
        ]

        if self.tool_results:
            sections.append(
                "## Tool Results\n" + safe_json_dumps(self.tool_results)
            )

        return "\n\n".join(sections)


class MemoryRAGPipeline:
    """Coordinates learner memory and RAG retrieval around a response generator.

    This class does not generate text itself. It is deliberately a thin
    coordinator: memory lives in `MemoryManager`, retrieval lives in
    `rag_context_builder`, and generation lives wherever the caller's LLM
    call is implemented (Week 4). This keeps each concern in exactly one
    place, matching the existing modular structure of the project.
    """

    def __init__(
        self,
        response_generator: ResponseGenerator,
        memory_manager: Optional["MemoryManager"] = None,
        rag_top_k: int = 4,
    ) -> None:
        """Initialize the pipeline.

        Args:
            response_generator: A callable `(prompt_context_block, TutorPromptContext) -> str`
                that produces the tutor's Socratic response. Typically a thin
                wrapper around the existing Week 3/4 tool-calling agent.
            memory_manager: An existing `MemoryManager` instance to reuse
                (e.g. one already holding an open DB connection). If not
                provided, a new one is constructed.
            rag_top_k: Number of documentation chunks to retrieve per turn.
                Must be a positive integer.

        Raises:
            RuntimeError: If `MemoryManager` could not be imported and no
                instance was supplied.
            ValueError: If `rag_top_k` is not a positive integer.
        """
        if memory_manager is not None:
            self.memory_manager = memory_manager
        elif MemoryManager is not None:
            self.memory_manager = MemoryManager()
        else:
            raise RuntimeError(
                "MemoryManager is unavailable. Ensure "
                "week5-memory/day1-learner-memory/memory_manager.py is "
                "importable, or pass an existing instance explicitly."
            )

        if not isinstance(rag_top_k, int) or rag_top_k <= 0:
            raise ValueError(
                f"rag_top_k must be a positive integer, got {rag_top_k!r}"
            )

        self.response_generator = response_generator
        self.rag_top_k = rag_top_k

        # Per-student locks, created lazily and kept in a plain dict rather
        # than a defaultdict so the set of keys is explicit and bounded by
        # actual student activity. `_locks_guard` protects concurrent
        # creation of a new per-student lock (not the per-student critical
        # section itself, which callers acquire via `_get_lock`).
        self._locks: Dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def _get_lock(self, student_id: str) -> threading.Lock:
        """Return the lock for `student_id`, creating it if needed.

        Args:
            student_id: Identifier for the learner.

        Returns:
            The `threading.Lock` associated with this student. Callers
            should use this as a context manager around any critical
            section touching that student's profile:

                with self._get_lock(student_id):
                    ...
        """
        with self._locks_guard:
            return self._locks.setdefault(student_id, threading.Lock())

    # ------------------------------------------------------------------
    # Step 1-4: load profile, run existing tools (caller's job), retrieve,
    # and build context.
    # ------------------------------------------------------------------
    def build_context(
        self,
        student_id: str,
        student_message: str,
        tool_results: Optional[Dict[str, Any]] = None,
    ) -> tuple[LearnerProfile, TutorPromptContext]:
        """Load the learner profile and assemble the full prompt context.

        Args:
            student_id: Identifier for the learner (used by MemoryManager).
            student_message: The student's raw message this turn.
            tool_results: Any results already produced by existing tools
                (e.g. sandbox execution output) that ran earlier in the
                turn, passed through for the generator's reference.

        Returns:
            A tuple of (profile, TutorPromptContext).
        """
        logger.info("Loading learner profile for student_id=%s", student_id)
        profile = self.memory_manager.get_or_create(student_id)

        learning_context = build_learning_context(profile)
        rag_context = build_rag_context(student_message, top_k=self.rag_top_k)

        prompt_context = TutorPromptContext(
            student_id=student_id,
            student_message=student_message,
            learning_context=learning_context,
            rag_context=rag_context,
            tool_results=tool_results,
        )
        return profile, prompt_context

    # ------------------------------------------------------------------
    # Step 5: generate response (delegated to caller-supplied generator)
    # ------------------------------------------------------------------
    def generate_response(self, prompt_context: TutorPromptContext) -> str:
        """Invoke the caller-supplied response generator.

        If the generator raises, this degrades gracefully by returning a
        safe fallback message rather than propagating the exception and
        aborting the whole turn (memory update, persistence, etc. can
        still proceed with the fallback text).

        Args:
            prompt_context: The assembled `TutorPromptContext` for this turn.

        Returns:
            The tutor's generated Socratic response text, or a fallback
            message if generation failed.
        """
        combined_block = prompt_context.as_prompt_block()
        logger.debug(
            "Generating response for student_id=%s (%d context chars)",
            prompt_context.student_id,
            len(combined_block),
        )
        try:
            return self.response_generator(combined_block, prompt_context)
        except Exception:
            logger.exception(
                "response_generator failed for student_id=%s; "
                "returning fallback response",
                prompt_context.student_id,
            )
            return (
                "I'm having trouble generating a response right now. "
                "Please try again in a moment."
            )

    # ------------------------------------------------------------------
    # Step 6-7: update learner memory
    # ------------------------------------------------------------------
    def update_memory(
        self,
        profile: LearnerProfile,
        student_message: str,
        tutor_response: str,
        run_result: Optional[Dict[str, Any]] = None,
        topics: Optional[List[str]] = None,
        mastered: Optional[List[str]] = None,
        struggling: Optional[List[str]] = None,
    ) -> None:
        """Update the learner's memory after a completed turn.

        Uses only the `MemoryManager` methods sanctioned for Day 5:
        `update_from_run_result`, `append_interaction`, `record_topic`,
        `mark_mastered`, and `mark_struggling`.

        These `MemoryManager` mutation methods (`record_topic`,
        `mark_mastered`, `mark_struggling`, `append_interaction`,
        `update_from_run_result`) already persist internally, so no
        separate explicit save/persist step is needed here.

        Args:
            profile: The learner profile returned by `build_context`.
            student_message: The student's message this turn.
            tutor_response: The tutor's generated response this turn.
            run_result: Optional raw result from tool execution (e.g. sandbox
                run output/errors) to fold into the profile's error history.
            topics: Topic name(s) touched on this turn, to record.
            mastered: Concept name(s) the student has now demonstrated
                mastery of, if any were detected this turn.
            struggling: Concept name(s) the student appears to be
                struggling with, if any were detected this turn.

        Returns:
            None. The profile is updated (and persisted) via `MemoryManager`.
        """
        learner_name = getattr(profile, "learner_name", None)

        # Only folds tool-execution results into the profile's error
        # history when there actually was a tool run this turn (e.g. a
        # theory question with no code execution has no run_result).
        if run_result is not None:
            self.memory_manager.update_from_run_result(
                profile,
                error_type=run_result.get("error_type", ""),
                error_msg=run_result.get("error_message", ""),
                topic=run_result.get("topic", ""),
                success=run_result.get("success", False),
            )

        # Everything below must always run, regardless of whether a tool
        # was executed this turn, otherwise plain Q&A turns (no
        # run_result) would never be saved to memory at all.
        self.memory_manager.append_interaction(
            profile,
            "student",
            student_message,
        )

        self.memory_manager.append_interaction(
            profile,
            "tutor",
            tutor_response,
        )

        for topic in topics or []:
            self.memory_manager.record_topic(profile, topic)

        for concept in mastered or []:
            self.memory_manager.mark_mastered(profile, concept)

        for concept in struggling or []:
            self.memory_manager.mark_struggling(profile, concept)

        logger.info(
            "Updated learner profile for %s",
            learner_name or "?",
        )

    # ------------------------------------------------------------------
    # Full end-to-end turn
    # ------------------------------------------------------------------
    def run_turn(
        self,
        student_id: str,
        student_message: str,
        tool_results: Optional[Dict[str, Any]] = None,
        run_result: Optional[Dict[str, Any]] = None,
        topics: Optional[List[str]] = None,
        mastered: Optional[List[str]] = None,
        struggling: Optional[List[str]] = None,
    ) -> str:
        """Execute one complete Memory + RAG tutoring turn.

        This is the single call `week4_mini_tutor.run_tutor_agent()` needs
        to make to satisfy the full Day 5 flow diagram.

        Args:
            student_id: Identifier for the learner.
            student_message: The student's raw message this turn.
            tool_results: Results from tools already run earlier this turn
                (e.g. sandbox execution), passed through to the generator.
            run_result: Structured result to fold into error/mistake history.
            topics: Topics to record as studied this turn.
            mastered: Concepts to mark as mastered this turn.
            struggling: Concepts to mark as struggling this turn.

        Returns:
            The tutor's generated Socratic response text.
        """
        lock = self._get_lock(student_id)

        with lock:
            profile, prompt_context = self.build_context(
                student_id,
                student_message,
                tool_results=tool_results,
            )

            tutor_response = self.generate_response(prompt_context)

            self.update_memory(
                profile,
                student_message,
                tutor_response,
                run_result=run_result,
                topics=topics,
                mastered=mastered,
                struggling=struggling,
            )

        return tutor_response