# Week 1 — Foundations

## Overview

Week 1 focuses on building the fundamental skills required to create an AI-powered coding tutor. The goal of this week is to become familiar with Python, environment setup, API integration, prompt construction, and model parameter tuning before moving on to more advanced concepts such as prompt engineering, tool use, and agent development.

This week serves as the foundation for all subsequent weeks in the Coding Tutor Agent project.

---

## Learning Objectives

By the end of Week 1, you should be able to:

* Set up a Python development environment
* Configure and use API keys securely
* Make API calls to a Large Language Model (LLM)
* Understand system prompts and user prompts
* Experiment with temperature and model behavior
* Process and display model responses
* Build simple command-line AI applications

---

## Topics Covered

### 1. Environment Setup

Learn how to:

* Create and activate virtual environments
* Install required Python packages
* Configure environment variables
* Store API keys securely using `.env`

---

### 2. First API Calls

Create basic programs that:

* Connect to the Groq API
* Send prompts to an LLM
* Receive and display responses
* Handle common API errors

---

### 3. Prompt Construction

Explore how prompts influence model behavior:

* System prompts
* User prompts
* Role-based prompting
* Structured instructions

Example:

```text
System: You are a helpful Python tutor.

User: Explain what a Python list is.
```

---

### 4. Temperature Experiments

Investigate how temperature affects responses.

Lower temperature:

* More deterministic
* More consistent
* Better for tutoring

Higher temperature:

* More creative
* More varied
* Better for brainstorming

Example:

```python
temperature = 0.2
```

vs

```python
temperature = 1.0
```

---

### 5. Response Processing

Learn how to:

* Extract model responses
* Format output for users
* Handle empty responses
* Display errors gracefully

---

## Skills Developed

During Week 1, the following skills were practiced:

* Python fundamentals
* API integration
* Environment management
* Prompt design
* LLM parameter tuning
* Command-line application development

---

## Key Takeaways

* Prompt quality significantly affects model responses.
* System prompts provide consistent behavior.
* Temperature controls creativity and determinism.
* Secure API key management is essential.
* Small experiments help build intuition for LLM behavior.

---

## Connection to Future Weeks

Week 1 establishes the foundation for:

### Week 2 — Prompt Engineering

* Few-shot prompting
* Socratic tutoring
* Structured outputs
* Streaming responses

### Week 3 — Tool Use

* Running Python code
* Linting and validation
* Tool-calling agents

### Week 4 — Mini Tutor

* Combining prompts, tools, and execution
* Building an interactive coding tutor
* Streamlit user interface

---

## Outcome

At the end of Week 1, a series of small Python programs were created to explore LLM interaction, prompt design, and API usage. These experiments provide the technical foundation for the more advanced tutoring system developed in later weeks.
