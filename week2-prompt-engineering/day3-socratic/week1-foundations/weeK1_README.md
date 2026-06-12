# Week 1 — Foundations

Week 1 focuses on building the core foundations required for developing AI-powered applications and coding tutors.

This week covers:
- Python basics
- Functions
- Debugging
- File handling
- AI API integration
- Prompt engineering

The goal was to move from:
- beginner Python programming

to:
- building the first AI tutor prompts.

---

# Goals

- Learn Python fundamentals
- Understand debugging
- Work with functions and files
- Integrate AI APIs
- Build beginner-friendly tutor prompts
- Learn prompt engineering basics

---

# Concepts Learned

- Variables
- Data types
- Lists & dictionaries
- Conditions
- Loops
- Functions
- Error handling
- File handling
- API integration
- Environment variables
- Prompt engineering

---

# Week 1 File Structure

```text
week1-foundations/
│
├── day2-python-basics/
│   ├── basics.py
│   └── student.py
│
├── day3-functions-debugging/
│   ├── functions.py
│   └── notes.txt
│
├── day4-llm-api/
│   ├── first_llm.py
│   ├── groq_test.py
│   ├── temperature_test.py
│   └── tokens_test.py
│
└── day5-prompt-engineering/
    ├── tutor_prompt.py
    └── notes.txt
```

---

# Day 1 — Environment Setup

## Focus
Preparing the development environment.

## Setup Completed
- Ubuntu development setup
- Git & GitHub configuration
- VS Code setup
- Python virtual environment
- AI libraries installation

## Technologies Installed
- Python
- Git
- Streamlit
- LangChain
- LangGraph
- FastAPI
- ChromaDB

## Learned
- Virtual environments
- Package installation
- Git basics
- Project setup workflow

---

# Day 2 — Python Basics

## Folder
`day2-python-basics`

## Files
- `basics.py`
- `student.py`

## Focus
Learning Python fundamentals.

## Topics Covered
- Variables
- Data types
- Conditions
- Loops
- Lists
- Dictionaries

## Programs Created
- Calculator
- Even/Odd checker
- Student marks program
- List iteration exercises

## Learned
- Writing Python programs
- Using loops and conditions
- Working with collections

---

# Day 3 — Functions & Debugging

## Folder
`day3-functions-debugging`

## Files
- `functions.py`
- `notes.txt`

## Focus
Learning reusable code and debugging.

## Topics Covered
- Functions
- Parameters
- Return values
- Error handling
- File handling

## Errors Practiced
- NameError
- IndexError
- TypeError

## Learned
- Reading Python errors
- Writing reusable functions
- Debugging workflow
- File operations

---

# Day 4 — LLM API Integration

## Folder
`day4-llm-api`

## Files
- `first_llm.py`
- `groq_test.py`
- `temperature_test.py`
- `tokens_test.py`

## Focus
Connecting Python with AI APIs.

## Topics Covered
- Groq API integration
- OpenAI-compatible SDK
- API key handling
- Temperature settings
- Token control

## Learned
- Sending prompts to AI models
- Secure API usage
- AI response generation
- Model parameter tuning

---

# Day 5 — Prompt Engineering

## Folder
`day5-prompt-engineering`

## Files
- `tutor_prompt.py`
- `notes.txt`

## Focus
Designing beginner-friendly AI tutor behavior.

## Topics Covered
- Prompt engineering
- System prompts
- Role prompting
- Socratic questioning
- AI behavior control

## Example Tutor Prompt

```python
prompt = """
You are a beginner-friendly Python tutor.

Rules:
- Never directly give the answer
- Ask guiding questions
- Encourage the student
- Explain concepts simply

Student Question:
"My Python loop is not working."
"""
```

## Learned
- Designing tutor-style AI behavior
- Guiding instead of solving
- Controlling AI responses using prompts

---

# Technologies Used

| Component | Tool |
|---|---|
| Programming Language | Python |
| Version Control | Git & GitHub |
| AI API | Groq API |
| SDK | OpenAI Python SDK |
| Environment Variables | python-dotenv |

---

# Example Progression

## Beginning of Week

```python
print("Hello World")
```

## End of Week

```python
prompt = """
You are a Python tutor.
Guide students instead of giving answers.
"""
```

This marks the transition from:
- basic Python programming

to:
- AI-powered tutoring systems.

---

# Key Takeaways

Week 1 builds the foundation for the entire project.

The focus shifts from:
- learning Python

to:
- building intelligent AI tutoring systems.

This week prepares the groundwork for:
- prompt engineering
- AI agents
- tool calling
- full AI tutor applications
```