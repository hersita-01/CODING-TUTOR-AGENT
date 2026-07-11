"""
week3-tool-use/day5-error-handling/test_failure_modes.py

Day 5 — Failure Mode Test Suite

Proves every failure mode listed in the Week 3 brief is actually handled,
without needing a live API key. Tests the pure functions from
robust_tool_loop.py directly — no network calls, no Groq dependency.

Run this file directly:
    python test_failure_modes.py

Each test prints PASS/FAIL so you can verify the defensive layer works
before relying on it with real student input.
"""

import json
import sys
from pathlib import Path

# Import the functions under test
sys.path.insert(0, str(Path(__file__).resolve().parent))
from robust_tool_loop import (
    categorise_api_error,
    ApiFailureCategory,
    validate_tool_call_name,
    parse_tool_arguments,
    validate_required_arguments,
    truncate_tool_result,
    detect_repeated_call,
    MAX_TOOL_RESULT_LEN,
)

# Import dispatcher to test real tool crash handling
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "day3-tool-loop"))
from tool_dispatcher import dispatch


_PASS = 0
_FAIL = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if condition:
        _PASS += 1
        print(f"  PASS  {label}")
    else:
        _FAIL += 1
        print(f"  FAIL  {label}  {detail}")


def section(title: str) -> None:
    print(f"\n{'─'*55}")
    print(title)
    print('─'*55)


# ---------------------------------------------------------------------------
# TEST 1 — Hallucinated tool names
# ---------------------------------------------------------------------------

section("1. HALLUCINATED TOOL NAMES")

is_valid, err = validate_tool_call_name("execute_code")
check("rejects hallucinated tool name 'execute_code'", not is_valid)
check("error message lists available tools", "run_python" in err)

is_valid, err = validate_tool_call_name("run_python")
check("accepts real tool name 'run_python'", is_valid)

is_valid, err = validate_tool_call_name("RunPython")  # wrong case
check("rejects case-mismatched tool name", not is_valid)


# ---------------------------------------------------------------------------
# TEST 2 — Malformed / missing tool arguments
# ---------------------------------------------------------------------------

section("2. MALFORMED TOOL CALL ARGUMENTS")

args, err = parse_tool_arguments('{"code": "print(1)"}', "run_python")
check("parses valid JSON arguments", err == "" and args == {"code": "print(1)"})

args, err = parse_tool_arguments('{"code": "print(1)"', "run_python")  # missing }
check("detects malformed/truncated JSON", err != "" and args == {})

args, err = parse_tool_arguments("", "run_python")
check("detects empty arguments string", err != "" and "empty" in err.lower())

args, err = parse_tool_arguments('"just a string"', "run_python")  # valid JSON, wrong type
check("detects non-object JSON (string instead of dict)", err != "")

args, err = parse_tool_arguments('[1, 2, 3]', "run_python")  # valid JSON, wrong type
check("detects non-object JSON (array instead of dict)", err != "")


# ---------------------------------------------------------------------------
# TEST 3 — Missing required fields
# ---------------------------------------------------------------------------

section("3. MISSING REQUIRED ARGUMENTS")

ok, err = validate_required_arguments("run_python", {"timeout_s": 5})
check("detects missing required 'code' field", not ok and "code" in err)

ok, err = validate_required_arguments("run_python", {"code": "print(1)"})
check("accepts when required field present", ok)

ok, err = validate_required_arguments("run_python", {"code": ""})
check("detects empty-string required field as missing", not ok)

ok, err = validate_required_arguments("doc_search", {})
check("detects missing required 'keyword' field for doc_search", not ok and "keyword" in err)

ok, err = validate_required_arguments("lint_code", {"code": "x=1"})
check("accepts lint_code with only required field (select is optional)", ok)


# ---------------------------------------------------------------------------
# TEST 4 — API error categorisation
# ---------------------------------------------------------------------------

section("4. API ERROR CATEGORISATION")

cat = categorise_api_error(Exception("Error code: 401 - Invalid API Key"))
check("categorises 401 as AUTH", cat == ApiFailureCategory.AUTH)

cat = categorise_api_error(Exception("Error code: 429 - rate limit exceeded"))
check("categorises 429 as RATE_LIMIT", cat == ApiFailureCategory.RATE_LIMIT)

cat = categorise_api_error(Exception("model 'fake-model' does not exist"))
check("categorises bad model name as MODEL_ERROR", cat == ApiFailureCategory.MODEL_ERROR)

cat = categorise_api_error(Exception("Connection timeout while reaching api.groq.com"))
check("categorises network timeout as NETWORK", cat == ApiFailureCategory.NETWORK)

cat = categorise_api_error(Exception("Something completely unexpected happened"))
check("categorises unrecognised error as UNKNOWN", cat == ApiFailureCategory.UNKNOWN)


# ---------------------------------------------------------------------------
# TEST 5 — Oversized tool result truncation
# ---------------------------------------------------------------------------

section("5. OVERSIZED TOOL RESULT TRUNCATION")

short_result = "Output: 42"
truncated = truncate_tool_result(short_result)
check("leaves short results unchanged", truncated == short_result)

huge_result = "x" * (MAX_TOOL_RESULT_LEN + 5000)
truncated = truncate_tool_result(huge_result)
check(
    f"truncates oversized result to under {MAX_TOOL_RESULT_LEN} + notice",
    len(truncated) < len(huge_result) and "truncated" in truncated.lower()
)


# ---------------------------------------------------------------------------
# TEST 6 — Repeated identical tool calls (runaway loop signal)
# ---------------------------------------------------------------------------

section("6. REPEATED CALL DETECTION (runaway loop signal)")

history = []
args_json = json.dumps({"code": "print(1)"}, sort_keys=True)

is_repeat = detect_repeated_call(history, "run_python", args_json)
check("first call is not flagged as repeat", not is_repeat)

history.append(("run_python", args_json))
is_repeat = detect_repeated_call(history, "run_python", args_json)
check("identical second call IS flagged as repeat", is_repeat)

different_args = json.dumps({"code": "print(2)"}, sort_keys=True)
is_repeat = detect_repeated_call(history, "run_python", different_args)
check("different arguments are NOT flagged as repeat", not is_repeat)


# ---------------------------------------------------------------------------
# TEST 7 — Real tool crashes (via actual dispatch(), not mocked)
# These exercise the Week 2 sandbox directly.
# ---------------------------------------------------------------------------

section("7. REAL TOOL EXECUTION — INFINITE LOOP / TIMEOUT")

result = dispatch("run_python", {"code": "while True:\n    pass", "timeout_s": 2})
check(
    "infinite loop is killed by timeout, not hung forever",
    "timeout" in result.lower() or "exceeded" in result.lower()
)

section("8. REAL TOOL EXECUTION — SYNTAX ERROR")

result = dispatch("run_python", {"code": "def broken(:\n    pass"})
check(
    "syntax error is caught and reported, not silently swallowed",
    "syntax" in result.lower() or "failed" in result.lower()
)

section("9. REAL TOOL EXECUTION — SECURITY VIOLATION")

result = dispatch("run_python", {"code": "import os\nos.system('echo pwned')"})
check(
    "dangerous os.system call is blocked by Week 2 sandbox",
    "security" in result.lower() or "blocked" in result.lower()
)

section("10. REAL TOOL EXECUTION — DISPATCHER NEVER RAISES")

# Even with garbage input, dispatch() must return a string, never raise
try:
    result = dispatch("run_python", {"code": None})
    check("dispatch() handles None code without raising", isinstance(result, str))
except Exception as exc:
    check("dispatch() handles None code without raising", False, f"raised {exc}")

try:
    result = dispatch("nonexistent_tool_xyz", {"anything": "goes"})
    check("dispatch() handles unknown tool without raising", isinstance(result, str))
except Exception as exc:
    check("dispatch() handles unknown tool without raising", False, f"raised {exc}")


# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------

print(f"\n{'='*55}")
print(f"RESULTS: {_PASS} passed, {_FAIL} failed")
print('='*55)

if _FAIL == 0:
    print("\nAll failure modes handled correctly. Ready for production use.")
else:
    print(f"\n{_FAIL} failure mode(s) NOT properly handled. Review robust_tool_loop.py.")
    sys.exit(1)