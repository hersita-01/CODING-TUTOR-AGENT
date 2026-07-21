# -----------------------------------
# WEEK 6 DAY 2 — RUN GRAPH
# week6-agent-frameworks/day2-langgraph-basics/run_graph.py
#
# LANGGRAPH CONCEPT: "invoke()"
# -----------------------------------
# Once a graph has been compiled, it behaves like a function.
# Calling graph.invoke(initial_state) executes all nodes,
# follows the edges, and returns the final TutorState.
# -----------------------------------

from graph_builder import build_graph


def main() -> None:
    graph = build_graph()

    print("Enter your Python code.")
    print("Press Enter twice to finish:\n")

    lines = []
    empty_count = 0

    while True:
        line = input()

        if line == "":
            empty_count += 1
            if empty_count == 2:
                break
        else:
            empty_count = 0
            lines.append(line)

    student_code = "\n".join(lines)
    if not student_code.strip():
        print("No code entered.")
        return

    valid_levels = {"beginner", "intermediate", "advanced"}

    while True:
        learner_level = input(
            "\nEnter level (beginner/intermediate/advanced): "
        ).strip().lower()

        if learner_level in valid_levels:
            break

        print("Invalid level. Please try again.")

    initial_state = {
        "student_id": "student_001",
        "student_code": student_code,
        "learner_level": learner_level,

        # Fields filled by nodes — left as neutral defaults here.
        # hint_level is NOT hardcoded: pedagogize_node derives it from
        # learner_level via _HINT_LEVEL_BY_LEARNER_LEVEL, so whatever you
        # type above ("beginner"/"intermediate"/"advanced") is what
        # actually drives detailed/guided/minimal — not this dict.
        "run_result": None,
        "execution_success": False,
        "error_type": None,
        "traceback": None,
        "hint_level": None,
        "learner_profile": {},
        "response": "",
    }

    final_state = graph.invoke(initial_state)

    print("\n===== FINAL STATE =====\n")

    for key, value in final_state.items():
        print(f"{key}:")
        print(value)
        print("-" * 50)


if __name__ == "__main__":
    main()