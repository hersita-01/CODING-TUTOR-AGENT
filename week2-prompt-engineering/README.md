# Week 2 — Prompt Engineering

## Overview

Week 2 focuses on prompt engineering — the process of designing prompts that guide Large Language Models (LLMs) toward consistent, helpful, and educational responses.

The goal of this week is to explore how different prompting strategies affect the quality of tutoring interactions. Instead of changing the underlying model, various prompt designs are tested to understand how instructions, examples, and response structures influence behavior.

This week serves as the bridge between basic API usage (Week 1) and tool-using AI systems (Week 3).

---

## Learning Objectives

By the end of Week 2, you should be able to:

* Design effective system prompts
* Compare different tutoring styles
* Use Socratic questioning techniques
* Create structured AI responses
* Understand chain-of-thought prompting
* Experiment with few-shot learning
* Improve consistency through prompt design

---

## Topics Covered

### 1. Friendly Tutor

A tutoring style focused on:

* Encouragement
* Positive reinforcement
* Beginner-friendly explanations
* Reducing student frustration

Example behavior:

```text
Great attempt!

Let's think about what happens when the loop reaches the last index.
What value do you think i + 1 has at that point?
```

---

### 2. Strict Socratic Tutor

A tutoring style that avoids giving direct answers.

The tutor:

* Diagnoses the issue
* Asks guiding questions
* Encourages independent problem-solving
* Provides hints rather than solutions

Example:

```text
Diagnosis:
Your program is accessing an index that may not exist.

Question:
What is the largest valid index in a list of length 5?

Next Step:
Try tracing the loop manually for the final iteration.
```

---

### 3. Chain-of-Thought Prompting

Experiments with encouraging the model to reason step-by-step before producing an answer.

Benefits:

* More accurate explanations
* Better debugging assistance
* Improved reasoning transparency

Example:

```text
Think through the program execution step-by-step before explaining the error.
```

---

### 4. Socratic Hint Generation

Focused on producing hints instead of solutions.

Goals:

* Promote active learning
* Encourage debugging skills
* Prevent answer dumping

The tutor guides students toward discovering the fix themselves.

---

### 5. Safe Python Runner

One of the most important components introduced during Week 2.

Features:

* AST-based code validation
* Detection of dangerous operations
* Temporary file execution
* Subprocess isolation
* Execution timeout handling
* Memory limits (Unix systems)
* Structured traceback parsing
* Safe output handling

Execution flow:

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
Output / Traceback
      │
      ▼
AI Tutor Explanation
```

---

## Key Concepts Explored

### System Prompts

System prompts define the tutor's overall behavior.

Example:

```text
You are a Socratic Python tutor.
Never provide the complete solution.
Guide students using questions.
```

---

### Structured Outputs

Responses were organized into sections such as:

```text
Diagnosis:
...

Question:
...

Next Step:
...
```

Benefits:

* Consistent responses
* Better readability
* Easier learning progression

---

### Prompt Consistency

Experiments demonstrated that:

* Clear instructions improve reliability
* Structured formats reduce randomness
* Explicit constraints improve educational value

---

## Skills Developed

During Week 2, the following skills were practiced:

* Prompt engineering
* Educational AI design
* Socratic tutoring techniques
* Structured response generation
* Chain-of-thought reasoning
* Secure code execution
* Error analysis and explanation

---

## Project Files

### Tutor Variations

* `friendly_tutor.py`
* `strict_socratic_mode.py`
* `chain_of_thought_tutor.py`
* `socratic_hint_generator.py`

These files experiment with different tutoring approaches and prompt structures.

### Execution Engine

* `safe_python_runner.py`

Provides secure execution, AST validation, subprocess isolation, timeout handling, and traceback analysis.

---

## Key Takeaways

* Prompt design significantly influences model behavior.
* Structured outputs improve consistency and readability.
* Socratic tutoring promotes deeper learning than direct answers.
* Secure code execution is essential when running student code.
* AST-based validation is more reliable than string-based blacklists.
* Educational effectiveness depends as much on prompt design as on model capability.

---

## Connection to Future Weeks

### Week 3 — Tool Use

Week 3 expands beyond prompting by allowing the tutor to:

* Execute student code
* Run analysis tools
* Inspect outputs programmatically
* Make decisions based on tool results

### Week 4 — Mini Tutor

Week 4 combines:

* Prompt engineering
* Tool use
* Safe code execution
* AI tutoring workflows

into a complete interactive coding tutor.

---

## Outcome

At the end of Week 2, multiple tutoring strategies were explored and evaluated, while a secure execution framework was developed for running student code safely. These experiments established the educational and technical foundations for the tool-using coding tutor built in later weeks.
