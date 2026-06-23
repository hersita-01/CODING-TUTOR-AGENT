# -----------------------------------
# WEEK 4 - MINI-TUTOR v2
# CORE AGENT  —  GROQ API
# -----------------------------------
#
# Architecture: calls Week 2 and Week 3 instead of reimplementing them.
#
# Week 2  safe_python_runner.py
#   └─ run_python_safely()     ← execution sandbox (AST security, timeout,
#   └─ RunResult               ← memory limit, subprocess isolation)
#
# Week 3  tool_dispatcher.py
#   └─ dispatch()              ← routes lint_code and doc_search tool calls
#
# Week 4  week4_mini_tutor.py  (this file)
#   └─ run_python()            ← thin wrapper: input mock + auto-install
#                                 then calls run_python_safely()
#   └─ lint_code()             ← delegates to Week 3 dispatch("lint_code")
#   └─ doc_search()            ← delegates to Week 3 dispatch("doc_search")
#   └─ run_tutor_agent()       ← ReAct loop
#
# What this file does NOT reimplement:
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
#            safe_python_runner.py in same folder or week2-prompt-engineering/day3-socratic/
#            tool_dispatcher.py   in same folder or week3-tool-use/day3-tool-loop/
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

import inspect
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, TypedDict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ============================================================
# LOGGING
# Internal diagnostics only — user-facing CLI output uses print().
# ============================================================

logging.basicConfig(
    level=logging.WARNING,
    format="[%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("week4_mini_tutor")


# ============================================================
# CONFIGURATION  (all constants live in config.py)
# ============================================================

from config import (
    GROQ_MODEL,
    MAX_CODE_LINES,
    MAX_RETRIES,
    MAX_TOOL_CALLS,
    RETRY_BACKOFF_S,
    TIMEOUT_SECONDS,
)


# ============================================================
# PATH SETUP — cross-folder imports
# Supports any working directory; same pattern used in Week 3 files.
# ============================================================

def _add_to_path(candidates: list[Path]) -> None:
    """Prepend existing directories to sys.path (once each)."""
    for candidate in candidates:
        if candidate.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


_here = Path(__file__).resolve().parent   # CODING-TUTOR-AGENT/week4_mini_tutor/
_root = _here.parent                      # CODING-TUTOR-AGENT/

# safe_python_runner.py
# Primary:  week2-prompt-engineering/day3-socratic/
# Fallback: week3-tool-use/shared/ or same folder
_add_to_path([
    _root / "week2-prompt-engineering" / "day3-socratic",
    _root / "week3-tool-use" / "shared",
    _here,
])

# tool_dispatcher.py + tool_schemas.py
_add_to_path([_root / "week3-tool-use" / "day3-tool-loop"])

# lint_tool.py + doc_search_tool.py
_add_to_path([_root / "week3-tool-use" / "day4-more-tools"])


# ============================================================
# WEEK 2 INTEGRATION — secure Python execution sandbox
# ============================================================

try:
    from safe_python_runner import RunResult, run_python_safely
    _WEEK2_AVAILABLE = True
    log.debug("Week 2 sandbox loaded.")
except ImportError:
    _WEEK2_AVAILABLE = False
    log.warning(
        "safe_python_runner.py not found — running without AST security. "
        "Place it in the same folder as week4_mini_tutor.py."
    )


# ============================================================
# WEEK 3 INTEGRATION — lint and doc-search tools
# ============================================================

try:
    from tool_dispatcher import dispatch as _w3_dispatch
    _WEEK3_AVAILABLE = True
    log.debug("Week 3 tool dispatcher loaded.")
except ImportError:
    _WEEK3_AVAILABLE = False
    log.warning("tool_dispatcher.py not found — fallback mode for lint/doc_search.")


# ============================================================
# SYSTEM PROMPT  (content lives in prompts.py)
# ============================================================

from prompts import build_system_prompt

SYSTEM_PROMPT: str = build_system_prompt(_WEEK2_AVAILABLE, _WEEK3_AVAILABLE)


# ============================================================
# TYPED RESULT SHAPES
# Shared by run_python(), lint_code(), doc_search() so callers
# can rely on a stable contract instead of bare dicts.
# ============================================================

class RunPythonResult(TypedDict, total=False):
    success: bool
    stdout: str
    stderr: str
    returncode: int
    error_type: str
    error_message: str
    input_mocked: bool
    line_number: int
    note: str | None
    blocked: bool
    error: str


class LintResult(TypedDict, total=False):
    success: bool
    summary: str
    issue_count: int
    error: str


class DocResult(TypedDict, total=False):
    success: bool
    summary: str
    error: str


# ============================================================
# HELPER — stdlib module set  (never pip-install these)
# ============================================================

_STDLIB_MODULES: frozenset[str] = frozenset({
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
})

_IMPORT_RE   = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE)
_VALID_PKG   = re.compile(r'^[a-zA-Z0-9_\-\.]{1,100}$')
_INPUT_RE    = re.compile(r'\binput\s*\(')
_LINE_NUM_RE = re.compile(r'\bline\s+(\d+)')


# ============================================================
# HELPER — auto-install missing third-party packages
# Package names are validated against PyPI naming rules before
# installation to prevent arbitrary shell injection.
# ============================================================

def _install_missing_packages(code: str) -> list[str]:
    """Attempt to pip-install any imported package not in the stdlib.

    Returns the list of package names that were installed.
    """
    found    = set(_IMPORT_RE.findall(code))
    external = [p for p in found if p not in _STDLIB_MODULES and _VALID_PKG.match(p)]

    installed: list[str] = []
    for pkg in external:
        try:
            __import__(pkg)
        except ImportError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--", pkg, "-q"],
                    capture_output=True, timeout=30,
                )
                installed.append(pkg)
                log.info("Auto-installed package: %s", pkg)
            except Exception as exc:
                log.warning("Could not install %s: %s", pkg, exc)
    return installed


# ============================================================
# HELPER — mock input() calls
# Injected as a preamble so interactive programs don't hang.
# This is a Week 4 UX concern, not a security concern — the
# sandbox in Week 2 handles security independently.
# ============================================================

_INPUT_MOCK_PREAMBLE = """\
import builtins as _builtins
_input_call_count = 0
_INPUT_RESPONSES = [
    "5", "10", "1000", "1", "2", "3", "500", "0", "-1", "6",
    "yes", "no", "quit", "exit", "hello", "world", "Alice", "Bob", "test",
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

# Lines injected by the preamble — subtracted from reported line numbers
# so the tutor always cites the student's original line, not the offset line.
_INPUT_MOCK_LINE_OFFSET: int = _INPUT_MOCK_PREAMBLE.count("\n")


def _has_input_calls(code: str) -> bool:
    return bool(_INPUT_RE.search(code))


def _inject_input_mock(code: str) -> str:
    return _INPUT_MOCK_PREAMBLE + code


# ============================================================
# HELPER — classify student input type
# Distinguishes JSON, Python dict literals, Python code, and
# plain questions so each can be handled appropriately.
# ============================================================

def _classify_input(text: str) -> str:
    """Return one of: 'json', 'dict', 'python', 'question'."""
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
    """Return runnable Python that parses and pretty-prints a data literal."""
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


# ============================================================
# HELPER — extract line number from a traceback string
# ============================================================

def _extract_line_number(traceback_text: str, offset: int = 0) -> int:
    """Return the last 'line N' value in a traceback, or 0 if none.

    Parameters
    ----------
    traceback_text:
        Raw stderr / traceback string from the sandbox.
    offset:
        Number of injected lines to subtract from the result so the
        reported line always refers to the student's original code.
        Pass _INPUT_MOCK_LINE_OFFSET when input() was mocked.
    """
    if not traceback_text:
        return 0
    matches = _LINE_NUM_RE.findall(traceback_text)
    if not matches:
        return 0
    raw_line = int(matches[-1])
    corrected = raw_line - offset
    return max(corrected, 1)  # never report line 0 or negative


# ============================================================
# TOOL WRAPPERS
# Each function is a thin Week-4 adapter that adds student-UX
# features (input mocking, data wrapping, auto-install) then
# delegates all heavy lifting to Week 2 or Week 3.
# ============================================================

def run_python(code: str) -> RunPythonResult:
    """Execute a Python snippet inside the Week 2 sandbox.

    Week 4 additions before delegating to run_python_safely():
    - Rejects empty input and over-long snippets.
    - Detects JSON/dict input and wraps it in runnable Python.
    - Auto-installs missing third-party packages.
    - Injects an input() mock so interactive programs don't hang.

    Security (AST visitor, memory cap, subprocess isolation) is
    entirely handled by Week 2.  The fallback subprocess path is
    used only when safe_python_runner.py cannot be found.
    """
    if not code or not code.strip():
        return {"success": False, "error": "No Python code was provided."}

    lines = code.splitlines()
    if len(lines) > MAX_CODE_LINES:
        return {
            "success": False,
            "error": (
                f"Code is {len(lines)} lines — the limit is {MAX_CODE_LINES}. "
                "Consider breaking it into smaller sections."
            ),
        }

    # Classify and optionally wrap data input
    kind = _classify_input(code)
    note: str | None = None
    if kind in ("dict", "json"):
        code = _wrap_data_as_code(code, kind)
        note = f"Input detected as {kind.upper()} — wrapped in Python to analyse it."

    _install_missing_packages(code)

    input_mocked = _has_input_calls(code)
    if input_mocked:
        code = _inject_input_mock(code)

    # ── Delegate to Week 2 sandbox ──────────────────────────────────────────
    if _WEEK2_AVAILABLE:
        result: RunResult = run_python_safely(code, timeout_s=TIMEOUT_SECONDS, user_input="")

        if result.error_type == "SecurityViolation":
            return {
                "success": False,
                "blocked": True,
                "error": (
                    f"Security violation: {result.error_message}\n"
                    "This operation is blocked to protect the tutor environment."
                ),
            }

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
            "success":       False,
            "stdout":        "",
            "stderr":        result.output,
            "returncode":    1,
            "error_type":    result.error_type,
            "error_message": result.error_message,
            "input_mocked":  input_mocked,
            "line_number":   _extract_line_number(
                result.output,
                offset=_INPUT_MOCK_LINE_OFFSET if input_mocked else 0,
            ),
            "note":          note,
        }

    # ── Fallback: Week 2 not found — minimal subprocess sandbox ────────────
    # Timeout-only; no AST security.  Developer sees a WARNING in the logs.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "code.py"
        script.write_text(code, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True,
                timeout=TIMEOUT_SECONDS, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {
                "success":       False,
                "error_type":    "TimeoutError",
                "error_message": "Program exceeded time limit. Possible infinite loop.",
                "line_number":   0,
                "input_mocked":  input_mocked,
            }

    if proc.returncode == 0:
        return {
            "success":      True,
            "stdout":       proc.stdout.strip(),
            "stderr":       "",
            "returncode":   0,
            "input_mocked": input_mocked,
            "line_number":  0,
            "note":         note,
        }

    stderr = proc.stderr.strip()
    # Best-effort parse of "ErrorType: message" from the traceback.
    # Scan ALL lines (not just the last) for a token that looks like a real
    # Python exception class name (CamelCase + "Error"/"Warning"/"Exception"/etc.)
    # so that "File '...', line N" lines are never misread as the error type.
    _EXC_LINE_RE = re.compile(
        r'^([A-Z][a-zA-Z0-9_]*(?:Error|Warning|Exception|Interrupt|Exit|Stop))\s*:\s*(.*)'
    )
    error_type, error_message = "RuntimeError", stderr
    for _line in reversed((stderr.splitlines() or [""])):
        _m = _EXC_LINE_RE.match(_line.strip())
        if _m:
            error_type, error_message = _m.group(1), _m.group(2)
            break

    return {
        "success":       False,
        "stdout":        "",
        "stderr":        stderr,
        "returncode":    1,
        "error_type":    error_type,
        "error_message": error_message,
        "input_mocked":  input_mocked,
        "line_number":   _extract_line_number(
            stderr,
            offset=_INPUT_MOCK_LINE_OFFSET if input_mocked else 0,
        ),
        "note":          note,
    }


def lint_code(code: str, select: str = "E,F,W") -> LintResult:
    """Check Python code quality via Week 3 (or ruff directly as fallback)."""
    if not code or not code.strip():
        return {"success": False, "error": "No code provided to lint."}

    # ── Delegate to Week 3 dispatcher ──────────────────────────────────────
    if _WEEK3_AVAILABLE:
        raw = _w3_dispatch("lint_code", {"code": code, "select": select})
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            # Week 3 returned a plain string — normalise to our shape
            return {"success": True, "summary": raw, "issue_count": -1}

    # ── Fallback: call ruff directly ────────────────────────────────────────
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        proc = subprocess.run(
            ["ruff", "check", "--select", select, tmp_path],
            capture_output=True, text=True, timeout=10,
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


def doc_search(keyword: str, version: str = "3", max_results: int = 3) -> DocResult:
    """Search the Python docs via Week 3 (or return a direct URL as fallback)."""
    if not keyword or not keyword.strip():
        return {"success": False, "error": "No keyword provided."}

    # ── Delegate to Week 3 dispatcher ──────────────────────────────────────
    if _WEEK3_AVAILABLE:
        raw = _w3_dispatch("doc_search", {
            "keyword": keyword,
            "version": version,
            "max_results": max_results,
        })
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"success": True, "summary": raw}

    # ── Fallback: return a direct docs.python.org search URL ───────────────
    url = (
        f"https://docs.python.org/{version}/search.html?"
        + urllib.parse.urlencode({"q": keyword})
    )
    return {
        "success": True,
        "summary": (
            f"Python {version} docs for '{keyword}':\n{url}\n"
            "(Week 3 tool_dispatcher not found — showing direct URL)"
        ),
    }


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOL_FUNCTIONS: dict[str, Any] = {
    "run_python": run_python,
    "lint_code":  lint_code,
    "doc_search": doc_search,
}

TOOL_SCHEMAS: list[dict] = [
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
                        ),
                    }
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        },
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
                    "select": {"type": "string", "description": "Ruff rules e.g. 'E,F,W'. Default E,F,W."},
                },
                "required": ["code"],
            },
        },
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
                    "max_results": {"type": "integer", "description": "Max results. Default 3."},
                },
                "required": ["keyword"],
            },
        },
    },
]


# ============================================================
# TOOL EXECUTOR
# Validates and normalises args before dispatching.
# Never raises — errors are returned as JSON for the agent.
# ============================================================

def execute_tool(tool_name: str, tool_input: Any) -> str:
    """Validate, sanitise, and dispatch a tool call from the agent loop.

    Returns a JSON string in all cases so the agent always gets a
    well-formed tool result message.
    """
    # Model sometimes passes a list of dicts instead of a single dict — merge them.
    if isinstance(tool_input, list):
        merged: dict = {}
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
            ),
        })

    # Drop any arguments the function doesn't declare, so the model can't inject
    # unexpected kwargs even if it hallucinates extra parameters.
    fn     = TOOL_FUNCTIONS[tool_name]
    params = set(inspect.signature(fn).parameters.keys())
    clean  = {k: v for k, v in tool_input.items() if k in params}

    try:
        return json.dumps(fn(**clean))
    except TypeError as exc:
        return json.dumps({"success": False, "error": f"Wrong arguments: {exc}"})
    except Exception as exc:
        return json.dumps({"success": False, "error": f"Tool crashed: {exc}"})


# ============================================================
# AGENT LOOP — ReAct pattern
# This is Week 4's own responsibility and is not delegated
# to Week 2 or Week 3.
# ============================================================

def run_tutor_agent(
    student_message: str,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    """Run one student turn through the ReAct agent loop.

    Parameters
    ----------
    student_message:
        The raw text submitted by the student.
    conversation_history:
        All prior turns (excluding the system prompt), mutated and returned.

    Returns
    -------
    (reply, updated_history)
        reply:           The tutor's final text response.
        updated_history: Full conversation minus the system prompt.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return (
            "Configuration error: GROQ_API_KEY is missing from your .env file.\n"
            "Create a .env file with: GROQ_API_KEY=your_key_here",
            conversation_history or [],
        )

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    if conversation_history is None:
        conversation_history = []

    messages: list[dict] = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + conversation_history
        + [{"role": "user", "content": student_message}]
    )

    tool_call_count = 0
    final_reply     = ""

    while True:
        response   = None
        last_error = ""

        # ── API call with retry ─────────────────────────────────────────────
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    max_tokens=1500,
                    tools=TOOL_SCHEMAS,
                    messages=messages,
                )
                break
            except Exception as exc:
                exc_str = str(exc).lower()

                if "401" in exc_str or "authentication" in exc_str or "api key" in exc_str:
                    return (
                        "Authentication failed — check your GROQ_API_KEY in .env.",
                        messages[1:],
                    )

                if "model" in exc_str and ("not found" in exc_str or "deprecated" in exc_str):
                    return (
                        f"Model '{GROQ_MODEL}' is unavailable. Update GROQ_MODEL in config.py.",
                        messages[1:],
                    )

                if "400" in exc_str or "tool_use_failed" in exc_str or "tool call validation" in exc_str:
                    return (
                        "I had trouble processing that input. "
                        "This sometimes happens with exec(), eval(), or complex escape sequences.\n\n"
                        "Try rephrasing, or paste just the relevant snippet.",
                        messages[1:],
                    )

                is_retryable = (
                    "429" in exc_str or "rate limit" in exc_str
                    or any(t in exc_str for t in ("connection", "timeout", "network"))
                )
                if is_retryable and attempt <= MAX_RETRIES:
                    log.warning("Retryable API error (attempt %d): %s", attempt, exc)
                    time.sleep(RETRY_BACKOFF_S * attempt)
                    last_error = str(exc)
                    continue

                return (f"API call failed: {exc}", messages[1:])

        if response is None:
            return (f"API call failed after retries: {last_error}", messages[1:])

        # ── Process response ────────────────────────────────────────────────
        choice  = response.choices[0]
        message = choice.message
        finish  = choice.finish_reason

        # Convert SDK object → plain dict to avoid 400 errors on subsequent turns.
        assistant_dict: dict = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id":       tc.id,
                    "type":     "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
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
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_content,
                })
        else:
            final_reply = "I ran into an unexpected state. Please try submitting your code again."
            break

    # Strip the system prompt before returning so history stays clean.
    return final_reply, messages[1:]


# ============================================================
# CLI — startup banner and interactive REPL
# ============================================================

def _print_startup_status() -> None:
    w2 = "✓ Week 2 sandbox (AST security)" if _WEEK2_AVAILABLE else "✗ Week 2 NOT FOUND — fallback mode"
    w3 = "✓ Week 3 tools (lint, doc_search)" if _WEEK3_AVAILABLE else "✗ Week 3 NOT FOUND — fallback mode"
    print("\n" + "=" * 55)
    print("  MINI-TUTOR v2  —  Week 2+3+4 Integration")
    print("=" * 55)
    print(f"  {w2}")
    print(f"  {w3}")
    print("=" * 55)


if __name__ == "__main__":
    _print_startup_status()
    print("  Type 'quit' to exit.\n")

    history: list[dict] = []
    while True:
        print("\nPaste your Python code, a dict, or a question.")
        print("Press ENTER twice to submit.\n")

        lines: list[str] = []
        blank_count = 0
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