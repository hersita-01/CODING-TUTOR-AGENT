# Week 2 — Prompt Engineering

Week 2 focuses on improving the AI tutor's behavior using prompt engineering techniques.

The tutor evolves from:
- simple AI responses

to:
- guided tutoring
- Socratic questioning
- structured explanations
- controlled AI behavior

---

# Goals

- Build beginner-friendly AI tutor prompts
- Improve debugging explanations
- Learn few-shot prompting
- Design Socratic tutoring systems
- Create structured AI outputs
- Understand streaming and token usage

---

# Concepts Learned

- Prompt engineering
- System prompts
- User prompts
- Few-shot prompting
- Socratic questioning
- Structured outputs
- Streaming responses
- Runtime error analysis
- Tutor personality design

---

# Week 2 File Structure

```text
week2-prompt-engineering/
│
├── prompt_library.md
│
├── day1-bug-explainer/
│   ├── bug_explainer.py
│   └── notes.md
│
├── day2-few-shot/
│   ├── few_shot_bug_explainer.py
│   └── notes.md
│
├── day3-socratic/
│   ├── friendly_tutor.py
│   ├── chain_of_thought_tutor.py
│   ├── strict_socratic_mode.py
│   ├── safe_python_runner.py
│   ├── socratic_hint_generator.py
│   └── README.md
│
├── day4-structured-output/
│   ├── structured_tutor_response.py
│   └── notes.md
│
└── day5-streaming-cost/
    ├── streaming_tutor.py
    └── notes.md
```

---

# Day 1 — Bug Explainer

## Folder
`day1-bug-explainer`

## Files
- `bug_explainer.py`
- `notes.md`

## Focus
Building a beginner-friendly debugging tutor.

## Features
- Explains Python errors
- Friendly AI responses
- Beginner-focused guidance
- Avoids direct answer dumping

## Learned
- System prompts
- User prompts
- AI behavior control
- Debugging-focused prompting

---

# Day 2 — Few-Shot Prompting

## Folder
`day2-few-shot`

## Files
- `few_shot_bug_explainer.py`
- `notes.md`

## Focus
Teaching the AI using examples.

## Features
- Few-shot examples
- Better Socratic hints
- Improved tutoring quality
- Runtime error capture

## Learned
- Few-shot prompting
- Prompt shaping
- Example-based behavior control

---

# Day 3 — Socratic Tutors

## Folder
`day3-socratic`

## Files
- `friendly_tutor.py`
- `chain_of_thought_tutor.py`
- `strict_socratic_mode.py`
- `safe_python_runner.py`
- `socratic_hint_generator.py`

## Focus
Experimenting with different tutoring styles.

## Tutor Variants

### `friendly_tutor.py`
Warm and encouraging tutor personality.

### `chain_of_thought_tutor.py`
Step-by-step reasoning style.

### `strict_socratic_mode.py`
Asks only guiding questions without revealing answers.

### `safe_python_runner.py`
Safely executes student Python code using subprocesses.

### `socratic_hint_generator.py`
Generates guided debugging hints.

## Learned
- Tutor personality design
- Socratic questioning
- Runtime analysis
- Safe subprocess execution
- Guided debugging

---

# Day 4 — Structured Outputs

## Folder
`day4-structured-output`

## Files
- `structured_tutor_response.py`
- `notes.md`

## Focus
Generating machine-readable AI responses.

## Features
JSON responses containing:
- diagnosis
- hint
- follow-up question
- confidence score

## Example

```json
{
  "diagnosis": "IndexError caused by invalid list access",
  "hint": "Check how many elements exist in the list.",
  "follow_up_question": "What is the largest valid index?",
  "confidence": 0.92
}
```

## Learned
- Structured AI outputs
- JSON formatting
- Output parsing
- UI-ready response formats

---

# Day 5 — Streaming & Cost Control

## Folder
`day5-streaming-cost`

## Files
- `streaming_tutor.py`
- `notes.md`

## Focus
Understanding streaming responses and token usage.

## Features
- Streaming AI output
- Token optimization
- Cost awareness
- Faster response rendering

## Learned
- Streaming APIs
- Token limits
- Latency handling
- AI cost optimization

---

# Prompt Library

## File
`prompt_library.md`

Contains:
- reusable prompts
- tutor prompt patterns
- debugging prompts
- Socratic prompt examples

Purpose:
- centralized prompt management
- easier experimentation
- reusable tutor behaviors

---

# Example Tutor Workflow

## Student Input

```python
numbers = [1, 2, 3]
print(numbers[5])
```

## AI Tutor Response

```text
Diagnosis:
You are trying to access a list position that does not exist.

Question:
How many items are currently inside the list?

Next Step:
Check the valid index range before accessing the list.
```

---

# Key Takeaways

Week 2 transforms the project from:
- basic AI API usage

to:
- controlled AI tutoring systems.

The tutor now:
- guides students
- explains bugs
- asks questions
- avoids directly giving answers

which is the foundation of intelligent tutoring systems.

---

# Technologies Used

| Component | Tool |
|---|---|
| Programming Language | Python |
| AI API | Groq API |
| SDK | OpenAI Python SDK |
| Environment Variables | python-dotenv |
| Sandbox Execution | subprocess |

---

# Skills Gained

- Prompt engineering
- AI tutoring design
- Few-shot learning
- Structured outputs
- Runtime debugging
- Safe code execution
- Streaming AI responses
- Behavior control for LLMs