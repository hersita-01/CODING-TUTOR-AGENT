# -----------------------------------
# WEEK 5 – MEMORY SUBSYSTEM
# week5-memory/ learner_profile.py
#
# Defines the LearnerProfile dataclass — the single canonical
# representation of a student's learning state.
#
# This module is intentionally self-contained:
#   ✗  No imports from week2, week3, or week4
#   ✗  No awareness of Groq, Streamlit, or the tutor loop
#   ✓  Plain Python: dataclasses, datetime, json, pathlib
#
# Future weeks that need memory (embeddings, RAG, multi-agent)
# will import MemoryManager, which in turn uses this class.
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("week5.learner_profile")


# ============================================================
# CONSTANTS
# ============================================================

# Supported error types — mirrors safe_python_runner classifications.
KNOWN_ERROR_TYPES: frozenset[str] = frozenset({
    "SyntaxError",
    "IndentationError",
    "NameError",
    "TypeError",
    "ValueError",
    "IndexError",
    "KeyError",
    "AttributeError",
    "ZeroDivisionError",
    "TimeoutError",
    "SecurityViolation",
})

# Rolling window sizes — keeps profiles from growing without bound.
MAX_RECENT_ERRORS  = 50
MAX_RECENT_TOPICS  = 30
MAX_SESSION_ITEMS  = 200


# ============================================================
# HELPERS
# ============================================================

def _utc_now() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _dedup_preserve_order(items: list[str]) -> list[str]:
    """Remove duplicates while preserving first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ============================================================
# LEARNER PROFILE
# ============================================================

@dataclass
class LearnerProfile:
    """Persistent representation of a single learner's state.

    All timestamps are UTC ISO-8601 strings so the JSON on disk is
    human-readable and timezone-unambiguous.

    Fields
    ------
    learner_name:
        Unique identifier for the learner (used as the filename stem).
    concepts_mastered:
        Topics the learner has demonstrated solid understanding of.
    concepts_struggling:
        Topics the learner is currently finding difficult.
    recent_errors:
        Rolling list of (error_type, message, topic) tuples recorded
        during code execution.  Capped at MAX_RECENT_ERRORS entries.
    recent_topics:
        Rolling list of Python topics covered in recent interactions.
        Capped at MAX_RECENT_TOPICS entries.
    session_history:
        Timestamped log of every interaction appended during a session.
        Capped at MAX_SESSION_ITEMS entries.
    learning_progress:
        Free-form dict for Week 5+ modules to store arbitrary numeric
        or boolean progress signals (e.g. streak counts, quiz scores).
    created_at:
        ISO-8601 UTC timestamp of profile creation.
    updated_at:
        ISO-8601 UTC timestamp of the most recent save.
    """

    learner_name:        str
    concepts_mastered:   list[str]             = field(default_factory=list)
    concepts_struggling: list[str]             = field(default_factory=list)
    recent_errors:       list[dict[str, str]]  = field(default_factory=list)
    recent_topics:       list[str]             = field(default_factory=list)
    session_history:     list[dict[str, Any]]  = field(default_factory=list)
    learning_progress:   dict[str, Any]        = field(default_factory=dict)
    created_at:          str                   = field(default_factory=_utc_now)
    updated_at:          str                   = field(default_factory=_utc_now)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise the profile to a JSON-compatible dictionary."""
        return {
            "learner_name":        self.learner_name,
            "concepts_mastered":   self.concepts_mastered,
            "concepts_struggling": self.concepts_struggling,
            "recent_errors":       self.recent_errors,
            "recent_topics":       self.recent_topics,
            "session_history":     self.session_history,
            "learning_progress":   self.learning_progress,
            "created_at":          self.created_at,
            "updated_at":          self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnerProfile":
        """Deserialise a profile from a dictionary (e.g. loaded from JSON).

        Unknown keys are silently ignored so old profiles are forward-
        compatible as new fields are added in later weeks.
        """
        return cls(
            learner_name        = data.get("learner_name", "unknown"),
            concepts_mastered   = data.get("concepts_mastered", []),
            concepts_struggling = data.get("concepts_struggling", []),
            recent_errors       = data.get("recent_errors", []),
            recent_topics       = data.get("recent_topics", []),
            session_history     = data.get("session_history", []),
            learning_progress   = data.get("learning_progress", {}),
            created_at          = data.get("created_at", _utc_now()),
            updated_at          = data.get("updated_at", _utc_now()),
        )

    # ------------------------------------------------------------------
    # Mutation methods
    # Each method updates `updated_at` so the timestamp is always fresh.
    # ------------------------------------------------------------------

    def add_error(
        self,
        error_type:    str,
        error_message: str,
        topic:         str = "",
    ) -> None:
        """Record a runtime or syntax error encountered during execution.

        Parameters
        ----------
        error_type:
            The Python exception class name (e.g. "ValueError").
            If not in KNOWN_ERROR_TYPES it is stored as-is with a warning.
        error_message:
            The raw exception message string.
        topic:
            Optional topic label associated with this error.
        """
        if error_type not in KNOWN_ERROR_TYPES:
            log.warning("Unrecognised error type '%s' — storing anyway.", error_type)

        entry: dict[str, str] = {
            "error_type":    error_type,
            "error_message": error_message[:300],   # guard against huge tracebacks
            "topic":         topic,
            "recorded_at":   _utc_now(),
        }
        self.recent_errors.append(entry)

        # Trim to rolling window — keep the most recent entries.
        if len(self.recent_errors) > MAX_RECENT_ERRORS:
            self.recent_errors = self.recent_errors[-MAX_RECENT_ERRORS:]

        # Errors imply the concept is being struggled with.
        if topic:
            self.mark_struggling(topic)

        self.updated_at = _utc_now()

    def add_topic(self, topic: str) -> None:
        """Record that a topic was covered in this session.

        Duplicates are moved to the end (most-recent semantics) rather
        than silently dropped, so `recent_topics[-1]` is always the
        latest topic.

        Parameters
        ----------
        topic:
            Short label for the Python concept covered (e.g. "loops").
        """
        topic = topic.strip()
        if not topic:
            return

        # Remove existing occurrence so re-adding pushes it to the end.
        self.recent_topics = [t for t in self.recent_topics if t != topic]
        self.recent_topics.append(topic)

        if len(self.recent_topics) > MAX_RECENT_TOPICS:
            self.recent_topics = self.recent_topics[-MAX_RECENT_TOPICS:]

        self.updated_at = _utc_now()

    def mark_mastered(self, concept: str) -> None:
        """Record that the learner has mastered a concept.

        Automatically removes the concept from `concepts_struggling`
        if it was listed there, since mastery supersedes struggle.

        Parameters
        ----------
        concept:
            Short label for the concept (e.g. "for loops").
        """
        concept = concept.strip()
        if not concept:
            return

        # Promote: remove from struggling, add to mastered (no duplicates).
        self.concepts_struggling = [c for c in self.concepts_struggling if c != concept]

        if concept not in self.concepts_mastered:
            self.concepts_mastered.append(concept)

        self.updated_at = _utc_now()

    def mark_struggling(self, concept: str) -> None:
        """Record that the learner is struggling with a concept.

        Will not demote a concept that has already been mastered —
        once mastered, a concept stays mastered unless explicitly removed.

        Parameters
        ----------
        concept:
            Short label for the concept.
        """
        concept = concept.strip()
        if not concept:
            return

        # Do not overwrite mastery.
        if concept in self.concepts_mastered:
            return

        if concept not in self.concepts_struggling:
            self.concepts_struggling.append(concept)

        self.updated_at = _utc_now()

    def append_interaction(
        self,
        role:    str,
        content: str,
        topic:   str = "",
    ) -> None:
        """Log a single interaction turn to the session history.

        Parameters
        ----------
        role:
            "student" or "tutor".
        content:
            The message content (truncated to 500 chars to keep JSON small).
        topic:
            Optional topic label for this turn.
        """
        entry: dict[str, Any] = {
            "role":       role,
            "content":    content[:500],
            "topic":      topic,
            "timestamp":  _utc_now(),
        }
        self.session_history.append(entry)

        if len(self.session_history) > MAX_SESSION_ITEMS:
            self.session_history = self.session_history[-MAX_SESSION_ITEMS:]

        self.updated_at = _utc_now()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self) -> str:
        """Return a human-readable summary of the learner's current state.

        Suitable for logging, debugging, or injecting into a tutor
        system prompt in a later week.
        """
        mastered   = ", ".join(self.concepts_mastered)   or "none yet"
        struggling = ", ".join(self.concepts_struggling) or "none identified"
        topics     = ", ".join(self.recent_topics[-5:])  or "none recorded"

        # Count error frequency
        error_counts: dict[str, int] = {}
        for e in self.recent_errors:
            et = e.get("error_type", "Unknown")
            error_counts[et] = error_counts.get(et, 0) + 1

        if error_counts:
            error_summary = ", ".join(
                f"{et} ×{n}" for et, n in
                sorted(error_counts.items(), key=lambda x: -x[1])
            )
        else:
            error_summary = "none recorded"

        lines = [
            f"Learner:           {self.learner_name}",
            f"Profile created:   {self.created_at}",
            f"Last updated:      {self.updated_at}",
            f"Mastered:          {mastered}",
            f"Struggling with:   {struggling}",
            f"Recent topics:     {topics}",
            f"Error history:     {error_summary}",
            f"Session turns:     {len(self.session_history)}",
        ]
        return "\n".join(lines)