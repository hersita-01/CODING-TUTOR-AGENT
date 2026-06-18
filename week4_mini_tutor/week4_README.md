# Mini-Tutor v1 — AI Coding Tutor Agent

**Week 4 deliverable** · AI Agents Internship · Coding Tutor Track

---

## Problem Statement

Beginner programmers often get stuck on bugs but learn nothing when they're just handed the fixed code. Mini-Tutor v1 is an AI-powered Python tutor that actually *runs* the student's code in a safe sandbox, diagnoses the error, and guides the learner toward the fix using Socratic questions — never giving the answer directly. The goal is understanding, not correction.

---

## Architecture

```
Student (Streamlit UI)
        │
        ▼
  run_tutor_agent()          ← week4_mini_tutor.py
        │
        ▼
┌───────────────────────────────────┐
│         ReAct Loop                │
│                                   │
│  1. Build messages list           │
│     [system + history + user]     │
│                                   │
│  2. Call Groq API                 │
│     model: llama-3.3-70b-versatile│
│                                   │
│  3a. finish_reason == "stop"      │
│      → return Socratic reply      │
│                                   │
│  3b. finish_reason == "tool_calls"│
│      → convert to plain dict ✓    │
│      → execute tool               │
│      → append tool result         │
│      → loop back to step 2        │
└───────────────────────────────────┘
        │
        ▼
  Tools (local Python functions)
  ┌─────────────┐  ┌───────────┐  ┌────────────┐
  │ run_python  │  │ lint_code │  │ doc_search │
  │ subprocess  │  │   ruff    │  │ local dict │
  │  sandbox    │  │  linter   │  │  (80+ topic│
  │  15s timeout│  │           │  │  partial   │
  │  30-line max│  │           │  │  match)    │
  │  +line_num  │  │           │  │            │
  └─────────────┘  └───────────┘  └────────────┘
        │
        ▼
  Streamlit chat UI       ← week4_app.py
  iOS-style design
  Frosted nav bar
  Message bubbles
  Fixed input bar
```

**Files:**
- `week4_mini_tutor.py` — agent core: tools, schemas, ReAct loop
- `week4_app.py` — Streamlit iOS-style chat UI
- `week4_README.md` — this file

---

## Tools

| Tool | Description | When used |
|---|---|---|
| `run_python` | Executes code in a subprocess sandbox. 15s hard timeout, 30-line limit. Returns stdout + stderr + the exact failing line number. | First on every code submission — to see actual runtime behaviour |
| `lint_code` | Runs `ruff` linter (E, F, W rules). Normalises temp file path in output. | When code runs but has style/quality issues worth discussing |
| `doc_search` | Searches a 21-topic local Python docs dictionary with partial matching. | When student seems confused about a concept or keyword |

---

## Setup

```bash
pip install openai streamlit python-dotenv ruff
```

Create `.env` in the project folder:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

Never commit `.env` — add it to `.gitignore`.

---

## Run

```bash
# Streamlit UI
streamlit run week4_app.py

# CLI (no Streamlit needed)
python week4_mini_tutor.py
```

---

## Example Interactions

### 1. NameError — typo in variable name
**Student submits:**
```python
def greet(name):
    message = "Hello, " + nme
    print(message)

greet("Alice")
```

**Tutor response:**
> Diagnosis: Line 2 raises a NameError — Python cannot find a variable called `nme`.
> Question: Look closely at line 2. You're combining a string with a variable called `nme` — does that name match what you defined in the function signature?
> Next Step: Compare the spelling of every name on line 2 with your parameter name on line 1.

---

### 2. IndexError — off-by-one in range loop (beginner off-by-one bug)
**Student submits:**
```python
marks = [85, 90, 78]
for i in range(len(marks) + 1):
    print("Mark", i + 1, ":", marks[i])
```

**Tutor response:**
> Diagnosis: Line 3 raises an IndexError — the loop runs one iteration too many and tries to access `marks[3]`, which doesn't exist.
> Question: If `marks` has 3 items, what are the valid index values? And what does `range(len(marks) + 1)` actually produce?
> Next Step: Print `list(range(len(marks) + 1))` to see exactly which values `i` takes.

---

### 3. Mutable default argument — classic Python trap
**Student submits:**
```python
def add_item(item, cart=[]):
    cart.append(item)
    return cart

print(add_item("apple"))
print(add_item("banana"))
```

**Tutor response:**
> Diagnosis: The default value `[]` is created once when the function is defined, not each time it is called, so the same list is reused across calls.
> Question: What do you expect the second `print` to show? Run it and compare — does the output surprise you?
> Next Step: Look up why Python default arguments should never be mutable objects like `[]` or `{}`.

---

### 4. IndentationError — missing indent inside if block
**Student submits:**
```python
score = 75
if score >= 50:
print("Pass")
```

**Tutor response:**
> Diagnosis: Line 3 has an IndentationError — Python expects the body of an `if` block to be indented.
> Question: What does Python use indentation for, and how many spaces should line 3 be indented by?
> Next Step: Add 4 spaces (or one Tab) before `print("Pass")` and run it again.

---

### 5. Logic bug — wrong output, no crash
**Student submits:**
```python
numbers = [3, 1, 4, 1, 5]
numbers.sort()
print("Largest:", numbers[0])
```
*"I expected the largest number but got 1."*

**Tutor response:**
> Diagnosis: The code runs successfully, but `sort()` arranges numbers in ascending order by default, so `numbers[0]` is the smallest, not the largest.
> Question: Print the full sorted list — in which direction does Python's `sort()` order numbers?
> Next Step: Check whether `sort()` has a parameter that reverses the order.

---

## Known Limitations

- `doc_search` covers 80+ topics from a local dictionary, not the full Python docs.
- No session memory across page refreshes — history resets when Streamlit reruns.
- `lint_code` returns a clear error message if `ruff` is not installed, but does not auto-install it.
- Code is capped at 30 lines per the Week 4 spec — longer programs are rejected with a message suggesting they be split.
- `_install_missing_packages` runs `pip install` for any import statement not in the standard library set. Package names are validated against a simple allowlist pattern before installation, but this is still an open trust boundary: a student (or anyone using a public deployment) could trigger installation of an arbitrary PyPI package by name. Acceptable for a local/personal tutor; for any public deployment this should be replaced with a fixed allowlist of approved packages.
- The 80-topic `doc_search` dictionary is hand-curated and will drift out of date for newer Python features faster than a live `docs.python.org` query would.

## What I'd Improve Next (Week 5+)

- Replace `doc_search` with a RAG pipeline over the full Python tutorial (Week 5).
- Add a persistent learner profile tracking errors seen and concepts explained.
- Move to LangGraph for proper stateful agent management (Week 6).
- Add an LLM-as-judge eval suite for 20 common beginner bugs (Week 7).
- Use a Docker container sandbox instead of subprocess for stronger isolation (Week 8).
- Deploy to Streamlit Cloud with environment secrets management.