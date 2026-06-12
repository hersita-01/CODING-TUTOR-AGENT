# Week 3 — Tool Use

Week 3 focuses on teaching the AI tutor how to safely use tools instead of guessing outputs.

This is the week where the tutor evolves from:
- prompt-based responses

to:
- real tool-using AI agents.

The tutor can now:
- execute Python code
- lint student code
- search Python documentation
- safely handle runtime failures

---

# Goals

- Learn AI function/tool calling
- Build tool schemas
- Implement a ReAct-style tool loop
- Safely execute Python code
- Handle runtime failures and infinite loops
- Build defensive AI systems

---

# Concepts Learned

- Tool calling
- Function schemas
- ReAct loops
- Sandboxed execution
- Subprocess handling
- Timeout protection
- Runtime analysis
- Multi-tool orchestration
- Defensive programming

---

# Week 3 File Structure

```text
week3-tool-use/
│
├── day1_tool_concepts.py
├── day2_tool_schema.py
├── day3_tool_loop.py
├── day4_multi_tools.py
├── day5_safe_tool_agent.py
└── README.md
```

---

# Day 1 — Tool Calling Concepts

## File
- `day1_tool_concepts.py`

## Focus
Understanding how AI models call tools/functions.

## Learned
- Function calling basics
- AI → tool interaction flow
- ReAct agent concepts
- Why tools are needed

## Key Idea

Instead of guessing outputs, the AI should:
1. choose a tool
2. run the tool
3. observe results
4. respond using real outputs

---

# Day 2 — Tool Schemas

## File
- `day2_tool_schema.py`

## Focus
Designing tool definitions in JSON format.

## Built Tool Schemas
- `run_python`
- `lint_code`
- `doc_search`

## Learned
- JSON schema design
- Parameter validation
- Tool descriptions
- AI-readable interfaces

---

# Day 3 — Tool Loop

## File
- `day3_tool_loop.py`

## Focus
Building the ReAct-style execution loop.

## Features
- AI selects tool
- Python subprocess execution
- Tool result returned to model
- Runtime observation

## Learned
- ReAct architecture
- Tool execution flow
- Runtime analysis
- Subprocess sandboxing

---

# Day 4 — Multiple Tools

## File
- `day4_multi_tools.py`

## Focus
Adding multiple tools and routing logic.

## Tools Added

### `run_python`
Safely executes Python code.

### `lint_code`
Runs Ruff linting checks.

### `doc_search`
Searches Python concept explanations.

## Learned
- Multi-tool orchestration
- Tool routing
- Runtime + static analysis combination

---

# Day 5 — Safe Tool Agent

## File
- `day5_safe_tool_agent.py`

## Focus
Making the AI tutor safer and more reliable.

## Features
- Infinite loop protection
- Hard execution timeout
- Missing argument handling
- Invalid tool handling
- Safer subprocess execution

## Learned
- Defensive programming
- AI safety basics
- Fault tolerance
- Runtime protection

---

# Tool Flow Architecture

```text
Student Input
      ↓
AI Agent
      ↓
Tool Selection
      ↓
Tool Execution
      ↓
Tool Result
      ↓
AI Explanation
```

---

# Example Workflow

## Student Code

```python
numbers = [1, 2, 3]
print(numbers[10])
```

## Tool Used
`run_python`

## Runtime Result
```text
IndexError: list index out of range
```

## Tutor Response

```text
Diagnosis:
You are trying to access a list position that does not exist.

Question:
How many elements are actually inside the list?

Next Step:
Check the valid index range for the list.
```

---

# Safety Rule

Never execute student code inside the main Python process.

Always use:
- subprocess
- hard timeouts
- sandboxing

to prevent:
- infinite loops
- crashes
- unsafe execution

---

# Technologies Used

| Component | Tool |
|---|---|
| Programming Language | Python |
| Sandbox Execution | subprocess |
| Linting | Ruff |
| AI Integration | Groq API |
| SDK | OpenAI Python SDK |

---

# Key Takeaway

Week 3 is where the project evolves from:
- AI chatting

to:
- real AI agent systems that can observe and reason using tools.