# Week 4 — Mini Tutor

## Overview

Week 4 brings together everything learned throughout the project to build a complete AI-powered coding tutor.

The Mini Tutor combines:

* Prompt Engineering (Week 2)
* Tool Use (Week 3)
* Safe Code Execution
* Error Analysis
* AI-Generated Feedback
* Interactive User Interfaces

The result is an educational assistant that can execute student code, analyze errors, and guide learners toward solutions using Socratic questioning rather than simply providing answers.

---

## Project Goal

The goal of the Mini Tutor is to help beginner programmers learn debugging and problem-solving skills.

Instead of giving direct solutions, the tutor:

1. Runs the student's code safely.
2. Identifies syntax and runtime errors.
3. Analyzes execution results.
4. Generates structured educational feedback.
5. Encourages students to discover fixes independently.

---

## Features

### Safe Code Execution

Student code is executed in an isolated subprocess environment.

Features include:

* AST-based validation
* Dangerous operation detection
* Temporary file execution
* Timeout protection
* Memory limits (Unix systems)
* Structured traceback analysis
* Output normalization

Execution workflow:

```text
Student Code
      │
      ▼
AST Validation
      │
      ▼
Syntax Check
      │
      ▼
Temporary File
      │
      ▼
Subprocess Execution
      │
      ▼
Execution Results
```

---

### AI-Powered Error Explanation

When an error occurs, the tutor sends:

* Student code
* Error type
* Error message
* Traceback information
* Line number

to the language model.

The model generates educational guidance rather than direct answers.

Example:

```text
Diagnosis:
The program is trying to access a list position that does not exist.

Question:
How many elements are in the list, and what is the highest valid index?

Next Step:
Trace the final iteration of the loop and check which index is being accessed.
```

---

### Socratic Tutoring

The tutoring philosophy emphasizes learning through guided discovery.

The tutor:

* Explains concepts
* Asks guiding questions
* Encourages debugging
* Avoids immediately providing solutions

Benefits:

* Better understanding
* Improved problem-solving skills
* Stronger debugging habits

---

### Interactive User Interfaces

The project supports multiple interaction modes.

#### Command Line Interface (CLI)

A lightweight terminal-based experience.

Features:

* Multi-line code input
* Error analysis
* AI-generated feedback
* Execution output display

#### Streamlit Web Application

A browser-based interface for easier interaction.

Features:

* Code input area
* Run button
* Output display
* Error explanations
* User-friendly workflow

---

## Architecture

### High-Level Workflow

```text
Student Code
        │
        ▼
Input Validation
        │
        ▼
AST Security Checks
        │
        ▼
Safe Execution Engine
        │
        ▼
Execution Results
        │
        ▼
Prompt Builder
        │
        ▼
Groq API
        │
        ▼
Socratic Tutor Response
        │
        ▼
Student Feedback
```

---

## Project Structure

```text
week4_mini_tutor/
│
├── week4_mini_tutor.py
├── week4_app.py
├── prompts.py
├── config.py
└── README.md
```

### File Descriptions

#### `week4_mini_tutor.py`

Core tutoring engine.

Responsibilities:

* Code validation
* Execution handling
* Error analysis
* Prompt construction
* AI interaction

---

#### `week4_app.py`

Streamlit web application.

Responsibilities:

* User interface
* Code submission
* Result display
* Tutor interaction

---

#### `prompts.py`

Stores tutoring prompts and response templates.

Responsibilities:

* System prompts
* Educational constraints
* Socratic guidance structure

---

#### `config.py`

Centralized configuration.

Examples:

* Model settings
* Token limits
* Timeouts
* Application constants

---

## Technologies Used

### Python

Core implementation language.

### Groq API

Used for generating tutoring responses.

Benefits:

* Fast inference
* OpenAI-compatible API
* Easy integration

### Streamlit

Used to build the web-based tutoring interface.

Benefits:

* Rapid development
* Interactive UI
* Simple deployment

### AST Module

Used for security validation and code inspection.

Benefits:

* More reliable than string-based filtering
* Detects dangerous imports and operations
* Supports safe execution workflows

---

## Educational Design Principles

The tutor follows several educational principles:

### 1. Guidance Over Answers

Students are encouraged to discover solutions rather than copy them.

### 2. Structured Feedback

Responses follow a consistent format:

```text
Diagnosis:
...

Question:
...

Next Step:
...
```

### 3. Incremental Learning

Hints are provided gradually.

### 4. Error Understanding

Focus is placed on understanding why errors occur rather than simply removing them.

---

## Example Workflow

Student submits:

```python
numbers = [1, 2, 3]
print(numbers[5])
```

Execution result:

```text
IndexError: list index out of range
```

Tutor response:

```text
Diagnosis:
The program is accessing an index that does not exist in the list.

Question:
How many elements are stored in the list?

Next Step:
Determine the largest valid index and compare it with the index being used.
```

---

## Skills Demonstrated

This project demonstrates:

* Python programming
* Prompt engineering
* AI application development
* Tool integration
* Agent design
* Secure code execution
* Error analysis
* User interface development
* Educational software design

---

## Project Evolution

### Week 1 — Foundations

* API integration
* Prompt basics
* Environment setup

### Week 2 — Prompt Engineering

* Socratic tutoring
* Structured responses
* Educational prompt design

### Week 3 — Tool Use

* Code execution tools
* Validation tools
* Agent workflows

### Week 4 — Mini Tutor

* Complete integration of prompts, tools, execution, and UI

---

## Future Improvements

Potential enhancements include:

* Docker-based sandboxing
* User authentication
* Conversation history
* Session persistence
* Automated test generation
* Multi-language support
* Enhanced debugging visualizations
* Deployment to cloud platforms

---

## Outcome

The Week 4 Mini Tutor represents the culmination of the project. It combines educational prompting, safe code execution, and AI-assisted debugging into a functional tutoring system that helps students learn programming through guided problem-solving rather than direct solution generation.
