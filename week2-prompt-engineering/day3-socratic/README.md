# Day 3: Socratic Tutor Variants

This folder compares several tutor behaviors:

- `friendly_tutor.py`: explains a Python concept simply and ends with a check question.
- `socratic_hint_generator.py`: gives a brief explanation plus one debugging question.
- `chain_of_thought_tutor.py`: gives a concise diagnosis without revealing hidden reasoning, then asks a Socratic question.
- `strict_socratic_mode.py`: asks only one question and does not explain or fix the code.
- `safe_python_runner.py`: runs pasted Python code in a temporary subprocess with a timeout.

Run a script, paste code when prompted, and press ENTER twice to finish input.
