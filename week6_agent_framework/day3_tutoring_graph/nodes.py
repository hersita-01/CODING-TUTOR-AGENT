import os
import sys
from pathlib import Path
from openai import OpenAI

from week6_agent_framework.day2_langgraph.state import TutorState

# Wire imports from previous weeks
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

sys.path.append(str(_PROJECT_ROOT / "week2_prompt_engineering" / "day3-socratic"))
sys.path.append(str(_PROJECT_ROOT / "week4_mini_tutor"))
sys.path.append(str(_PROJECT_ROOT / "week5_memory" / "day1-learner-memory"))
sys.path.append(str(_PROJECT_ROOT / "week5_memory" / "day5_rag"))

# Week 2 Sandbox
try:
    from safe_python_runner import run_python_safely as safe_run
    _WEEK2_AVAILABLE = True
except ImportError:
    _WEEK2_AVAILABLE = False

# Week 5 Memory
try:
    from memory_manager import MemoryManager
    _WEEK5_AVAILABLE = True
except ImportError:
    _WEEK5_AVAILABLE = False

_memory_manager = MemoryManager() if _WEEK5_AVAILABLE else None

# Week 5 RAG
try:
    from rag_context_builder import build_rag_context
    _RAG_AVAILABLE = True
except ImportError:
    _RAG_AVAILABLE = False

# Configuration
TIMEOUT_SECONDS = 5


def diagnose_node(state: TutorState) -> dict[str, object]:
    """Execute code and generate a diagnosis."""
    student_code = state.get("student_code", "")

    if not _WEEK2_AVAILABLE:
        return {
            "execution_success": False,
            "error_type": "SandboxUnavailable",
            "traceback": "Week 2 module missing.",
            "diagnosis": "Unable to run code because the sandbox is missing."
        }

    result = safe_run(student_code, timeout_s=TIMEOUT_SECONDS)
    diagnosis = "Code executed successfully." if result.ok else f"Execution failed with a {result.error_type}."

    return {
        "run_result": result,
        "execution_success": result.ok,
        "error_type": result.error_type or None,
        "traceback": result.traceback or None,
        "diagnosis": diagnosis,
    }


def pedagogize_node(state: TutorState) -> dict[str, object]:
    """Load learner profile and determine hint level and context."""
    student_id = state.get("student_id", "unknown")
    learner_level = state.get("learner_level", "intermediate")
    
    hint_map = {"beginner": "detailed", "intermediate": "guided", "advanced": "minimal"}
    hint_level = hint_map.get(learner_level, "guided")

    if _WEEK5_AVAILABLE and _memory_manager:
        profile = _memory_manager.get_or_create(student_id)
        run_result = state.get("run_result")
        
        if run_result:
            _memory_manager.update_from_run_result(
                profile,
                error_type=run_result.error_type,
                error_msg=run_result.error_message,
                topic="",
                success=run_result.ok,
            )
        learner_profile = profile.to_dict()
    else:
        learner_profile = {"learner_name": student_id, "note": "Memory unavailable."}

    if _RAG_AVAILABLE:
        search_query = state.get("traceback") or state.get("student_code", "")
        retrieved_context = build_rag_context(search_query, top_k=3)
    else:
        retrieved_context = "RAG unavailable."

    return {
        "hint_level": hint_level,
        "learner_profile": learner_profile,
        "retrieved_context": retrieved_context,
    }


def respond_node(state: TutorState) -> dict[str, object]:
    """Generate Socratic response using LLM."""
    diagnosis = state.get("diagnosis", "")
    student_code = state.get("student_code", "")
    traceback_text = state.get("traceback", "")
    error_type = state.get("error_type", "")
    hint_level = state.get("hint_level", "guided")
    retrieved_context = state.get("retrieved_context", "")
    execution_success = state.get("execution_success", False)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "response": f"Diagnosis: {diagnosis}\n(No API key found, unable to generate Socratic hint.)",
            "socratic_hint": None
        }

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    system_prompt = (
        "You are a patient Python tutor for beginners. Explain errors in plain English, "
        "avoid jargon, and never give the full corrected code first.\n"
        "You are a Socratic Python tutor. Your job is to ask a question that nudges "
        "the learner toward the bug without revealing the fix.\n"
        "Ask exactly ONE guiding Socratic question."
    )

    user_prompt = f"Student Code:\n{student_code}\n\n"
    if not execution_success:
        user_prompt += f"Error:\n{error_type}\nTraceback:\n{traceback_text}\n\n"
    else:
        user_prompt += "The code executed successfully, but the student may have logic issues.\n\n"
        
    user_prompt += f"Diagnosis: {diagnosis}\n"
    user_prompt += f"Hint Level required: {hint_level}\n\n"
    user_prompt += f"Context:\n{retrieved_context}\n\n"
    user_prompt += "Explain briefly and ask one Socratic debugging question."

    try:
        llm_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=256
        )
        response_text = llm_response.choices[0].message.content or "No response generated."
    except Exception as e:
        response_text = f"Diagnosis: {diagnosis}\nSystem Error: LLM call failed ({e})."

    return {
        "response": response_text,
        "socratic_hint": response_text
    }
