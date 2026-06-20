# -----------------------------------
# WEEK 4 - MINI-TUTOR v2
# CORE AGENT  —  GROQ API
# -----------------------------------
#
# Architecture: calls Week 2 and Week 3 instead of reimplementing them.
#
# Week 2  safe_python_runner.py
#   └─ run_python_safely()     ← execution sandbox (AST security, timeout,
#   └─ find_forbidden_operation()   memory limit, subprocess isolation)
#   └─ RunResult               ← structured result object
#
# Week 3  tool_dispatcher.py
#   └─ dispatch()              ← routes lint_code and doc_search tool calls
#
# Week 4  week4_mini_tutor.py  (this file)
#   └─ run_python()            ← thin wrapper: input mock + auto-install
#                                 then calls run_python_safely()
#   └─ lint_code()             ← delegates to Week 3 dispatch("lint_code")
#   └─ doc_search()            ← delegates to Week 3 dispatch("doc_search")
#   └─ run_tutor_agent()       ← ReAct loop (unchanged)
#
# What this file no longer reimplements:
#   ✗ AST security visitor           → Week 2 safe_python_runner.py
#   ✗ Subprocess sandbox             → Week 2 safe_python_runner.py
#   ✗ Memory limit                   → Week 2 safe_python_runner.py
#   ✗ Path normalisation             → Week 2 safe_python_runner.py
#   ✗ ruff linter wrapper            → Week 3 tool_dispatcher / lint_tool.py
#   ✗ doc search implementation      → Week 3 tool_dispatcher / doc_search_tool.py
#   ✗ Retry/backoff logic            → kept here (agent-specific concern)
#
# Requires:  pip install openai python-dotenv ruff
#            GROQ_API_KEY in .env
#            safe_python_runner.py in same folder or day3-socratic/
#            tool_dispatcher.py   in same folder or day3-tool-loop/
# -----------------------------------

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# -----------------------------------
# CROSS-FOLDER IMPORTS
# Supports any working directory — same pattern used in Week 3 files.
# -----------------------------------

def _add_to_path(candidates: list[Path]) -> None:
    for c in candidates:
        if c.exists() and str(c) not in sys.path:
            sys.path.insert(0, str(c))

_here = Path(__file__).resolve().parent   # CODING-TUTOR-AGENT/week4_mini_tutor/
_root = _here.parent                      # CODING-TUTOR-AGENT/

# safe_python_runner.py
# Primary:  week2-prompt-engineering/day3-socratic/  (original Week 2 location)
# Fallback: week3-tool-use/shared/
_add_to_path([
    _root / "week2-prompt-engineering" / "day3-socratic",
    _root / "week3-tool-use" / "shared",
    _here,
])

# tool_dispatcher.py + tool_schemas.py
# Location: week3-tool-use/day3-tool-loop/
_add_to_path([
    _root / "week3-tool-use" / "day3-tool-loop",
])

# lint_tool.py + doc_search_tool.py
# Location: week3-tool-use/day4-more-tools/
_add_to_path([
    _root / "week3-tool-use" / "day4-more-tools",
])

# --- Import Week 2 sandbox ---
try:
    from safe_python_runner import (
        run_python_safely,
        find_forbidden_operation,
        RunResult,
    )
    _WEEK2_AVAILABLE = True
except ImportError:
    _WEEK2_AVAILABLE = False

# --- Import Week 3 dispatcher ---
try:
    from tool_dispatcher import dispatch as _w3_dispatch
    _WEEK3_AVAILABLE = True
except ImportError:
    _WEEK3_AVAILABLE = False


# -----------------------------------
# CONSTANTS
# -----------------------------------

MAX_TOOL_CALLS  = 8
MAX_CODE_LINES  = 30          # Week 4 brief: ≤30 lines per snippet
TIMEOUT_SECONDS = 5           # Week 2 default is 3s; 5s for interactive code
GROQ_MODEL      = "llama-3.3-70b-versatile"
MAX_RETRIES     = 2           # Week 3 robust_tool_loop pattern
RETRY_BACKOFF_S = 2


# -----------------------------------
# STDLIB SET  (never pip-install these)
# -----------------------------------

STDLIB_MODULES = {
    "os", "sys", "re", "json", "math", "time", "datetime", "random",
    "string", "io", "pathlib", "collections", "itertools", "functools",
    "operator", "copy", "pprint", "types", "typing", "abc", "dataclasses",
    "enum", "struct", "array", "queue", "heapq", "bisect", "weakref",
    "gc", "inspect", "ast", "dis", "traceback", "warnings", "contextlib",
    "threading", "multiprocessing", "subprocess", "socket", "ssl",
    "http", "urllib", "email", "html", "xml", "csv", "sqlite3",
    "hashlib", "hmac", "secrets", "base64", "uuid", "tempfile",
    "shutil", "glob", "fnmatch", "stat", "logging", "unittest",
    "doctest", "argparse", "configparser", "pickle", "shelve",
    "zlib", "gzip", "zipfile", "tarfile", "platform", "signal",
    "atexit", "builtins", "keyword", "token", "tokenize",
    "textwrap", "difflib", "decimal", "fractions", "statistics",
    "cmath", "numbers", "concurrent", "asyncio", "selectors",
}


# -----------------------------------
# HELPER: auto-install missing packages
# Same validation pattern as the previous version — package names are
# validated against PyPI naming rules before installation.
# -----------------------------------

def _install_missing_packages(code: str) -> list:
    pattern   = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE)
    found     = set(re.findall(pattern, code))
    external  = [p for p in found if p not in STDLIB_MODULES]
    valid_name = re.compile(r'^[a-zA-Z0-9_\-\.]{1,100}$')
    external  = [p for p in external if valid_name.match(p)]

    installed = []
    for pkg in external:
        try:
            __import__(pkg)
        except ImportError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--", pkg, "-q"],
                    capture_output=True, timeout=30
                )
                installed.append(pkg)
            except Exception:
                pass
    return installed


# -----------------------------------
# HELPER: mock input() calls
# Injected as a preamble so interactive programs don't hang.
# This is a Week 4 concern (UX for students) — not a security concern,
# which is why it lives here rather than in Week 2's sandbox.
# -----------------------------------

_INPUT_MOCK = """\
import builtins as _builtins
_input_call_count = 0
_INPUT_RESPONSES = [
    "Alice", "1000", "Bob", "500", "1", "2", "3", "test", "yes", "no",
    "0", "10", "hello", "world", "quit", "exit", "6"
]
def _mock_input(prompt=""):
    global _input_call_count
    print(f"[INPUT] {prompt}", end="")
    response = _INPUT_RESPONSES[_input_call_count % len(_INPUT_RESPONSES)]
    _input_call_count += 1
    print(response)
    return response
_builtins.input = _mock_input

"""

def _has_input_calls(code: str) -> bool:
    return bool(re.search(r'\binput\s*\(', code))

def _inject_input_mock(code: str) -> str:
    return _INPUT_MOCK + code


# -----------------------------------
# HELPER: classify input type
# Unchanged from previous version — Week 4 specific UX feature.
# -----------------------------------

def _classify_input(text: str) -> str:
    stripped = text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or \
       (stripped.startswith("[") and stripped.endswith("]")):
        try:
            json.loads(stripped)
            return "json"
        except json.JSONDecodeError:
            pass
        try:
            import ast as _ast
            _ast.literal_eval(stripped)
            return "dict"
        except Exception:
            pass
    if re.match(r'^\s*\{', stripped) and ":" in stripped:
        return "dict"
    python_signals = [
        r'\bdef\s+\w+\s*\(', r'\bclass\s+\w+', r'\bimport\s+\w+',
        r'\bfor\s+\w+\s+in\b', r'\bwhile\s+.+:', r'\bif\s+.+:',
        r'\bprint\s*\(', r'\breturn\b', r'=\s*\[', r'=\s*\{',
    ]
    if any(re.search(p, stripped) for p in python_signals):
        return "python"
    return "question"


def _wrap_data_as_code(text: str, kind: str) -> str:
    if kind == "json":
        return (
            f"import json\ndata = json.loads({repr(text)})\n"
            "print('Type:', type(data).__name__)\n"
            "print('Value:', data)\n"
            "if isinstance(data, dict):\n"
            "    print('Keys:', list(data.keys()))\n"
            "    for k, v in data.items():\n"
            "        print(f'  {k}: {v} ({type(v).__name__})')\n"
            "elif isinstance(data, list):\n"
            "    print('Length:', len(data))\n"
        )
    return (
        f"data = {text}\n"
        "print('Type:', type(data).__name__)\n"
        "print('Value:', data)\n"
        "if isinstance(data, dict):\n"
        "    print('Keys:', list(data.keys()))\n"
        "    for k, v in data.items():\n"
        "        print(f'  {k}: {v} ({type(v).__name__})')\n"
        "elif isinstance(data, list):\n"
        "    print('Length:', len(data))\n"
    )


# -----------------------------------
# HELPER: extract line number from traceback
# Same pattern as Week 3 structured_tutor_response.py
# -----------------------------------

def _extract_line_number(traceback_text: str) -> int:
    if not traceback_text:
        return 0
    matches = re.findall(r"\bline\s+(\d+)", traceback_text)
    return int(matches[-1]) if matches else 0


# -----------------------------------
# TOOL: run_python
#
# Week 4 adds:
#   - input() mocking (UX — students paste interactive code)
#   - dict/JSON wrapping (UX — students paste data structures)
#   - auto-install missing packages (UX — students use third-party libs)
#   - line number extraction from RunResult (UX — cite the failing line)
#
# Security (AST visitor, memory limit, subprocess isolation, path
# normalisation) is entirely delegated to Week 2 run_python_safely().
#
# Fallback: if Week 2 is not available, runs a minimal subprocess
# sandbox (timeout only — no AST security). A warning is logged.
# -----------------------------------

def run_python(code: str) -> dict:

    if not code or not code.strip():
        return {"success": False, "error": "No Python code was provided."}

    # Line limit
    lines = code.splitlines()
    if len(lines) > MAX_CODE_LINES:
        return {
            "success": False,
            "error": (
                f"Code is {len(lines)} lines — the limit is {MAX_CODE_LINES}. "
                "Consider breaking it into smaller sections."
            )
        }

    # Classify and optionally wrap data input
    kind = _classify_input(code)
    note = None
    if kind in ("dict", "json"):
        code = _wrap_data_as_code(code, kind)
        note = f"Input detected as {kind.upper()} — wrapped in Python to analyse it."

    # Auto-install missing packages before execution
    _install_missing_packages(code)

    # Mock input() calls so interactive programs don't hang
    input_mocked = _has_input_calls(code)
    if input_mocked:
        code = _inject_input_mock(code)

    # ── Delegate to Week 2 sandbox ─────────────────────────────────────────
    if _WEEK2_AVAILABLE:
        result: RunResult = run_python_safely(
            code,
            timeout_s=TIMEOUT_SECONDS,
            user_input="",
        )

        # Security violation — Week 2 AST caught it
        if result.error_type == "SecurityViolation":
            return {
                "success": False,
                "blocked": True,
                "error": (
                    f"Security violation: {result.error_message}\n"
                    "This operation is blocked to protect the tutor environment."
                )
            }

        line_number = _extract_line_number(result.output)

        if result.ok:
            return {
                "success":      True,
                "stdout":       result.output,
                "stderr":       "",
                "returncode":   0,
                "input_mocked": input_mocked,
                "line_number":  0,
                "note":         note,
            }

        return {
            "success":      False,
            "stdout":       "",
            "stderr":       result.output,
            "returncode":   1,
            "error_type":   result.error_type,
            "error_message": result.error_message,
            "input_mocked": input_mocked,
            "line_number":  line_number,
            "note":         note,
        }

    # ── Fallback: Week 2 not found — minimal subprocess sandbox ───────────
    # No AST security. Logs a warning so the developer notices.
    import tempfile, platform
    print(
        "[WARNING] safe_python_runner.py not found — running without AST "
        "security. Place it in the same folder as week4_mini_tutor.py.",
        file=sys.stderr
    )

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "code.py"
        script.write_text(code, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True,
                timeout=TIMEOUT_SECONDS, cwd=tmp
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False, "error_type": "TimeoutError",
                "error_message": "Program exceeded time limit. Possible infinite loop.",
                "line_number": 0, "input_mocked": input_mocked
            }

    line_number = _extract_line_number(proc.stderr)
    if proc.returncode == 0:
        return {
            "success": True, "stdout": proc.stdout.strip(),
            "stderr": "", "returncode": 0,
            "input_mocked": input_mocked, "line_number": 0, "note": note
        }

    stderr = proc.stderr.strip()
    error_type, error_message = "RuntimeError", stderr
    if ": " in (stderr.splitlines() or [""])[-1]:
        last = stderr.splitlines()[-1]
        parts = last.split(": ", 1)
        error_type, error_message = parts[0], parts[1]

    return {
        "success": False, "stdout": "", "stderr": stderr, "returncode": 1,
        "error_type": error_type, "error_message": error_message,
        "input_mocked": input_mocked, "line_number": line_number, "note": note
    }


# -----------------------------------
# TOOL: lint_code
#
# Delegates entirely to Week 3 tool_dispatcher.dispatch("lint_code").
# Fallback: calls ruff directly if Week 3 is not available.
# -----------------------------------

def lint_code(code: str, select: str = "E,F,W") -> dict:
    if not code or not code.strip():
        return {"success": False, "error": "No code provided to lint."}

    # ── Delegate to Week 3 dispatcher ─────────────────────────────────────
    if _WEEK3_AVAILABLE:
        raw = _w3_dispatch("lint_code", {"code": code, "select": select})
        try:
            result = json.loads(raw)
            return result
        except (json.JSONDecodeError, TypeError):
            # Week 3 returns a plain string — wrap it
            return {"success": True, "summary": raw, "issue_count": -1}

    # ── Fallback: call ruff directly ───────────────────────────────────────
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        proc = subprocess.run(
            ["ruff", "check", "--select", select, tmp_path],
            capture_output=True, text=True, timeout=10
        )
        os.remove(tmp_path)

        output = re.sub(r"[^\s]+\.py:", "Line ", proc.stdout.strip())
        if not output:
            return {"success": True, "summary": "No lint issues found.", "issue_count": 0}
        return {"success": True, "summary": output, "issue_count": output.count("\n") + 1}

    except FileNotFoundError:
        return {"success": False, "error": "ruff not installed. Run: pip install ruff"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# -----------------------------------
# TOOL: doc_search
#
# Delegates entirely to Week 3 tool_dispatcher.dispatch("doc_search").
# Fallback: returns a direct docs.python.org search URL.
# -----------------------------------

def doc_search(keyword: str, version: str = "3", max_results: int = 3) -> dict:
    if not keyword or not keyword.strip():
        return {"success": False, "error": "No keyword provided."}

    # ── Delegate to Week 3 dispatcher ─────────────────────────────────────
    if _WEEK3_AVAILABLE:
        raw = _w3_dispatch("doc_search", {
            "keyword": keyword,
            "version": version,
            "max_results": max_results
        })
        try:
            result = json.loads(raw)
            return result
        except (json.JSONDecodeError, TypeError):
            return {"success": True, "summary": raw}

    # ── Fallback: return search URL directly ───────────────────────────────
    import urllib.parse
    url = (
        f"https://docs.python.org/{version}/search.html?"
        + urllib.parse.urlencode({"q": keyword})
    )
    return {
        "success": True,
        "summary": (
            f"Python {version} docs for '{keyword}':\n{url}\n"
            "(Week 3 tool_dispatcher not found — showing direct URL)"
        )
    }


# -----------------------------------
# TOOL REGISTRY
# -----------------------------------

TOOL_FUNCTIONS = {
    "run_python": run_python,
    "lint_code":  lint_code,
    "doc_search": doc_search,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute a Python code snippet and return its output. "
                "Pass the ENTIRE code as the single 'code' string — "
                "do NOT pass any other arguments. "
                "Interactive programs are handled automatically. "
                "Missing packages are installed automatically. "
                "Returns stdout, stderr, and the failing line number. "
                f"Maximum {MAX_CODE_LINES} lines. "
                "ALWAYS call this first when the student submits code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "The complete Python code to run, as a single string. "
                            "This is the ONLY parameter — never pass 'input', "
                            "'stdin', 'timeout', or any other argument."
                        )
                    }
                },
                "required": ["code"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lint_code",
            "description": (
                "Check Python code for style issues, unused variables, and "
                "common mistakes using ruff. Does NOT execute the code. "
                "Use when student asks about code quality or best practices."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code":   {"type": "string", "description": "Python code to lint."},
                    "select": {"type": "string", "description": "Ruff rules e.g. 'E,F,W'. Default E,F,W."}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "doc_search",
            "description": (
                "Search the official Python documentation by keyword. "
                "Use when student asks how a built-in function, module, "
                "or language feature works."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword":     {"type": "string",  "description": "Concept to look up e.g. 'enumerate'."},
                    "version":     {"type": "string",  "description": "Python version. Default '3'."},
                    "max_results": {"type": "integer", "description": "Max results. Default 3."}
                },
                "required": ["keyword"]
            }
        }
    },
]


# -----------------------------------
# TOOL EXECUTOR
# Validates args, drops unknown keys, never raises.
# -----------------------------------

def execute_tool(tool_name: str, tool_input: dict) -> str:
    import inspect

    # Model sometimes passes a list [{arg1}, {arg2}] — merge into one dict
    if isinstance(tool_input, list):
        merged = {}
        for item in tool_input:
            if isinstance(item, dict):
                merged.update(item)
        tool_input = merged

    if not isinstance(tool_input, dict):
        tool_input = {}

    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({
            "success": False,
            "error": (
                f"Unknown tool '{tool_name}'. "
                f"Available: {list(TOOL_FUNCTIONS.keys())}"
            )
        })

    # Drop invented args the function doesn't accept
    fn     = TOOL_FUNCTIONS[tool_name]
    params = set(inspect.signature(fn).parameters.keys())
    clean  = {k: v for k, v in tool_input.items() if k in params}

    try:
        return json.dumps(fn(**clean))
    except TypeError as exc:
        return json.dumps({"success": False, "error": f"Wrong arguments: {exc}"})
    except Exception as exc:
        return json.dumps({"success": False, "error": f"Tool crashed: {exc}"})


# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------

_w2_status = "✓ active (AST security, memory limit, subprocess isolation)" if _WEEK2_AVAILABLE else "✗ NOT FOUND — fallback mode (no AST security)"
_w3_status = "✓ active (ruff linter, Python docs search)" if _WEEK3_AVAILABLE else "✗ NOT FOUND — fallback mode"

SYSTEM_PROMPT = f"""You are Mini-Tutor, a patient AI coding tutor for Python learners.
Your goal is to help students UNDERSTAND bugs — never to write fixes for them.

SANDBOX STATUS:
- Week 2 security sandbox: {_w2_status}
- Week 3 tools (lint/docs): {_w3_status}

TOOL CALLING RULES:
- run_python takes EXACTLY ONE argument: "code". Nothing else.
- Never pass "input", "stdin", "timeout", or any other argument.
- Always pass a single JSON object: {{"code": "..."}}
- exec() and eval() are blocked in the sandbox.

TUTOR RULES:
1. When a student submits code, ALWAYS call run_python first.
2. The result includes "line_number" — always cite it in Diagnosis.
3. NEVER reveal the corrected code. One Socratic question per reply.
4. Structure every reply EXACTLY like this:

Diagnosis: (one sentence — what is wrong, citing the exact line number)
Question: (one guiding question pointing toward the issue)
Next Step: (one small concrete action)

5. If code runs but output is wrong, ask what the student expected.
6. Use doc_search when student is confused about a concept.
7. Use lint_code when code runs but quality could be improved.
8. Tone: warm, encouraging, never condescending.
9. Maximum {MAX_TOOL_CALLS} tool calls per turn.
10. Use plain text labels — no ** markdown bold **."""


# -----------------------------------
# AGENT LOOP
# Unchanged from previous version — this is Week 4's own concern.
# -----------------------------------

def run_tutor_agent(
    student_message: str,
    conversation_history: list = None
) -> tuple:

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return (
            "Configuration error: GROQ_API_KEY is missing from your .env file.\n"
            "Create a .env file with: GROQ_API_KEY=your_key_here",
            conversation_history or []
        )

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    if conversation_history is None:
        conversation_history = []

    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + conversation_history
        + [{"role": "user", "content": student_message}]
    )

    tool_call_count = 0
    final_reply     = ""

    while True:
        response   = None
        last_error = ""

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    max_tokens=1500,
                    tools=TOOL_SCHEMAS,
                    messages=messages
                )
                break
            except Exception as exc:
                exc_str = str(exc).lower()

                if "401" in exc_str or "authentication" in exc_str or "api key" in exc_str:
                    return ("Authentication failed — check your GROQ_API_KEY in .env.", messages[1:])

                if "model" in exc_str and ("not found" in exc_str or "deprecated" in exc_str):
                    return (f"Model '{GROQ_MODEL}' is unavailable. Update GROQ_MODEL in config.", messages[1:])

                if "400" in exc_str or "tool_use_failed" in exc_str or "tool call validation" in exc_str:
                    return (
                        "I had trouble processing that input. "
                        "This sometimes happens with exec(), eval(), or complex escape sequences.\n\n"
                        "Try rephrasing, or paste just the relevant snippet.",
                        messages[1:]
                    )

                is_retryable = (
                    "429" in exc_str or "rate limit" in exc_str
                    or any(t in exc_str for t in ("connection", "timeout", "network"))
                )
                if is_retryable and attempt <= MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_S * attempt)
                    last_error = str(exc)
                    continue

                return (f"API call failed: {exc}", messages[1:])

        if response is None:
            return (f"API call failed after retries: {last_error}", messages[1:])

        choice  = response.choices[0]
        message = choice.message
        finish  = choice.finish_reason

        # Convert SDK object → plain dict (prevents 400 on subsequent turns)
        assistant_dict: dict = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id":       tc.id,
                    "type":     "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in message.tool_calls
            ]
        messages.append(assistant_dict)

        if finish in ("stop", "length"):
            final_reply = message.content or ""
            break

        if finish == "tool_calls" and message.tool_calls:
            for tc in message.tool_calls:
                tool_call_count += 1
                if tool_call_count > MAX_TOOL_CALLS:
                    result_content = json.dumps({"success": False, "error": "Tool call limit reached."})
                else:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    result_content = execute_tool(tc.function.name, args)

                messages.append({
                    "role": "tool", "tool_call_id": tc.id, "content": result_content
                })
        else:
            final_reply = "I ran into an unexpected state. Please try submitting your code again."
            break

    updated_history = messages[1:]
    return final_reply, updated_history


# -----------------------------------
# STARTUP: report which weeks are loaded
# -----------------------------------

def _print_startup_status() -> None:
    print("\n" + "=" * 55)
    print("  MINI-TUTOR v2  —  Week 2+3+4 Integration")
    print("=" * 55)
    w2 = "✓ Week 2 sandbox (AST security)" if _WEEK2_AVAILABLE else "✗ Week 2 NOT FOUND — fallback mode"
    w3 = "✓ Week 3 tools (lint, doc_search)" if _WEEK3_AVAILABLE else "✗ Week 3 NOT FOUND — fallback mode"
    print(f"  {w2}")
    print(f"  {w3}")
    print("=" * 55)


# -----------------------------------
# CLI ENTRY POINT
# -----------------------------------

if __name__ == "__main__":
    _print_startup_status()
    print("  Type 'quit' to exit.\n")

    history = []
    while True:
        print("\nPaste your Python code, a dict, or a question.")
        print("Press ENTER twice to submit.\n")

        lines, blank_count = [], 0
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.lower().strip() == "quit":
                print("\nGoodbye! Keep coding.")
                sys.exit(0)
            if line == "":
                blank_count += 1
            else:
                blank_count = 0
            if blank_count == 2:
                break
            lines.append(line)

        student_input = "\n".join(lines).strip()
        if not student_input:
            print("Nothing entered — try again.")
            continue

        print("\n[Tutor is thinking...]\n")
        reply, history = run_tutor_agent(student_input, history)
        print("-" * 55)
        print("TUTOR:\n")
        print(reply)
        print("-" * 55)