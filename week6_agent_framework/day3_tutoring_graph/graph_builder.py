import os
from pathlib import Path
from typing import Any

from langgraph.graph import StateGraph, START, END

# Import the shared state and routing from Day 2
from week6_agent_framework.day2_langgraph.state import TutorState
from week6_agent_framework.day2_langgraph.routes import route_by_level

# Import our new functional Day 3 nodes
from .nodes import diagnose_node, pedagogize_node, respond_node

def build_tutoring_graph():
    """Assemble the complete 3-node tutoring graph for Day 3."""
    graph = StateGraph(TutorState)

    graph.add_node("diagnose", diagnose_node)
    graph.add_node("pedagogize", pedagogize_node)
    graph.add_node("respond", respond_node)

    graph.add_edge(START, "diagnose")
    graph.add_edge("diagnose", "pedagogize")

    graph.add_conditional_edges(
        "pedagogize",
        route_by_level,
        {
            "beginner": "respond",
            "intermediate": "respond",
            "advanced": "respond",
        },
    )

    graph.add_edge("respond", END)

    return graph.compile()
