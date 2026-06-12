"""
week3-tool-use/day2-tool-schema/tool_schemas.py

Day 2 — Tool Schema Design

Defines JSON schemas for the three tools the LLM tutor can call:
  1. run_python  — executes student code via Week 2 safe_python_runner.py
  2. lint_code   — checks code quality using ruff
  3. doc_search  — searches official Python docs by keyword

This file is DATA ONLY — no logic, no API calls, no external imports.
Every Day 3 / Day 4 / Day 5 file imports TUTOR_TOOLS and KNOWN_TOOL_NAMES
from here. To change a description or add a parameter, edit only this file.
"""

# ---------------------------------------------------------------------------
# TOOL 1 — run_python
# Backed by: safe_python_runner.run_python_safely() (Week 2, never rewritten)
# ---------------------------------------------------------------------------

RUN_PYTHON_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_python",
        "description": (
            "Safely execute a Python code snippet in a sandboxed subprocess "
            "and return its stdout output, stderr, or any runtime error. "
            "ALWAYS use this tool when you need to know what a piece of "
            "Python code actually produces — never guess the output. "
            "The sandbox blocks dangerous operations: file writes, OS "
            "commands, subprocess calls, eval, exec, and memory abuse. "
            "Use this to diagnose crashes, verify output, and explain "
            "runtime behaviour to the student."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": (
                        "The complete, self-contained Python code snippet "
                        "to execute. Do not assume variables exist from "
                        "previous calls."
                    ),
                },
                "timeout_s": {
                    "type": "integer",
                    "description": (
                        "Maximum seconds before the process is killed. "
                        "Default 3. Never set above 10."
                    ),
                },
                "user_input": {
                    "type": "string",
                    "description": (
                        "Newline-separated stdin values to feed if the "
                        "code calls input(). Leave empty if not needed."
                    ),
                },
            },
            "required": ["code"],
        },
    },
}

# ---------------------------------------------------------------------------
# TOOL 2 — lint_code
# Backed by: ruff (pip install ruff)
# Does NOT execute code — use run_python for execution.
# ---------------------------------------------------------------------------

LINT_CODE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "lint_code",
        "description": (
            "Analyse Python code for style issues, unused variables, "
            "undefined names, and common mistakes using the ruff linter. "
            "Use this when a student asks about code quality, PEP 8 "
            "compliance, best practices, or potential bugs that do not "
            "require running the code. "
            "Does NOT execute — use run_python for runtime behaviour. "
            "Returns warnings with line numbers and rule codes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": (
                        "The Python code to lint. Does not need to be "
                        "runnable — works even with syntax errors."
                    ),
                },
                "select": {
                    "type": "string",
                    "description": (
                        "Comma-separated ruff rule codes. "
                        "'E,W' for PEP8 style, 'F' for pyflakes logic errors, "
                        "'E,F,W' for common checks (default), "
                        "'ALL' for everything."
                    ),
                },
            },
            "required": ["code"],
        },
    },
}

# ---------------------------------------------------------------------------
# TOOL 3 — doc_search
# Backed by: docs.python.org search API (live documentation)
# ---------------------------------------------------------------------------

DOC_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "doc_search",
        "description": (
            "Search the official Python documentation at docs.python.org "
            "by keyword and return relevant page titles, URLs, and excerpts. "
            "Use this when a student asks how a built-in function, standard "
            "library module, or language feature works — for example: "
            "'how does enumerate work', 'what does sorted() return', "
            "'explain list comprehensions', 'os.path methods'. "
            "Do NOT use for debugging runtime errors — use run_python. "
            "Returns the top matching documentation sections."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "Python concept, function, or module to search. "
                        "Examples: 'enumerate', 'list append', "
                        "'dictionary comprehension', 'os.path', 'try except'."
                    ),
                },
                "version": {
                    "type": "string",
                    "description": (
                        "Python version to search. Use '3' for latest "
                        "Python 3 docs (default), or '3.11', '3.12' etc."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Maximum results to return. Default 3. Max 5. "
                        "Keep low to avoid filling the context window."
                    ),
                },
            },
            "required": ["keyword"],
        },
    },
}

# ---------------------------------------------------------------------------
# EXPORTS — import these in every Week 3 file
# ---------------------------------------------------------------------------

TUTOR_TOOLS = [
    RUN_PYTHON_SCHEMA,
    LINT_CODE_SCHEMA,
    DOC_SEARCH_SCHEMA,
]

# Used by tool_dispatcher to detect hallucinated tool names
KNOWN_TOOL_NAMES = {schema["function"]["name"] for schema in TUTOR_TOOLS}


# ---------------------------------------------------------------------------
# VALIDATION — run directly to verify all schemas before Day 3
# ---------------------------------------------------------------------------

def validate_schema(schema: dict) -> list[str]:
    """Check a tool schema. Returns list of error strings."""
    errors = []
    fn = schema.get("function", {})

    if not fn.get("name"):
        errors.append("Missing: function.name")
    if not fn.get("description") or len(fn["description"]) < 50:
        errors.append("Description missing or too short")

    params = fn.get("parameters", {})
    if params.get("type") != "object":
        errors.append("parameters.type must be 'object'")

    props = params.get("properties", {})
    if not props:
        errors.append("No properties defined")

    for req in params.get("required", []):
        if req not in props:
            errors.append(f"Required field '{req}' missing from properties")

    for fname, fdef in props.items():
        if "type" not in fdef:
            errors.append(f"Property '{fname}' missing 'type'")
        if "description" not in fdef:
            errors.append(f"Property '{fname}' missing 'description'")

    return errors


if __name__ == "__main__":
    import json

    print("=" * 50)
    print("DAY 2 — TOOL SCHEMA VALIDATION")
    print("=" * 50)

    all_valid = True
    for schema in TUTOR_TOOLS:
        name   = schema["function"]["name"]
        errors = validate_schema(schema)
        status = "PASS" if not errors else "FAIL"
        print(f"\n  {status}  {name}")
        for e in errors:
            all_valid = False
            print(f"       ✗ {e}")
        print(f"\n  Schema preview:")
        print(f"    description : {schema['function']['description'][:80]}...")
        print(f"    required    : {schema['function']['parameters'].get('required')}")
        print(f"    optional    : {[k for k in schema['function']['parameters']['properties'] if k not in schema['function']['parameters'].get('required',[])]}")

    print(f"\n{'─'*50}")
    print(f"  Total tools   : {len(TUTOR_TOOLS)}")
    print(f"  Tool names    : {sorted(KNOWN_TOOL_NAMES)}")
    print()
    print("ALL SCHEMAS VALID — ready for Day 3" if all_valid else "FIX ISSUES ABOVE")