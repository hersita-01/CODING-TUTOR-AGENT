# -----------------------------------
# WEEK 6 DAY 2 — DEMO
# week6-agent-frameworks/day2-langgraph-basics/demo.py
#
# LANGGRAPH CONCEPT: "invoke"
# ---------------------------------
# graph.invoke(initial_state) runs the compiled graph start-to-finish:
# START -> diagnose -> pedagogize -> (conditional) -> respond -> END,
# and returns the FINAL merged state — every field any node wrote
# along the way, all in one dict.
#
# This script builds one deliberately-buggy student submission (an
# IndexError from indexing past the end of a 3-item list), runs it
# through the graph, and prints the fields a real tutor UI would show.
# -----------------------------------

from __future__ import annotations

from graph_builder import build_graph


def main() -> None:
    # Only the fields the student/UI actually supplies at turn-start.
    # The rest of TutorState's fields are written by nodes as the graph
    # runs — LangGraph doesn't require every TypedDict key to be present
    # up front, only that nodes don't try to *read* a key before some
    # earlier node has written it.
    initial_state = {
        "student_id": "student_001",
        "student_code": "numbers=[1,2,3]\nprint(numbers[10])",
        "learner_level": "beginner",
    }

    graph = build_graph()

    # This single call walks the entire graph we wired up in
    # graph_builder.py and returns the final TutorState.
    final_state = graph.invoke(initial_state)

    print("=" * 50)
    print("MINI-TUTOR — LANGGRAPH DEMO RUN")
    print("=" * 50)

    print(f"\nStudent code:\n{initial_state['student_code']}")

    print("\n--- diagnose_node output ---")
    status = "SUCCESS" if final_state["execution_success"] else "FAILED"
    print(f"Execution status : {status}")
    print(f"Error type       : {final_state['error_type']}")

    print("\n--- pedagogize_node output ---")
    print(f"Hint level       : {final_state['hint_level']}")
    print(f"Learner profile  : {final_state['learner_profile']}")

    print("\n--- respond_node output ---")
    print(final_state["response"])


if __name__ == "__main__":
    main()