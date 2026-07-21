# -----------------------------------
# WEEK 6 DAY 2 — GRAPH BUILDER
# week6-agent-frameworks/day2-langgraph-basics/graph_builder.py
#
# LANGGRAPH CONCEPT: "StateGraph", "add_node", "add_edge",
#                     "add_conditional_edges", "compile"
# ---------------------------------
# StateGraph(TutorState) is the graph itself, parameterised by the
# TypedDict schema that flows through every node (see state.py).
#
# The overall shape we're building:
#
#         START
#           |
#      diagnose_node
#           |
#      pedagogize_node
#           |
#     (conditional edge via route_by_level)
#       /    |    \
#  beginner inter. advanced   <- labels returned by route_by_level()
#       \    |    /
#      respond_node
#           |
#          END
#
# START and END are special sentinel nodes LangGraph provides — every
# graph must eventually reach END or it will run forever waiting for a
# next step.
# -----------------------------------

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from state import TutorState
from nodes import diagnose_node, pedagogize_node, respond_node
from routes import route_by_level


def build_graph():
    """Assemble and compile the Mini-Tutor LangGraph graph.

    Returns
    -------
    A compiled LangGraph graph object with an .invoke(state) method,
    exactly like the ones used throughout the rest of this lesson.
    """
    # 1. Create the graph, telling LangGraph the shape of state that
    #    will be passed between every node (TutorState from state.py).
    graph = StateGraph(TutorState)

    # 2. Register each node function under a name. The name is what
    #    add_edge() / add_conditional_edges() below refer to — it does
    #    not have to match the Python function name, though here it does
    #    for clarity.
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("pedagogize", pedagogize_node)
    graph.add_node("respond", respond_node)

    # 3. Plain edges: START always flows into diagnose, and diagnose
    #    always flows into pedagogize. No branching happens here.
    graph.add_edge(START, "diagnose")
    graph.add_edge("diagnose", "pedagogize")

    # 4. Conditional edge: after pedagogize_node runs, LangGraph calls
    #    route_by_level(state) and looks up the returned string in the
    #    path_map below to decide which node to go to next.
    #
    #    All three branches currently point at the same "respond" node —
    #    the point of this step is to demonstrate the BRANCHING
    #    mechanism itself, which is exactly what the Week 6 Day 2 brief
    #    asks for ("even if all branches currently point to the same
    #    response node"). Swapping any one of these three values for a
    #    different node name is all a future lesson would need to do to
    #    make the branches diverge in practice.
    graph.add_conditional_edges(
        "pedagogize",
        route_by_level,
        {
            "beginner":     "respond",
            "intermediate": "respond",
            "advanced":     "respond",
        },
    )

    # 5. respond_node is the last real step; wire it to END.
    graph.add_edge("respond", END)

    # 6. compile() validates the graph (no dangling nodes, no missing
    #    edges) and returns an executable object.
    return graph.compile()