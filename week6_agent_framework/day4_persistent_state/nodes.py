import os
import sys
from pathlib import Path

from week6_agent_framework.day2_langgraph.state import TutorState
from week6_agent_framework.day3_tutoring_graph.nodes import diagnose_node, pedagogize_node, respond_node

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(_PROJECT_ROOT / "week5_memory" / "day1-learner-memory"))

try:
    from memory_manager import MemoryManager
    _memory_manager = MemoryManager()
    _WEEK5_AVAILABLE = True
except ImportError:
    _memory_manager = None
    _WEEK5_AVAILABLE = False


def load_session_node(state: TutorState) -> dict[str, object]:
    """Load conversation history and profile from disk at the start of the session."""
    student_id = state.get("student_id", "unknown")
    
    if not _WEEK5_AVAILABLE or not _memory_manager:
        return {"conversation_history": [], "learner_profile": {}}

    profile = _memory_manager.get_or_create(student_id)
    
    # Reloading state from disk
    return {
        "learner_profile": profile.to_dict(),
        "conversation_history": profile.session_history
    }


def save_session_node(state: TutorState) -> dict[str, object]:
    """Save the interaction to disk before ending the graph."""
    student_id = state.get("student_id", "unknown")
    
    if not _WEEK5_AVAILABLE or not _memory_manager:
        return {}

    profile = _memory_manager.get_or_create(student_id)
    
    # Save the student's submission and the tutor's generated response
    student_code = state.get("student_code")
    if student_code:
        profile.append_interaction("student", student_code, topic="submission")
        
    response = state.get("response")
    if response:
        profile.append_interaction("tutor", response, topic="socratic_hint")
        
    # The MemoryManager handles updating timestamps and writing to disk
    _memory_manager.save_profile(profile)
    
    return {}
