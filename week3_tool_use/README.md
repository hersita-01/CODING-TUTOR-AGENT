\# Week 3 — Tool Use

## Overview

Week 3 focuses on one of the most important concepts in modern AI systems: **tool use**.

Until this point, the tutor relied entirely on prompting and language model reasoning. In Week 3, the tutor gains the ability to interact with external tools, execute Python code, analyze results, and make decisions based on real program behavior rather than guesses.

This marks the transition from a conversational AI assistant to an AI-powered coding agent.

---

## Learning Objectives

By the end of Week 3, you should be able to:

* Understand the concept of tool-calling agents
* Design Python functions as AI tools
* Execute student code safely
* Analyze execution results
* Perform linting and validation
* Build multi-tool workflows
* Connect LLM reasoning with programmatic actions

---

## Why Tool Use Matters

Without tools, an AI tutor can only infer what code does.

Example:

```python
numbers = [1, 2, 3]
print(numbers[5])
```

A language model can predict that this will likely cause an error.

However, with tool use, the tutor can:

1. Run the code
2. Capture the actual error
3. Analyze the traceback
4. Generate targeted guidance

This allows the tutor to work from facts instead of assumptions.

---

## Topics Covered

### Day 1 — Building Your First Tool

Introduction to tool-calling concepts.

Goals:

* Understand how tools extend LLM capabilities
* Design simple Python helper functions
* Connect tool outputs to model reasoning

Key idea:

```text
User Request
      │
      ▼
LLM
      │
      ▼
Tool
      │
      ▼
Result
      │
      ▼
LLM Response
```

---

### Day 2 — Code Execution Tools

Building tools capable of running student programs.

Features:

* Execute Python code
* Capture stdout
* Capture stderr
* Return structured results

Example workflow:

```text
Student Code
      │
      ▼
run_python()
      │
      ▼
Execution Result
      │
      ▼
Tutor Analysis
```

---

### Day 3 — Linting Tools

Introduction to static code analysis.

Goals:

* Detect style issues
* Identify common mistakes
* Provide early feedback before execution

Examples:

* Missing indentation
* Naming issues
* Unused variables
* Formatting problems

---

### Day 4 — Multi-Tool Workflows

Combining multiple tools into a single tutoring process.

The tutor can:

1. Validate code
2. Run linting
3. Execute the program
4. Collect outputs
5. Generate educational feedback

Workflow:

```text
Student Code
      │
      ▼
Validation Tool
      │
      ▼
Lint Tool
      │
      ▼
Execution Tool
      │
      ▼
Tutor Response
```

---

### Day 5 — Safe Tool Agent

The culmination of Week 3.

A complete tool-using tutor capable of:

* Running code safely
* Detecting execution errors
* Performing validation
* Producing structured educational guidance

This serves as the direct precursor to the Week 4 Mini Tutor.

---

## Core Tools Developed

### 1. Python Execution Tool

Purpose:

* Run student code
* Capture output
* Capture exceptions
* Return structured execution results

Example:

```python
print("Hello World")
```

Output:

```text
Hello World
```

---

### 2. Linting Tool

Purpose:

* Analyze source code without running it
* Detect common quality issues
* Improve code readability

Benefits:

* Faster feedback
* Reduced debugging effort
* Better coding practices

---

### 3. Validation Tool

Purpose:

* Check code before execution
* Prevent invalid inputs
* Improve system robustness

Examples:

* Empty code detection
* Syntax checking
* Security checks

---

## Agent Architecture

The Week 3 tutor follows a simple agent pattern:

```text
Student Request
        │
        ▼
     LLM Agent
        │
        ▼
Tool Selection
        │
        ▼
Tool Execution
        │
        ▼
Tool Results
        │
        ▼
Educational Response
```

The agent decides which tool to use and incorporates the results into its response.

---

## Educational Design

A major goal of Week 3 is preserving the educational philosophy established in Week 2.

The tutor does not simply report errors.

Instead, it:

* Diagnoses the issue
* Explains the underlying concept
* Uses Socratic questioning
* Encourages independent problem-solving

Example format:

```text
Diagnosis:
The program is attempting to access a list index that does not exist.

Question:
What is the highest valid index in this list?

Next Step:
Trace the final loop iteration manually and check which index is being accessed.
```

---

## Skills Developed

During Week 3, the following skills were practiced:

* Tool design
* Agent architecture
* Code execution workflows
* Static analysis
* Error handling
* Structured data processing
* Educational feedback generation
* AI application engineering

---

## Key Takeaways

* LLMs become significantly more capable when connected to tools.
* Tool outputs provide reliable facts for reasoning.
* Execution results are more trustworthy than model guesses.
* Multi-tool workflows enable richer tutoring experiences.
* Educational guidance remains important even when tools provide exact answers.

---

## Connection to Future Weeks

### Week 1 — Foundations

Provided:

* Python fundamentals
* API integration
* Prompt basics

### Week 2 — Prompt Engineering

Provided:

* Socratic tutoring
* Structured outputs
* Educational prompting

### Week 4 — Mini Tutor

Week 4 combines:

* Prompt engineering
* Tool use
* Safe code execution
* Interactive UI

into a complete AI-powered coding tutor capable of assisting students through the debugging process.

---

## Outcome

At the end of Week 3, the tutor evolves from a prompt-driven assistant into a tool-using AI agent capable of executing code, analyzing results, and generating educational feedback based on real program behavior. This week establishes the technical foundation for the fully integrated tutoring system built in Week 4.
