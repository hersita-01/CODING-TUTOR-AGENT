# Mini-Tutor v1 — AI Coding Tutor Agent

**Week 4 deliverable** for the AI Agents Internship (Coding Tutor track).

Mini-Tutor v1 is an AI-powered Python tutor that runs student code in a safe sandbox, diagnoses bugs, and guides learners toward the fix using Socratic questions — never handing over the answer directly.

---

## Architecture

```
Student message
      │
      ▼
┌─────────────────────────────────────┐
│           AGENT LOOP (ReAct)        │
│                                     │
│  Claude (claude-sonnet-4-5)         │
│       │                             │
│       ├── Thought: what to do?      │
│       │                             │
│       ├── tool_use: run_python  ────┼──► subprocess sandbox (5s timeout)
│       ├── tool_use: lint_code   ────┼──► ruff linter
│       └── tool_use: doc_search  ────┼──► local Python docs dict
│                                     │
│  Tool results fed back into loop    │
│  Loop ends when stop_reason=end_turn│
└─────────────────────────────────────┘
      │
      ▼
Socratic reply:
  Diagnosis / Question / Next Step
```

**Files:**
- `week4_mini_tutor.py` — agent core: tools, tool schemas, ReAct loop
- `week4_app.py` — Streamlit chat UI
- `week4_README.md` — this file

---

## Setup

### 1. Install dependencies
```bash
pip install anthropic streamlit python-dotenv ruff
```

### 2. Set your API key
Create a `.env` file in the same folder:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxx
```
Never commit this file — add `.env` to `.gitignore`.

### 3. Run the Streamlit UI
```bash
streamlit run week4_app.py
```
Opens at `http://localhost:8501`.

### 4. Or test via CLI (no Streamlit needed)
```bash
python week4_mini_tutor.py
```

---

## Tools

| Tool | What it does | When Claude uses it |
|---|---|---|
| `run_python` | Executes code in a subprocess sandbox (5s timeout, 30-line limit) | Always first — to see actual runtime behaviour |
| `lint_code` | Runs `ruff` to find style and quality issues | When code runs but has readability/quality problems |
| `doc_search` | Returns explanations from a local Python docs dictionary | When learner seems confused about a concept |

---

## Example Interactions

### 1. NameError — undefined variable
**Student:**
```python
def greet(name):
    message = "Hello, " + nme
    print(message)

greet("Alice")
```

**Tutor:**
> **Diagnosis:** Line 2 raises a `NameError` because `nme` is not defined — Python cannot find a variable with that name.
> **Question:** Take a close look at line 2. You're trying to use a variable called `nme` — does that name match exactly what you defined or passed in?
> **Next Step:** Compare the spelling of every name on line 2 with the parameter name in your function definition.

---

### 2. IndexError — list out of bounds
**Student:**
```python
colours = ["red", "green", "blue"]
print(colours[3])
```

**Tutor:**
> **Diagnosis:** Line 2 raises an `IndexError` — you're accessing index 3, but the list only has 3 items (indices 0, 1, 2).
> **Question:** If a list has 3 items, what is the index of the last one?
> **Next Step:** Print `len(colours)` and compare it to the index you used.

---

### 3. Infinite loop — missing increment
**Student:**
```python
i = 0
while i < 5:
    print(i)
```

**Tutor:**
> **Diagnosis:** The code timed out after 5 seconds — the while loop never ends because `i` never changes.
> **Question:** For a while loop to eventually stop, what needs to happen to the condition variable (`i`) inside the loop?
> **Next Step:** Look at what would need to change inside the loop body to make `i < 5` become False.

---

### 4. TypeError — mixing types
**Student:**
```python
age = input("Enter your age: ")
next_year = age + 1
print("Next year you will be", next_year)
```

**Tutor:**
> **Diagnosis:** Line 2 raises a `TypeError` — `input()` always returns a string, and Python cannot add a string to an integer.
> **Question:** What type does `input()` give you, and what type does `1` have? How would you make them the same type?
> **Next Step:** Look up what `int()` does — could it help here?

---

### 5. Code runs but output is unexpected
**Student submits working code:**
```python
numbers = [3, 1, 4, 1, 5]
numbers.sort()
print(numbers[0])
```
*"I expected the largest number but got 1."*

**Tutor:**
> **Diagnosis:** The code ran successfully — the output of `1` is correct given what `sort()` does by default.
> **Question:** What order does Python's `sort()` put numbers in — ascending or descending?
> **Next Step:** Try printing the full sorted list to see what order it's in, then look up whether `sort()` has a parameter to reverse the order.

---

## Known Limitations

- `doc_search` uses a local dictionary (~20 topics) — not the full Python docs.
- No multi-turn memory across sessions (history resets on page refresh).
- `lint_code` requires `ruff` to be installed; silently fails if not found.
- Code is capped at 30 lines — longer snippets are rejected.
- No support for languages other than Python.

## What I'd Improve Next (Week 5+)

- Replace `doc_search` with a RAG pipeline over the full Python tutorial (Week 5).
- Add a persistent learner profile that tracks errors seen and concepts explained.
- Move to LangGraph for proper stateful agent management (Week 6).
- Add an LLM-as-judge eval suite for 20 common beginner bugs (Week 7).
- Deploy to Streamlit Cloud with Docker sandbox for production safety (Week 8).