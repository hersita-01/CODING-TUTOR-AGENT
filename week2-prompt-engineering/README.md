# AI Coding Tutor Agent

An AI-powered coding tutor that helps beginner programmers learn Python through guided debugging, Socratic questioning, safe code execution, and AI-assisted explanations.

The tutor does not directly give answers.  
Instead, it helps students think through bugs step-by-step.

---

# Project Goal

The goal of this project is to build a modern AI coding tutor capable of:

- Understanding beginner Python mistakes
- Running student code safely
- Explaining runtime errors
- Asking guiding questions
- Using tools instead of guessing
- Teaching programming concepts interactively

This project evolves week-by-week from:
- Python foundations
- Prompt engineering
- AI tool use
- Full AI tutor applications

---

# Features

- Beginner-friendly AI tutor
- Guided debugging workflow
- Socratic questioning
- Safe Python execution sandbox
- Ruff linting integration
- Python documentation search
- Structured AI outputs
- Streaming responses
- Tool-calling AI agents
- Runtime error analysis
- Infinite loop protection
- Streamlit frontend UI

---

# Technologies Used

| Category | Tools |
|---|---|
| Programming Language | Python |
| AI API | Groq API |
| AI SDK | OpenAI Python SDK |
| Frontend UI | Streamlit |
| Linting | Ruff |
| Environment Variables | python-dotenv |
| Sandbox Execution | subprocess |
| Version Control | Git & GitHub |

---

# Complete Project Structure

```text
coding-tutor-agent/
│
├── week1-foundations/
│   ├── README.md
│   │
│   ├── day2-python-basics/
│   │   ├── basics.py
│   │   └── student.py
│   │
│   ├── day3-functions-debugging/
│   │   ├── functions.py
│   │   └── notes.txt
│   │
│   ├── day4-llm-api/
│   │   ├── first_llm.py
│   │   ├── groq_test.py
│   │   ├── temperature_test.py
│   │   └── tokens_test.py
│   │
│   └── day5-prompt-engineering/
│       ├── tutor_prompt.py
│       └── notes.txt
│
├── week2-prompt-engineering/
│   ├── README.md
│   ├── prompt_library.md
│   │
│   ├── day1-bug-explainer/
│   │   ├── bug_explainer.py
│   │   └── notes.md
│   │
│   ├── day2-few-shot/
│   │   ├── few_shot_bug_explainer.py
│   │   └── notes.md
│   │
│   ├── day3-socratic/
│   │   ├── friendly_tutor.py
│   │   ├── chain_of_thought_tutor.py
│   │   ├── strict_socratic_mode.py
│   │   ├── safe_python_runner.py
│   │   ├── socratic_hint_generator.py
│   │   └── README.md
│   │
│   ├── day4-structured-output/
│   │   ├── structured_tutor_response.py
│   │   └── notes.md
│   │
│   └── day5-streaming-cost/
│       ├── streaming_tutor.py
│       └── notes.md
│
├── week3-tool-use/
│   ├── README.md
│   ├── day1_tool_concepts.py
│   ├── day2_tool_schema.py
│   ├── day3_tool_loop.py
│   ├── day4_multi_tools.py
│   └── day5_safe_tool_agent.py
│
├── week4-mini-tutor/
│   ├── week4_mini_tutor.py
│   ├── week4_app.py
│   ├── week4_README.md
│   └── .env
│
├── tutor-env/
├── .gitignore
└── README.md
```

---

# Weekly Progression

| Week | Focus |
|---|---|
| Week 1 | Python foundations & AI API basics |
| Week 2 | Prompt engineering & tutor behavior |
| Week 3 | Tool-calling AI agents |
| Week 4 | Full AI tutor application |

---

# Week 1 — Foundations

Focus:
Learning Python fundamentals and integrating AI APIs.

Topics:
- Variables
- Loops
- Functions
- Debugging
- File handling
- AI APIs
- Prompt engineering

---

# Week 2 — Prompt Engineering

Focus:
Improving AI tutoring quality using prompts.

Topics:
- Bug explanation
- Few-shot prompting
- Socratic questioning
- Structured outputs
- Streaming responses

---

# Week 3 — Tool Use

Focus:
Allowing the AI tutor to safely use tools instead of guessing.

Topics:
- Function calling
- Tool schemas
- ReAct loops
- Safe code execution
- Linting
- Documentation search
- Runtime protection

---

# Week 4 — Mini-Tutor v1

Focus:
Building a complete AI-powered coding tutor application.

Features:
- Streamlit UI
- Tool-calling AI agent
- Safe subprocess execution
- Conversation memory
- Guided debugging workflow

---

# Installation

## Clone Repository

```bash
git clone <your-repo-url>
cd coding-tutor-agent
```

---

## Create Virtual Environment

```bash
python3 -m venv tutor-env
source tutor-env/bin/activate
```

---

## Install Dependencies

```bash
pip install openai streamlit python-dotenv ruff
```

---

# Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

# Run Week 4 Mini-Tutor

## CLI Version

```bash
python3 week4_mini_tutor.py
```

---

## Streamlit App

```bash
streamlit run week4_app.py
```

---

# Example Tutor Workflow

## Student Code

```python
numbers = [1, 2, 3]
print(numbers[10])
```

## Runtime Error

```text
IndexError: list index out of range
```

## Tutor Response

```text
Diagnosis:
You are trying to access a list position that does not exist.

Question:
How many elements are currently inside the list?

Next Step:
Check the valid index range before accessing the list.
```

---

# Core AI Tools

| Tool | Purpose |
|---|---|
| `run_python` | Executes Python safely |
| `lint_code` | Runs Ruff linting |
| `doc_search` | Explains Python concepts |

---

# AI Tutor Architecture

```text
Student
   ↓
Streamlit UI
   ↓
Tutor Agent
   ↓
Tool Loop
   ↓
run_python / lint_code / doc_search
   ↓
Tool Result
   ↓
Tutor Response
```

---

# Key Learning Outcomes

This project teaches:
- Python programming
- Prompt engineering
- AI agents
- Tool calling
- Safe execution systems
- Runtime analysis
- Streamlit frontend development
- Full-stack AI application design

---

# Future Improvements

- Docker sandboxing
- Persistent memory
- Multi-language support
- Voice tutoring
- Authentication system
- Student progress tracking
- Vector database integration
- Cloud deployment

---

# Author

Built as part of an AI engineering learning journey focused on:
- AI tutors
- Prompt engineering
- Tool-calling agents
- Safe execution systems
- Full-stack AI applications