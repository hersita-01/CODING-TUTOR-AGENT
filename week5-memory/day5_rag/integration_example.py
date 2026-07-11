"""
integration_examples.py

Week 5 / Day 5 - Memory + RAG Integration
------------------------------------------
Runnable, self-contained examples showing how `MemoryRAGPipeline` is used,
both standalone and as it is wired into `week4_mini_tutor.run_tutor_agent()`.

Run directly with:
    python integration_examples.py
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from memory_rag_pipeline import MemoryRAGPipeline, TutorPromptContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fake_socratic_generator(context_block: str, prompt_context: TutorPromptContext) -> str:
    """A stand-in for the real Week 3/4 LLM-calling tutor agent.

    In production this is replaced by a thin wrapper around
    `tutor_agent.py` / `week4_mini_tutor.py`'s existing LLM call, which
    receives `context_block` as an additional system-prompt section.

    Args:
        context_block: Combined learning + RAG context, ready for injection.
        prompt_context: The full `TutorPromptContext` for this turn.

    Returns:
        A fake Socratic-style response for demonstration purposes.
    """
    logger.info("---- Prompt context sent to LLM ----\n%s\n-------------------------------------", context_block)
    return (
        f"Before I give you the answer -- looking at your code, what do you "
        f"think happens the first time the loop variable reaches the last "
        f"index? Walk me through it."
    )


def example_single_turn() -> None:
    """Demonstrate a single end-to-end tutoring turn."""
    pipeline = MemoryRAGPipeline(response_generator=fake_socratic_generator)

    student_id = "student_demo_01"
    student_message = "Why does my for loop skip the last item in the list?"

    # Step: "run existing tools" would happen here in the real agent
    # (e.g. sandbox execution of the student's code). We simulate a result:
    tool_results: Dict[str, Any] = {
        "executed": True,
        "stdout": "[1, 2, 3]\n",
        "stderr": "",
    }
    run_result: Dict[str, Any] = {
        "concept": "for-loops",
        "error": "off-by-one / range boundary misunderstanding",
        "success": False,
    }

    response = pipeline.run_turn(
        student_id=student_id,
        student_message=student_message,
        tool_results=tool_results,
        run_result=run_result,
        topics=["loops", "iteration"],
        struggling=["range() boundaries"],
    )

    print("\n=== Tutor response ===")
    print(response)


def example_repeated_mistake() -> None:
    """Demonstrate how a second occurrence of the same mistake is surfaced.

    Calling `run_turn` twice with the same struggling concept simulates a
    student repeating a mistake across sessions; `build_learning_context`
    will surface it in the "Struggling Concepts" section with an
    incremented flag count (assuming `MemoryManager.mark_struggling`
    increments existing counts -- see README for the assumed contract).
    """
    pipeline = MemoryRAGPipeline(response_generator=fake_socratic_generator)
    student_id = "student_demo_02"

    for attempt in range(2):
        print(f"\n--- Attempt {attempt + 1} ---")
        pipeline.run_turn(
            student_id=student_id,
            student_message="My off-by-one error is back again in the loop.",
            run_result={"concept": "for-loops", "error": "off-by-one", "success": False},
            struggling=["off-by-one errors"],
        )


if __name__ == "__main__":
    example_single_turn()
    example_repeated_mistake()