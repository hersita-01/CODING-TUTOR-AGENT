from langgraph.graph import StateGraph, START, END

from week6_agent_framework.day2_langgraph.state import TutorState
from week6_agent_framework.day2_langgraph.routes import route_by_level
from week6_agent_framework.day3_tutoring_graph.nodes import diagnose_node, pedagogize_node, respond_node
from .nodes import load_session_node, save_session_node

def build_persistent_graph():
    """Assemble the 5-node graph for Day 4 with disk persistence."""
    graph = StateGraph(TutorState)

    graph.add_node("load_session", load_session_node)
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("pedagogize", pedagogize_node)
    graph.add_node("respond", respond_node)
    graph.add_node("save_session", save_session_node)

    # 1. Start by loading from disk
    graph.add_edge(START, "load_session")
    graph.add_edge("load_session", "diagnose")
    
    # 2. Main logic
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

    # 3. Save to disk before exiting
    graph.add_edge("respond", "save_session")
    graph.add_edge("save_session", END)

    return graph.compile()
