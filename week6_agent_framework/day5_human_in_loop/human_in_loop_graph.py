from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from week6_agent_framework.day2_langgraph.state import TutorState
from week6_agent_framework.day3_tutoring_graph.nodes import diagnose_node, pedagogize_node
from week6_agent_framework.day4_persistent_state.nodes import load_session_node, save_session_node
from .nodes import human_checkpoint_node, await_approval_node

def route_checkpoint(state: TutorState) -> str:
    """Routes to the approval node if flagged, otherwise straight to respond."""
    metadata = state.get("metadata", {}) or {}
    if metadata.get("requires_approval", False):
        return "await_approval"
    return "respond"

def build_human_in_loop_graph():
    """
    Assemble the Day 5 graph matching the strict core flow:
    START -> Diagnose -> Pedagogize -> Human Checkpoint -> Respond -> END
    
    (Note: load_session is wrapped around START and save_session acts as Respond
     to satisfy Day 4 persistence requirements without breaking the 5-node core architecture).
    """
    graph = StateGraph(TutorState)

    # We map "load_session" as the first step to satisfy Day 4 persistence
    graph.add_node("load_session", load_session_node)
    
    # Core nodes
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("pedagogize", pedagogize_node)
    graph.add_node("human_checkpoint", human_checkpoint_node)
    
    # We use save_session_node as the "Respond" step because in a backend system,
    # responding means committing the final output to the database/memory.
    graph.add_node("respond", save_session_node)
    
    # Dummy node for LangGraph's interrupt_before
    graph.add_node("await_approval", await_approval_node)

    # Edges
    graph.add_edge(START, "load_session")
    graph.add_edge("load_session", "diagnose")
    graph.add_edge("diagnose", "pedagogize")
    graph.add_edge("pedagogize", "human_checkpoint")

    # Conditional Routing for Checkpoint
    graph.add_conditional_edges(
        "human_checkpoint",
        route_checkpoint,
        {
            "await_approval": "await_approval",
            "respond": "respond"
        }
    )

    # Resume flow after human approval
    graph.add_edge("await_approval", "respond")
    graph.add_edge("respond", END)

    # MemorySaver satisfies LangGraph's requirement for a Checkpointer 
    # to support interrupt_before across the execution thread.
    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["await_approval"]
    )
