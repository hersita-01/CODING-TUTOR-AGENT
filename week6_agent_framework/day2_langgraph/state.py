# -----------------------------------
# WEEK 6 DAY 2 — SHARED STATE
# week6-agent-frameworks/day2-langgraph-basics/state.py
#
# LANGGRAPH CONCEPT: "State"
# ---------------------------------
# LangGraph builds a graph out of plain Python functions ("nodes").
# Every node receives the *same* state object, may return a dict of
# updates, and LangGraph merges those updates back into state before
# handing it to the next node.
#
# TutorState is a TypedDict — a regular dict at runtime, but type
# checkers (and LangGraph's StateGraph constructor) use the annotated
# fields to know what shape flows through the graph. Unlike a class,
# there is no custom __init__ or methods; it is purely a schema.
#
# Nothing here executes code or does I/O — it only DESCRIBES the data
# that nodes.py will read from and write to.
# -----------------------------------

from __future__ import annotations

from typing import Any, Literal, TypedDict


class TutorState(TypedDict):
    """Single shared state object passed between every node in the graph.

    Each node in nodes.py receives the current TutorState, does its work,
    and returns a (partial) dict of the fields it updated. LangGraph then
    merges that dict into the running state before invoking the next node.

    Fields
    ------
    student_id:
        Identifier used to load/save the learner's profile via
        Week 5's MemoryManager (e.g. "student_001").
    student_code:
        The raw Python source the student submitted this turn.
    learner_level:
        One of "beginner" / "intermediate" / "advanced". Drives the
        conditional branch in routes.route_by_level().
    execution_success:
        Set by diagnose_node — True if Week 2's safe_python_runner
        reported RunResult.ok == True.
    error_type:
        Set by diagnose_node — short exception class name (e.g.
        "IndexError"), or None on success.
    traceback:
        Set by diagnose_node — full traceback text from RunResult, or
        None on success.
    hint_level:
        Set by pedagogize_node — "detailed" / "guided" / "minimal",
        chosen from learner_level.
    response:
        Set by respond_node — the final Socratic-style reply shown to
        the student.
    learner_profile:
        Set by pedagogize_node — a plain dict snapshot of the learner's
        history, loaded via Week 5's MemoryManager.
    run_result:
        Set by diagnose_node — the raw RunResult dataclass instance
        from safe_python_runner, kept around in case a later node wants
        additional fields (line_number, execution_time, etc.) beyond
        the ones already unpacked into execution_success/error_type/
        traceback. Typed as Any because RunResult is a dataclass, not a
        TypedDict-friendly type.
    """

    student_id: str
    student_code: str
    learner_level: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ]
    execution_success: bool
    error_type: str | None
    traceback: str | None

    # Added for Day 3 Requirements
    diagnosis: str | None
    socratic_hint: str | None
    conversation_history: list[dict[str, str]]
    retrieved_context: str | None
    metadata: dict[str, Any]

    hint_level: Literal[
        "detailed",
        "guided",
        "minimal",
    ]
    response: str
    learner_profile: dict[str, Any]

    run_result: Any