"""
week3-tool-use/day3-tool-loop/tool_dispatcher.py

Day 3 — Tool Dispatcher

Single responsibility: receive a tool name and arguments from the model,
route to the correct implementation, and return a plain string result.

This is the switchboard between the LLM and the actual tool implementations.

Rules this file follows:
  1. NEVER raises exceptions to the caller — all errors become result strings
  2. NEVER executes student code itself — delegates to safe_python_runner
  3. NEVER imports tool implementations at module level that might fail
     (ruff not installed, network down) — imports happen inside each handler
  4. Always returns a non-empty string the model can read as a tool_result

Reuses from Week 2:
  - run_python_safely()  — the entire execution sandbox
  - RunResult dataclass  — structured result object
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# IMPORT safe_python_runner from Week 2
# Supports being called from any working directory.
# ---------------------------------------------------------------------------

def _bootstrap() -> None:
    this_dir = Path(__file__).resolve().parent
    candidates = [
        this_dir,                                    # same folder
        this_dir.parent / "day3-socratic",           # week2 day3 location
        this_dir.parent.parent / "week2-prompt-engineering" / "day3-socratic",
        this_dir.parent / "shared",                  # shared folder
    ]
    for candidate in candidates:
        if (candidate / "safe_python_runner.py").exists():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return

_bootstrap()

try:
    from safe_python_runner import run_python_safely, RunResult
except ImportError as _err:
    print(f"ERROR: Cannot import safe_python_runner: {_err}")
    print("Place safe_python_runner.py in the same folder or in 'shared/'")
    sys.exit(1)

from tool_schemas import KNOWN_TOOL_NAMES


# ---------------------------------------------------------------------------
# RESULT FORMATTER
#
# Converts a RunResult from Week 2 into a plain string the LLM can read.
# The model sees this string as the tool_result content.
# ---------------------------------------------------------------------------

def format_run_result(result: RunResult) -> str:
    """
    Convert a Week 2 RunResult into a readable string for the LLM.

    The model needs to see:
    - Whether execution succeeded
    - The actual output (stdout)
    - The error type and message if it failed
    - The full traceback for line-number context
    """
    if result.error_type == "SecurityViolation":
        return (
            "SECURITY VIOLATION\n"
            f"{result.error_message}\n"
            "This operation is blocked by the tutor sandbox. "
            "Explain to the student why this operation is not permitted."
        )

    if result.ok:
        if result.output:
            return f"Execution successful.\nOutput:\n{result.output}"
        return "Execution successful. No output was produced (no print statements)."

    # Error case — include everything the model needs
    parts = [
        f"Execution failed.",
        f"Error Type    : {result.error_type}",
        f"Error Message : {result.error_message}",
    ]
    if result.output:
        parts.append(f"Full Traceback:\n{result.output}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# TOOL HANDLERS
# Each handler validates its own arguments and returns a string.
# Exceptions are caught inside the handler — never propagated.
# ---------------------------------------------------------------------------

def _handle_run_python(args: dict) -> str:
    """
    Route run_python tool call to safe_python_runner from Week 2.
    Validates arguments before calling the sandbox.
    """
    code = args.get("code", "").strip()
    if not code:
        return "Error: run_python requires a non-empty 'code' argument."

    timeout_s  = int(args.get("timeout_s", 3))
    user_input = args.get("user_input", "")

    # Cap timeout — never allow more than 10 seconds
    timeout_s = min(max(timeout_s, 1), 10)

    # Delegate entirely to Week 2 sandbox
    result = run_python_safely(
        code       = code,
        timeout_s  = timeout_s,
        user_input = user_input,
    )

    return format_run_result(result)


def _handle_lint_code(args: dict) -> str:
    """
    Route lint_code tool call to ruff via subprocess.
    Returns structured lint warnings the model can explain to the student.
    """
    import subprocess
    import tempfile

    code = args.get("code", "").strip()
    if not code:
        return "Error: lint_code requires a non-empty 'code' argument."

    select = args.get("select", "E,F,W")

    # Write code to temp file — ruff works on files not stdin
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        result = subprocess.run(
            ["ruff", "check", "--select", select, "--output-format", "text", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        import os
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        # Ruff exit code 0 = no issues, 1 = issues found, 2 = error
        if result.returncode == 2:
            return f"Ruff error: {result.stderr.strip()}"

        output = result.stdout.strip()
        if not output:
            return "No lint issues found. Code follows PEP 8 and pyflakes rules."

        # Clean up temp file path from output so model sees clean line numbers
        import re
        output = re.sub(r"[^\s]+\.py:", "Line ", output)
        return f"Lint results ({select} rules):\n{output}"

    except FileNotFoundError:
        return (
            "Error: ruff is not installed. "
            "Install it with: pip install ruff\n"
            "Cannot perform lint check without ruff."
        )
    except subprocess.TimeoutExpired:
        return "Error: lint check timed out."
    except Exception as exc:
        return f"Error: lint_code failed unexpectedly: {exc}"


def _handle_doc_search(args: dict) -> str:
    """
    Route doc_search tool call to docs.python.org search.
    Returns documentation excerpts the model can use to explain concepts.
    """
    import urllib.request
    import urllib.parse

    keyword     = args.get("keyword", "").strip()
    if not keyword:
        return "Error: doc_search requires a non-empty 'keyword' argument."

    version     = args.get("version", "3")
    max_results = min(int(args.get("max_results", 3)), 5)

    try:
        query  = urllib.parse.urlencode({"q": keyword})
        url    = f"https://docs.python.org/{version}/search.html?{query}"
        search_api = (
            f"https://docs.python.org/{version}/"
            f"genindex-all.html"
        )

        # Use the Python docs search JSON endpoint
        search_url = (
            f"https://docs.python.org/{version}/search.html?"
            + urllib.parse.urlencode({"q": keyword, "check_keywords": "yes", "area": "default"})
        )

        # Fetch search results
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "PythonTutor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode("utf-8")

        # Extract result titles and links from search HTML
        import re
        # Match search result links in Python docs HTML
        pattern = re.compile(
            r'<li><a href="([^"]+)"[^>]*>([^<]+)</a>'
        )
        matches = pattern.findall(html)

        if not matches:
            return (
                f"No documentation results found for '{keyword}'. "
                f"Try a simpler keyword like the function name alone.\n"
                f"Browse manually: https://docs.python.org/{version}/search.html?q={urllib.parse.quote(keyword)}"
            )

        results = []
        base_url = f"https://docs.python.org/{version}/"
        for href, title in matches[:max_results]:
            full_url = base_url + href if not href.startswith("http") else href
            results.append(f"• {title.strip()}\n  {full_url}")

        result_text = "\n".join(results)
        search_link = f"https://docs.python.org/{version}/search.html?q={urllib.parse.quote(keyword)}"

        return (
            f"Python {version} documentation results for '{keyword}':\n\n"
            f"{result_text}\n\n"
            f"Full search: {search_link}"
        )

    except urllib.error.URLError as exc:
        return (
            f"Error: Could not reach docs.python.org: {exc}\n"
            f"Check your internet connection, or browse manually:\n"
            f"https://docs.python.org/3/search.html?q={urllib.parse.quote(keyword)}"
        )
    except Exception as exc:
        return f"Error: doc_search failed: {exc}"


# ---------------------------------------------------------------------------
# DISPATCHER — the single entry point called by the tool loop
# ---------------------------------------------------------------------------

_HANDLERS = {
    "run_python": _handle_run_python,
    "lint_code":  _handle_lint_code,
    "doc_search": _handle_doc_search,
}


def dispatch(tool_name: str, args: dict) -> str:
    """
    Route a tool call from the LLM to the correct handler.

    Always returns a string — never raises an exception.
    The tool loop appends this string as a tool_result message.

    Handles:
      - Hallucinated tool names (model invents a name that doesn't exist)
      - Missing arguments (caught inside each handler)
      - Tool crashes (caught here as a final safety net)
    """
    # Hallucinated tool name — model requested something that doesn't exist
    if tool_name not in KNOWN_TOOL_NAMES:
        known = ", ".join(sorted(KNOWN_TOOL_NAMES))
        return (
            f"Error: tool '{tool_name}' does not exist.\n"
            f"Available tools: {known}\n"
            f"Please call one of the available tools."
        )

    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return f"Error: tool '{tool_name}' has no handler implementation."

    # Final safety net — tool crashes must never crash the loop
    try:
        return handler(args)
    except Exception as exc:
        return (
            f"Error: tool '{tool_name}' failed unexpectedly.\n"
            f"Detail: {exc}\n"
            f"Report this to the tutor developer."
        )


# ---------------------------------------------------------------------------
# MANUAL TEST — run directly to verify all three tools work
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("DAY 3 — TOOL DISPATCHER TEST")
    print("=" * 50)

    tests = [
        # run_python — success
        ("run_python", {"code": "print(2 ** 10)"}),
        # run_python — runtime error
        ("run_python", {"code": "x = 1 / 0"}),
        # run_python — security violation
        ("run_python", {"code": "import os; os.system('echo hacked')"}),
        # run_python — timeout
        ("run_python", {"code": "while True: pass", "timeout_s": 2}),
        # run_python — missing argument
        ("run_python", {}),
        # lint_code — has issues
        ("lint_code",  {"code": "x=1\ny = x+1\nprint(y )"}),
        # doc_search
        ("doc_search", {"keyword": "enumerate", "max_results": 2}),
        # hallucinated tool name
        ("execute_code", {"code": "print(1)"}),
    ]

    for tool_name, args in tests:
        print(f"\n{'─'*50}")
        print(f"Tool  : {tool_name}")
        print(f"Args  : {args}")
        result = dispatch(tool_name, args)
        print(f"Result:\n{result}")

    print(f"\n{'='*50}")
    print("Dispatcher test complete.")