# AI Coding Tutor Agent

An AI-powered coding tutor that helps beginner programmers debug Python code using Socratic questioning instead of directly giving answers.

---

# Week 1 Progress

## Day 1 — Environment Setup

Completed:
- Ubuntu development setup
- Git installation and configuration
- GitHub repository setup
- Python virtual environment creation
- Installed AI development packages
- VS Code setup
- Connected local repository to GitHub

Technologies installed:
- Python
- Git
- LangChain
- LangGraph
- Streamlit
- FastAPI
- ChromaDB

---

## Day 2 — Python Basics

Learned:
- Variables
- Data types
- Lists
- Dictionaries
- Conditions (`if-else`)
- Loops (`for` loop)

Completed exercises:
- Simple calculator
- Even/Odd checker
- Student marks program
- List iteration programs

Skills gained:
- Writing basic Python programs
- Using loops and conditions
- Working with collections like lists and dictionaries

---

## Day 3 — Functions & Debugging

Learned:
- Python functions
- Function parameters
- Return values
- Error handling using `try-except`
- File handling (`read` and `write`)
- Debugging Python errors

Practiced common errors:
- NameError
- IndexError
- TypeError

Completed:
- Calculator function
- File read/write programs
- Intentional bug debugging exercises

Skills gained:
- Understanding Python error messages
- Writing reusable functions
- Basic debugging workflow
- Reading and writing files

---

## Day 4 — First LLM API Calls & Parameter Tuning

Learned:
- Working with LLM APIs via the OpenAI Python client library
- Routing requests to the **Groq API Cloud platform** using ultra-fast open-source models
- Using environment variables securely to load system API keys via `.env`
- Understanding core LLM configuration settings: **Temperature** and **Max Tokens**
- Network exception handling for API infrastructure endpoints

Implemented:
- `groq_test.py`: Initial setup verification for Groq's high-speed inference cloud using `llama-3.1-8b-instant`.
- `first_llm.py`: A clean implementation verifying secure key capture and basic structural prompt execution.
- `temperature_test.py`: A comparison script executing identical prompts at opposite configuration values (`0.0` vs `1.0`) to witness deterministic precision versus creative word distribution.
- `tokens_test.py`: A text constraint pipeline using `max_tokens` to cap generational budget and analyzing `finish_reason` output properties.

Skills gained:
- Dynamic AI multi-platform application design
- Configuration management using token budget boundaries
- API architecture tracking and diagnostics
- Secure credential protection via strict `.gitignore` patterns

---

# Current Project Structure

```text
coding-tutor-agent/
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
│   ├── .env
│   ├── .env.example
│   ├── first_llm.py
│   ├── groq_test.py
│   ├── temperature_test.py
│   └── tokens_test.py
│
├── tutor-env/
├── README.md
└── .gitignore