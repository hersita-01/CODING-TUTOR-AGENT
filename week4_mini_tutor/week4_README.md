# Week 4 — Mini-Tutor v2

An AI-powered coding tutor that runs your Python code, diagnoses bugs, and guides you to the fix using Socratic questions — never just handing you the answer.

Built as the orchestration layer on top of Week 2 (secure sandbox) and Week 3 (lint + doc tools).

---

## Project Structure

```
CODING-TUTOR-AGENT/
├── week2-prompt-engineering/
│   └── day3-socratic/
│       └── safe_python_runner.py     ← Week 2: AST security + execution sandbox
│
├── week3-tool-use/
│   ├── day3-tool-loop/
│   │   └── tool_dispatcher.py        ← Week 3: tool router
│   └── day4-more-tools/
│       ├── lint_tool.py
│       └── doc_search_tool.py
│
└── week4_mini_tutor/
    ├── .env                          ← your GROQ_API_KEY goes here
    ├── config.py                     ← all tunable constants
    ├── prompts.py                    ← system prompt builder
    ├── week4_mini_tutor.py           ← agent core (ReAct loop)
    └── week4_app.py                  ← Streamlit UI  ← run this
```

---

## Architecture

Week 4 is the orchestration layer. It does not reimplement anything from Week 2 or Week 3.

| Responsibility | Handled by |
|---|---|
| AST security, memory limit, subprocess isolation | Week 2 `safe_python_runner.py` |
| Code linting via ruff | Week 3 `tool_dispatcher` → `lint_tool.py` |
| Python docs search | Week 3 `tool_dispatcher` → `doc_search_tool.py` |
| ReAct agent loop | Week 4 `week4_mini_tutor.py` |
| Conversation history | Week 4 `week4_mini_tutor.py` |
| Input classification (code / dict / JSON / question) | Week 4 `week4_mini_tutor.py` |
| `input()` mocking for interactive programs | Week 4 `week4_mini_tutor.py` |
| Auto-install missing packages | Week 4 `week4_mini_tutor.py` |
| Streamlit chat UI | Week 4 `week4_app.py` |

---

## Setup

### 1. Install dependencies

```bash
pip install openai streamlit python-dotenv ruff
```

### 2. Create your `.env` file

Inside `week4_mini_tutor/`, create a file named `.env`:

```
GROQ_API_KEY=your_actual_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### 3. Run the Streamlit UI

```bash
cd CODING-TUTOR-AGENT/week4_mini_tutor
streamlit run week4_app.py
```

Opens at `http://localhost:8501` automatically.

---

## Configuration

All constants are in `config.py`. Edit them without touching the agent logic.

| Constant | Default | Purpose |
|---|---|---|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM used for the agent |
| `MAX_TOOL_CALLS` | `8` | Max tool calls per student turn |
| `MAX_CODE_LINES` | `30` | Max lines per code snippet |
| `TIMEOUT_SECONDS` | `5` | Execution timeout passed to Week 2 sandbox |
| `MAX_RETRIES` | `2` | API retry budget for rate-limit / network errors |
| `RETRY_BACKOFF_S` | `2` | Back-off base in seconds (multiplied by attempt number) |

---

## Tools

The agent has three tools available per turn.

### `run_python`
Executes a Python snippet inside the Week 2 sandbox.

Week 4 adds before delegating:
- Detects JSON / dict input and wraps it in runnable Python
- Auto-installs missing third-party packages via pip
- Injects an `input()` mock so interactive programs don't hang
- Enforces the `MAX_CODE_LINES` limit

Security (AST visitor, memory cap, subprocess isolation) is fully handled by Week 2.

### `lint_code`
Delegates to Week 3 `tool_dispatcher.dispatch("lint_code")`.
Falls back to calling `ruff` directly if Week 3 is not found.

### `doc_search`
Delegates to Week 3 `tool_dispatcher.dispatch("doc_search")`.
Falls back to returning a direct `docs.python.org` search URL.

---

## Fallback Modes

Week 4 degrades gracefully when Week 2 or Week 3 cannot be found.

| Missing | Effect |
|---|---|
| Week 2 `safe_python_runner.py` | Execution falls back to a subprocess-only sandbox (timeout, no AST security). A `WARNING` is logged. |
| Week 3 `tool_dispatcher.py` | `lint_code` calls ruff directly. `doc_search` returns a Python docs URL. |
| Both missing | Tutor still runs; security and tool quality are reduced. |

The startup banner in the Streamlit sidebar shows which weeks loaded successfully.

---

## How the Agent Works

Week 4 uses the **ReAct pattern** (Reason + Act):

1. Student submits code or a question via the UI.
2. Agent calls `run_python` first (always, per system prompt rules).
3. Based on the result, the agent may also call `lint_code` or `doc_search`.
4. Agent produces a structured reply with three sections:
   - **Diagnosis** — what is wrong, citing the exact line number
   - **Question** — one Socratic question pointing toward the issue
   - **Next Step** — one small concrete action for the student
5. The agent never reveals the corrected code.

Tool calls are capped at `MAX_TOOL_CALLS` per turn. Conversation history is maintained across turns so the tutor remembers context.

---

## Module Reference

### `config.py`
Single source of truth for all tunable constants. Import from here; never hardcode values in other modules.

### `prompts.py`
Exports `build_system_prompt(week2_available, week3_available) -> str`.
Embeds live sandbox status and `MAX_TOOL_CALLS` into the prompt at startup.

### `week4_mini_tutor.py`
Main agent module. Public API:

```python
from week4_mini_tutor import run_tutor_agent, MAX_CODE_LINES

reply, updated_history = run_tutor_agent(
    student_message="...",
    conversation_history=[]   # pass [] for a new session
)
```

`run_tutor_agent` returns `(reply: str, updated_history: list[dict])`.
Pass `updated_history` back in on the next turn to maintain context.

### `week4_app.py`
Streamlit UI. Imports only `run_tutor_agent` and `MAX_CODE_LINES` from `week4_mini_tutor`. All session state, rendering, and styling lives here.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `✗ Week 2 NOT FOUND` in sidebar | Ensure `safe_python_runner.py` is at `week2-prompt-engineering/day3-socratic/` |
| `✗ Week 3 NOT FOUND` in sidebar | Ensure `tool_dispatcher.py` is at `week3-tool-use/day3-tool-loop/` |
| `GROQ_API_KEY is missing` error | Create `.env` in `week4_mini_tutor/` with `GROQ_API_KEY=your_key` |
| `Model unavailable` error | Change `GROQ_MODEL` in `config.py` to another model on Groq |
| `<function/...>` visible in replies | Replace `week4_app.py` with the latest version (includes `_strip_tool_traces`) |
| Blank reply after submit | Check your API key is valid at console.groq.com |

---

## Dependencies

| Package | Purpose |
|---|---|
| `openai` | Groq API client (OpenAI-compatible) |
| `streamlit` | Chat UI |
| `python-dotenv` | Loads `GROQ_API_KEY` from `.env` |
| `ruff` | Linter used by `lint_code` fallback |