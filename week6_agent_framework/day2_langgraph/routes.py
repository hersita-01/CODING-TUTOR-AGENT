# -----------------------------------
# WEEK 6 DAY 2 — CONDITIONAL ROUTING
# week6-agent-frameworks/day2-langgraph-basics/routes.py
#
# LANGGRAPH CONCEPT: "Conditional edges"
# ---------------------------------
# A normal edge (graph.add_edge("a", "b")) always goes from node "a" to
# node "b". A CONDITIONAL edge instead goes from a node to a ROUTING
# FUNCTION. That function inspects the current state and returns a
# label (a string). graph_builder.py then maps each possible label to
# the actual node it should lead to.
#
# This lets the same graph structure support different learner levels
# taking different paths in the future (e.g. "advanced" students could
# skip straight to a terser response node, or "beginner" students could
# be routed through an extra hint-expansion node) without changing how
# pedagogize_node or diagnose_node work at all.
#
# Today all three labels happen to map to the same respond_node — the
# BRANCHING mechanism is what we're demonstrating, not divergent
# behaviour (that's a natural "next day" extension).
# -----------------------------------

from __future__ import annotations

from state import TutorState


def route_by_level(state: TutorState) -> str:
    """Return a routing label based on state["learner_level"].

    LangGraph calls this function with the full TutorState after
    pedagogize_node has run. The string it returns is looked up in the
    path_map dict passed to graph.add_conditional_edges() in
    graph_builder.py to decide which node runs next.

    Returns
    -------
    "beginner", "intermediate", or "advanced".
    Unrecognised or missing levels default to "intermediate" so the
    graph never dead-ends on unexpected input.
    """
    learner_level = state.get("learner_level", "intermediate")

    if learner_level not in ("beginner", "intermediate", "advanced"):
        return "intermediate"

    return learner_level