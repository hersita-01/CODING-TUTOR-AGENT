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

## Day 4 — First LLM API Calls

Learned:
- Working with Gemini API
- Using environment variables securely
- Loading API keys using `.env`
- Sending prompts to AI models
- Receiving AI-generated responses
- Error handling for API requests

Implemented:
- Gemini 2.5 Flash integration
- Secure API key handling
- AI prompt-response workflow
- Exception handling using `try-except`

Skills gained:
- Basic AI application development
- Understanding prompt engineering
- API communication workflow
- Secure credential management

Example features:
- Prompting Gemini for coding advice
- Generating AI responses from Python
- Handling API failures gracefully

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
│   ├── first_llm.py
│   └── .env
│
├── tutor-env/
├── README.md
└── .gitignore
```

---

# Technologies Used

- Python
- Git & GitHub
- Google Gemini API
- python-dotenv
- VS Code
- Ubuntu Linux

---

# GitHub Repository

Repository Link:
https://github.com/hersita-01/CODING-TUTOR-AGENT

---

# Goal

Build an AI Coding Tutor Agent that:
- Diagnoses beginner Python bugs
- Guides learners using Socratic questioning
- Uses AI tools and memory systems
- Helps users learn instead of spoon-feeding answers
- Integrates LLMs for interactive tutoring