# AI Coding Tutor Agent

An AI-powered Python Coding Tutor that helps beginner programmers learn through guided debugging, Socratic questioning, safe code execution, and AI-assisted feedback.

Instead of directly providing answers, the tutor encourages students to analyze errors, understand programming concepts, and discover solutions independently.

---

# Project Overview

The AI Coding Tutor Agent was developed as a four-week learning project that progressively explores:

* Python fundamentals
* Prompt engineering
* AI tool integration
* Safe code execution
* AI agent design
* Educational software development

Each week builds upon the previous one, culminating in a fully functional AI-powered tutoring application.

---

# Project Objectives

The primary goals of this project are to:

* Help beginners understand Python errors and debugging techniques
* Provide guided, Socratic-style tutoring instead of direct answers
* Execute and analyze student code safely
* Use AI tools to generate context-aware educational feedback
* Explore modern AI application development practices

---

# Technologies Used

| Category               | Technology                 |
| ---------------------- | -------------------------- |
| Programming Language   | Python                     |
| AI Provider            | Groq API                   |
| AI SDK                 | OpenAI Python SDK          |
| Frontend               | Streamlit                  |
| Code Validation        | AST (Abstract Syntax Tree) |
| Safe Execution         | subprocess                 |
| Environment Management | python-dotenv              |
| Linting                | Ruff                       |
| Version Control        | Git & GitHub               |

---
CODING-TUTOR-AGENT/
│
├── .vscode/
│
├── week1-foundations/
│   │
│   ├── day2-python-basics/
│   │   ├── 2ndlargestno.py
│   │   ├── basics.py
│   │   ├── celsius to fahrenheit.py
│   │   ├── char count in sentence.py
│   │   ├── digit sum.py
│   │   ├── frequency of chars.py
│   │   ├── nested tup-roll,name,marks.py
│   │   ├── number of wds in sent.py
│   │   ├── replacevowel.py
│   │   └── student.py
│   │
│   ├── day3-functions-debugging/
│   │   ├── author menu driven final.py
│   │   ├── dollar conv.py
│   │   ├── functions.py
│   │   ├── notes.txt
│   │   ├── random 3 nos.py
│   │   ├── series menu driven final.py
│   │   └── twin primes final.py
│   │
│   ├── day4-llm-api/
│   │   ├── .gitignore
│   │   ├── first_llm.py
│   │   ├── groq_test.py
│   │   ├── temperature_test.py
│   │   └── tokens_test.py
│   │
│   ├── day5-prompt-engineering/
│   │   ├── notes.txt
│   │   └── tutor_prompt.py
│   │
│   └── week1_README.md
│
├── week2-prompt-engineering/
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
│   │   ├── .gitignore
│   │   ├── chain_of_thought_tutor.py
│   │   ├── friendly_tutor.py
│   │   ├── safe_python_runner.py
│   │   ├── socratic_hint_generator.py
│   │   ├── strict_socratic_mode.py
│   │   └── __pycache__/
│   │
│   ├── day4-structured-output/
│   │   ├── structured_tutor_response.py
│   │   └── notes.md
│   │
│   ├── day5-streaming-cost/
│   │   ├── streaming_tutor.py
│   │   └── notes.md
│   │
│   ├── prompt_library.md
│   └── README.md
│
├── week3-tool-use/
│   │
│   ├── day1_tool_concepts.py
│   │
│   ├── day2-tool-schemas/
│   │   └── tool_schemas.py
│   │
│   ├── day3-tool-loop/
│   │   ├── tool_dispatcher.py
│   │   ├── tool_schemas.py
│   │   ├── tutor_agent.py
│   │   └── __pycache__/
│   │
│   ├── day4-more-tools/
│   │   ├── doc_search_tool.py
│   │   └── lint_tool.py
│   │
│   ├── day5-error-handling/
│   │   ├── robust_tool_loop.py
│   │   ├── test_failure_modes.py
│   │   └── __pycache__/
│   │
│   └── README.md
│
├── week4_mini_tutor/
│   ├── config.py
│   ├── prompts.py
│   ├── week4_app.py
│   ├── week4_mini_tutor.py
│   ├── week4_README.md
│   └── __pycache__/
│
├── .env
├── .gitignore
└── README.md
---

# Week 1 – Foundations

Focus: Learning Python fundamentals and understanding how Large Language Models can be integrated into applications.

Implemented:

* Python programming exercises
* Functions and debugging practice
* API integration using Groq
* Temperature and token experiments
* Initial prompt engineering concepts
* Basic AI tutor prototypes

Key Learning:

Understanding how language models generate responses and how prompts influence output quality.

---

# Week 2 – Prompt Engineering

Focus: Improving tutoring quality through prompt design.

Implemented:

* Bug explanation assistants
* Few-shot prompting examples
* Socratic tutoring workflows
* Chain-of-thought reasoning experiments
* Structured tutor responses
* Streaming AI responses
* Safe Python execution using AST-based validation
* Enhanced traceback parsing and execution result handling

Key Learning:

Prompt design significantly affects the quality, consistency, and educational value of AI-generated feedback.

---

# Week 3 – Tool Use

Focus: Building AI systems that use tools instead of relying only on model reasoning.

Implemented:

* Tool schemas and tool-calling workflows
* Code execution tools
* Validation and analysis pipelines
* Runtime error analysis
* Multi-step tool execution loops
* Safe execution workflows
* Tool-based tutoring agents

Key Learning:

AI systems become more reliable when they can execute code, inspect results, and use external tools to make decisions.

---

# Week 4 – Mini Tutor

Focus: Integrating all previous concepts into a complete AI-powered tutoring application.

Implemented:

* Command Line Interface (CLI)
* Streamlit-based web application
* Safe code execution pipeline
* AST-based security validation
* Timeout protection
* Memory protection
* Structured traceback analysis
* AI-generated Socratic debugging guidance
* Modular configuration and prompt management
* Improved project organization and maintainability

Key Learning:

Combining prompt engineering, tool use, and secure execution creates a practical educational AI application.

---

# Core Features

* Socratic tutoring approach
* Safe Python code execution
* Runtime error detection
* Structured traceback analysis
* AST-based security validation
* Timeout and memory protection
* AI-assisted debugging guidance
* Command Line Interface (CLI)
* Streamlit Web Interface
* Modular and maintainable architecture

---

# Example Workflow

Student Code

```python
numbers = [1, 2, 3]
print(numbers[10])
```

Runtime Error

```text
IndexError: list index out of range
```

Tutor Response

```text
Diagnosis:
The program is trying to access a list index that does not exist.

Question:
How many elements are currently stored in the list?

Next Step:
Check the valid index range before accessing an element.
```

---

# Running the Project

Clone the repository:

```bash
git clone https://github.com/hersita-01/CODING-TUTOR-AGENT.git
cd CODING-TUTOR-AGENT
```

Create a virtual environment:

```bash
python -m venv tutor-env
```

Activate the environment:

Windows:

```bash
tutor-env\Scripts\activate
```

Linux/macOS:

```bash
source tutor-env/bin/activate
```

Install dependencies:

```bash
pip install openai streamlit python-dotenv ruff
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Run the Mini Tutor:

CLI:

```bash
python week4_mini_tutor/week4_mini_tutor.py
```

Streamlit:

```bash
streamlit run week4_mini_tutor/week4_app.py
```


# Author

Developed as part of an AI Engineering learning journey focused on:

* Prompt Engineering
* AI Agents
* Tool Calling
* Safe Code Execution
* Educational AI Systems
* Full-Stack AI Application Development
