# -----------------------------------
# WEEK 6 DAY 2 — NODES
# week6-agent-frameworks/day2-langgraph-basics/nodes.py
#
# LANGGRAPH CONCEPT: "Nodes"
# ---------------------------------
# A node is just a Python function: (state) -> partial_state_update.
# LangGraph calls each node in turn, passing the full TutorState dict,
# and merges whatever dict the node returns back into that state.
# Nodes should be side-effect-light with respect to the graph itself —
# all the "real" side effects here (running code, hitting disk) are
# delegated to the Week 2 / Week 5 modules we import below, exactly as
# they already exist. Nothing in those modules is modified.
#
# This file wires THREE nodes:
#   diagnose_node    — runs student code through the Week 2 sandbox
#   pedagogize_node  — loads learner history (Week 5) and picks a hint level
#   respond_node      —  generates a Socratic response from TutorState
# -----------------------------------

from __future__ import annotations

import sys
from pathlib import Path

from week6_agent_framework.day2_langgraph.state import TutorState

# ============================================================
# WIRE UP IMPORTS FROM EXISTING WEEKS
#
# We do NOT copy or rewrite any Week 2 / Week 4 / Week 5 code. Instead,
# following the same "graceful degradation" pattern used in earlier weeks,
# we add each week's real folder to sys.path and import the real modules.
# If a module is missing, the node falls back instead of crashing.
# ============================================================

_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../ (repo root)
# TODO (Week 6+):
# Replace sys.path manipulation with proper Python packages
# and absolute imports.
sys.path.append(str(_PROJECT_ROOT / "week2-prompt-engineering" / "day3-socratic"))
sys.path.append(str(_PROJECT_ROOT / "week4_mini_tutor"))
sys.path.append(str(_PROJECT_ROOT / "week5-memory" / "day1-memory-manager"))

# ── Week 2: safe execution sandbox ──────────────────────────────────────────
try:
    # The real public entry point is run_python_safely(); we alias it to
    # safe_run() here purely for a short, readable name inside this file.
    from safe_python_runner import run_python_safely as safe_run
    _WEEK2_AVAILABLE = True
except ImportError:
    _WEEK2_AVAILABLE = False

# ── Week 4: configuration values ────────────────────────────────────────────
try:
    from config import TIMEOUT_SECONDS
except ImportError:
    TIMEOUT_SECONDS = 5  # fallback default, mirrors config.py's own default

# ── Week 5: persistent learner profiles ─────────────────────────────────────
try:
    from memory_manager import MemoryManager
    _WEEK5_AVAILABLE = True
except ImportError:
    # Most likely cause: learner_profile.py (LearnerProfile, _utc_now) was
    # not included in this bundle. We do not reconstruct or guess at that
    # file's contents — we simply fall back to an in-memory stub so the
    # graph still runs end-to-end for this LangGraph lesson.
    _WEEK5_AVAILABLE = False

# A single shared MemoryManager instance for this process, mirroring how a
# real app would construct one manager and reuse it across requests.
_memory_manager = (
    MemoryManager() if _WEEK5_AVAILABLE else None
)


# ============================================================
# NODE 1 — diagnose_node
# ============================================================

def diagnose_node(state: TutorState) -> dict[str, object]:
    """Execute the student's code through Week 2's safe sandbox.

    LANGGRAPH CONCEPT: a node reads whatever fields it needs from the
    incoming `state` dict (here: student_code) and returns ONLY the
    fields it wants to update (execution_success, error_type,
    traceback, run_result). LangGraph merges this partial dict into the
    full state — diagnose_node never has to know about, or touch,
    fields like learner_level or hint_level that belong to other nodes.
    """
    student_code = state["student_code"]

    if not _WEEK2_AVAILABLE:
        # Fallback so the graph is still runnable for teaching purposes
        # even if safe_python_runner.py isn't on the path.
        return {
            "run_result": None,
            "execution_success": False,
            "error_type": "SandboxUnavailable",
            "traceback": "Week 2 safe_python_runner module could not be imported.",
        }

    # Reuse Week 2's sandbox exactly as-is: AST security check, syntax
    # check, subprocess isolation, memory cap, and structured traceback
    # parsing all happen inside safe_run() (a.k.a. run_python_safely()).
    result = safe_run(student_code, timeout_s=TIMEOUT_SECONDS)

    return {
        "run_result": result,
        "execution_success": result.ok,
        # error_type / traceback are empty strings on success in RunResult;
        # normalise those to None so downstream checks can use `is None`.
        "error_type": result.error_type or None,
        "traceback": result.traceback or None,
    }


# ============================================================
# NODE 2 — pedagogize_node
# ============================================================

# Maps a student's self-reported (or profile-inferred) level to how much
# scaffolding the tutor should provide in its next reply.
_HINT_LEVEL_BY_LEARNER_LEVEL: dict[str, str] = {
    "beginner": "detailed",
    "intermediate": "guided",
    "advanced": "minimal",
}


def pedagogize_node(state: TutorState) -> dict[str, object]:
    """Load learner history (Week 5) and decide how much scaffolding to give.

    LANGGRAPH CONCEPT: nodes can call out to arbitrary Python — including
    stateful classes like MemoryManager — as long as they still return a
    plain dict of state updates. The MemoryManager object itself is NOT
    part of TutorState; only the plain-dict *snapshot* it produces
    (learner_profile) is put into state, keeping TutorState serializable.
    """
    student_id = state["student_id"]
    learner_level = state["learner_level"]

    hint_level = _HINT_LEVEL_BY_LEARNER_LEVEL.get(learner_level, "guided")

    if _WEEK5_AVAILABLE and _memory_manager is not None:
        # get_or_create() is idempotent (Week 5 design principle): calling
        # it repeatedly for the same student_id never overwrites history.
        profile = _memory_manager.get_or_create(student_id)

        # Record this attempt so future turns see accumulated history —
        # reusing Week 5's update_from_run_result() integration point,
        # which was written specifically to accept a RunResult-shaped
        # (error_type, error_message, success) triple.
        run_result = state.get("run_result")
        if run_result is not None:
            _memory_manager.update_from_run_result(
                profile,
                error_type=run_result.error_type,
                error_msg=run_result.error_message,
                topic="",
                success=run_result.ok,
            )

        learner_profile = profile.to_dict()
    else:
        # Fallback stub — keeps TutorState's "learner_profile: dict"
        # contract satisfied even without Week 5's storage layer.
        learner_profile = {
            "learner_name": student_id,
            "note": "Week 5 MemoryManager unavailable — no history loaded.",
        }

    return {
        "hint_level": hint_level,
        "learner_profile": learner_profile,
    }


# ============================================================
# NODE 3 — respond_node
# ============================================================

def respond_node(state: TutorState) -> dict[str, object]:
    """Build a Socratic-style reply from the current TutorState.

    LANGGRAPH CONCEPT: this is the terminal node before END. In a full
    application, this node could pass the TutorState to an LLM to generate
    a personalized response. For this LangGraph lesson, we keep the node
    offline and deterministic by constructing the reply with simple rules
    based on hint_level and execution results.
    """

    hint_level = state["hint_level"]
    execution_success = state["execution_success"]
    error_type = state["error_type"]
    traceback_text = state["traceback"]

    if execution_success:
        response = (
            "Diagnosis: Your code ran without errors.\n"
            "Question: What output did you expect to see, and does it match "
            "what actually printed?\n"
            "Next Step: Try a slightly different input and predict the output "
            "before running it."
        )
    else:
        # Pull the last traceback line for a beginner-friendly line reference,
        # without ever handing over the corrected code (Week 4 tutor rule #3).
        last_line = (traceback_text or "").strip().splitlines()[-1] if traceback_text else ""

        if hint_level == "detailed":
            question = (
                f"Diagnosis: Your code raised a {error_type}. "
                f"Looking at the last line of the traceback ({last_line!r}), "
                "what value do you think the program was working with right "
                "before it failed?\n"
                "Question: Can you print() that value just before the failing "
                "line to see what it actually is?\n"
                "Next Step: Add one print() statement above the failing line "
                "and re-run."
            )
        elif hint_level == "guided":
            question = (
                f"Diagnosis: A {error_type} occurred during execution.\n"
                "Question: Which line do you think is responsible, and what "
                "assumption does that line make about its input?\n"
                "Next Step: Re-read that line and check whether the assumption "
                "always holds."
            )
        else:  # "minimal"
            question = (
                f"Diagnosis: {error_type} raised.\n"
                "Question: What invariant does this error type usually signal "
                "is being violated?\n"
                "Next Step: Isolate the failing expression and test it alone."
            )

        response = question

    return {"response": response}