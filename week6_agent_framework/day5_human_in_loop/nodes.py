import os
from openai import OpenAI

from week6_agent_framework.day2_langgraph.state import TutorState
from week6_agent_framework.day3_tutoring_graph.nodes import respond_node as generate_response_logic

def human_checkpoint_node(state: TutorState) -> dict[str, object]:
    """
    Acts as the Human Checkpoint.
    1. Generates the draft response (reusing Day 3's logic).
    2. Evaluates the draft against Socratic rules.
    3. Flags for human approval if rules are violated.
    """
    # Generate draft using Day 3 logic
    draft_state = generate_response_logic(state)
    response_text = draft_state.get("response", "")
    
    student_code = state.get("student_code", "")
    metadata = state.get("metadata", {}) or {}
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        metadata["requires_approval"] = False
        return {"response": response_text, "socratic_hint": draft_state.get("socratic_hint"), "metadata": metadata}
        
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    eval_prompt = f"""
Student Code:
{student_code}

Tutor Draft Response:
{response_text}

Does this response reveal the complete solution, contain full corrected code, provide excessive hints, or violate Socratic tutoring?
Answer YES if it reveals the solution or violates rules. Answer NO if it is a good Socratic hint.
"""
    try:
        eval_resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.0,
            max_tokens=10
        )
        answer = eval_resp.choices[0].message.content.strip().upper()
        requires_approval = "YES" in answer
    except Exception as e:
        requires_approval = False
        
    metadata["requires_approval"] = requires_approval
    metadata["checkpoint_reason"] = "Solution revealed or Socratic rules violated." if requires_approval else "Passed."
    
    return {
        "response": response_text,
        "socratic_hint": draft_state.get("socratic_hint"),
        "metadata": metadata
    }

def await_approval_node(state: TutorState) -> dict[str, object]:
    """
    Dummy node used strictly as a LangGraph interrupt point.
    Execution pauses before this node runs.
    """
    metadata = state.get("metadata", {}) or {}
    metadata["approved"] = True
    metadata["requires_approval"] = False
    return {"metadata": metadata}
