# Week 4 — Mini-Tutor v1

Mini-Tutor v1 is a complete AI-powered coding tutor application.

It combines:
- AI agents
- tool calling
- safe code execution
- Streamlit frontend
- guided debugging

into one working system.

---

# Features

- Safe Python execution
- Ruff linting
- Python documentation search
- Streamlit chat interface
- Tool-calling ReAct agent
- Socratic tutoring
- Conversation memory
- Runtime error analysis

---

# Project Files

## `week4_mini_tutor.py`

Core backend agent.

Contains:
- tool schemas
- tool execution
- ReAct loop
- subprocess sandbox
- tutor prompting
- conversation management

---

## `week4_app.py`

Frontend UI built with Streamlit.

Features:
- iOS-inspired design
- chat interface
- sticky input bar
- tutor/student bubbles
- session history

---

# Available Tools

| Tool | Purpose |
|---|---|
| `run_python` | Executes Python code safely |
| `lint_code` | Runs Ruff linting |
| `doc_search` | Explains Python concepts |

---

# Architecture

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

# Installation

## Install Dependencies

```bash
pip install openai streamlit python-dotenv ruff
```

---

# Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_api_key_here
```

---

# Run CLI Version

```bash
python3 week4_mini_tutor.py
```

---

# Run Streamlit App

```bash
streamlit run week4_app.py
```

---

# Concepts Learned

- AI agents
- Tool calling
- Safe execution
- Streamlit UI
- Conversation state
- ReAct loops
- Runtime analysis
- AI orchestration

---

# Future Improvements

- Docker sandbox
- Persistent memory
- Multi-language support
- Authentication
- Database integration
- Cloud deployment
- Voice tutoring
- Code editor integration