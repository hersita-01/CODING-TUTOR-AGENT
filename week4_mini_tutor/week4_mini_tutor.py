# -----------------------------------
# WEEK 4 - MINI-TUTOR v1
# CORE AGENT  —  GROK API (OpenAI-compatible)
# -----------------------------------
#
# Uses the OpenAI Python SDK pointed at xAI's endpoint.
# Set XAI_API_KEY in your .env file.
#
# This file contains:
#   1. All three tools  (run_python, lint_code, doc_search)
#   2. Tool schemas in OpenAI / Grok function-calling format
#   3. Tool executor
#   4. The ReAct agent loop
#   5. A CLI entry point for testing without Streamlit
# -----------------------------------

import subprocess
import tempfile
import os
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------
# SAFETY CONSTANTS
# -----------------------------------

MAX_TOOL_CALLS  = 6       # handbook: cap at 6 per turn
MAX_CODE_LINES  = 30      # handbook: accept ≤ 30 lines
TIMEOUT_SECONDS = 5       # hard sandbox timeout

# Grok model to use — fast, capable, tool-calling supported
GROK_MODEL ="llama-3.3-70b-versatile"

# -----------------------------------
# TOOL 1 : RUN PYTHON
# -----------------------------------

def run_python(code: str, timeout_s: int = TIMEOUT_SECONDS) -> dict:
    """Safely execute Python code in a subprocess sandbox."""

    if not code or not code.strip():
        return {"success": False, "error": "No Python code was provided."}

    lines = code.splitlines()
    if len(lines) > MAX_CODE_LINES:
        return {
            "success": False,
            "error": (
                f"Code exceeds the {MAX_CODE_LINES}-line limit "
                f"({len(lines)} lines submitted). Please submit a shorter snippet."
            )
        }

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_s
        )
        os.remove(temp_path)

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return {
            "success": False,
            "error": (
                f"Execution stopped after {timeout_s}s — "
                "this usually means an infinite loop. "
                "Check your loop conditions."
            )
        }

    except Exception as e:
        return {"success": False, "error": f"Execution environment error: {str(e)}"}


# -----------------------------------
# TOOL 2 : LINT CODE
# -----------------------------------

def lint_code(code: str) -> dict:
    """Run ruff linter on Python code."""

    if not code or not code.strip():
        return {"success": False, "error": "No code was provided for linting."}

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["ruff", "check", temp_path, "--select", "E,F,W"],
            capture_output=True,
            text=True
        )
        os.remove(temp_path)

        lint_output = result.stdout.replace(temp_path, "<your_code>")
        return {
            "success": True,
            "issues_found": bool(lint_output.strip()),
            "lint_output": lint_output,
        }

    except FileNotFoundError:
        return {"success": False, "error": "ruff is not installed. Run: pip install ruff"}

    except Exception as e:
        return {"success": False, "error": f"Linter error: {str(e)}"}


# -----------------------------------
# TOOL 3 : DOC SEARCH
# -----------------------------------

def doc_search(keyword: str) -> dict:
    """Search local Python documentation by keyword (partial match)."""

    if not keyword or not keyword.strip():
        return {"success": False, "error": "No keyword was provided."}

    python_docs = {
        "list":        "Lists store ordered, mutable collections. Created with []. Supports .append(), .remove(), .sort(), indexing, and slicing.",
        "dictionary":  "Dictionaries store key-value pairs. Created with {}. Access values with dict[key] or dict.get(key). Keys must be unique and hashable.",
        "function":    "Functions are reusable blocks defined with 'def'. They accept parameters and return values with 'return'. Parameters have local scope.",
        "loop":        "Python has two loops: 'for' (iterate over a sequence) and 'while' (run while a condition is True).",
        "for loop":    "For loops iterate over sequences. Syntax: 'for item in sequence:'. Use range(n) to loop n times. Use enumerate() for index + value.",
        "while loop":  "While loops run while a condition is True. Syntax: 'while condition:'. Always ensure the condition can become False to avoid infinite loops.",
        "try":         "try-except handles runtime errors. Syntax: 'try: ... except ErrorType as e: ...'. Use 'finally:' for cleanup. Common: ValueError, TypeError, KeyError, IndexError.",
        "if":          "if-elif-else runs code based on conditions. Syntax: 'if cond: ... elif other: ... else: ...'. Uses ==, !=, <, >, <=, >=.",
        "class":       "Classes are blueprints for objects. Defined with 'class Name:'. __init__(self) is the constructor. Set instance attributes with self.attr = value.",
        "inheritance": "Inheritance lets a class extend another. Syntax: 'class Child(Parent):'. Use super() to call parent methods.",
        "string":      "Strings store text in quotes. Immutable. Useful methods: .strip(), .split(), .join(), .replace(), .upper(), .lower(), and f-strings.",
        "integer":     "Integers (int) are whole numbers. Supports +, -, *, /, // (floor), % (modulo), ** (power). Convert with int().",
        "float":       "Floats store decimals. Watch out for precision issues (0.1 + 0.2 ≠ 0.3). Use round() to limit decimal places.",
        "enumerate":   "enumerate() gives both index and value. Syntax: 'for i, val in enumerate(my_list):'. Optional start: enumerate(lst, start=1).",
        "tuple":       "Tuples store ordered, immutable data. Created with (). Cannot be modified after creation. Good for fixed data like coordinates.",
        "set":         "Sets store unique, unordered values. Created with set() (not {} — that's a dict). Fast membership checks. Supports union, intersection.",
        "import":      "import loads modules. Syntax: 'import module' or 'from module import name'. Standard library needs no install; third-party needs pip.",
        "return":      "return sends a value back from a function. No return means the function returns None. Can return multiple values: 'return a, b'.",
        "variable":    "Variables store data. Python is dynamically typed — no type declaration needed. Names are case-sensitive. Use descriptive names.",
        "scope":       "Scope determines where a variable is accessible. Local: inside a function. Global: top level. Use 'global' keyword to modify a global inside a function.",
        "recursion":   "Recursion is when a function calls itself. Needs a base case (stop condition) or it hits Python's recursion limit (default 1000). Example: factorial.",
    }

    kw = keyword.lower().strip()

    matches = [
        {"topic": t, "explanation": e}
        for t, e in python_docs.items()
        if kw in t or t in kw
    ]

    if not matches:
        matches = [
            {"topic": t, "explanation": e}
            for t, e in python_docs.items()
            if any(word in kw for word in t.split())
        ]

    if not matches:
        return {
            "success": True,
            "results": [],
            "message": (
                f"No documentation found for '{keyword}'. "
                "Try: list, dictionary, function, loop, for loop, while loop, "
                "try, class, string, integer, recursion, scope, import, return."
            )
        }

    return {"success": True, "results": matches}


# -----------------------------------
# TOOL REGISTRY & SCHEMAS
# -----------------------------------

TOOL_FUNCTIONS = {
    "run_python": run_python,
    "lint_code":  lint_code,
    "doc_search": doc_search,
}

# OpenAI / Grok function-calling format
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Safely execute Python code in a sandboxed subprocess and return "
                "stdout, stderr, and exit code. Use this first whenever the student's "
                f"question involves runtime behaviour or errors. Max {MAX_CODE_LINES} "
                f"lines, {TIMEOUT_SECONDS}s hard timeout."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code submitted by the student."
                    },
                    "timeout_s": {
                        "type": "integer",
                        "description": "Max execution seconds.",
                        "default": TIMEOUT_SECONDS,
                        "minimum": 1,
                        "maximum": TIMEOUT_SECONDS
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lint_code",
            "description": (
                "Run the ruff linter on Python code to find style issues, "
                "undefined names, unused variables, and code quality problems. "
                "Use when code runs but may have quality issues worth discussing."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to lint."
                    }
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
                "Search local Python documentation for concept explanations. "
                "Use when the student seems confused about a Python keyword, "
                "data type, or built-in concept."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Python concept to look up, e.g. 'list', 'for loop', 'recursion'."
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]


# -----------------------------------
# TOOL EXECUTOR
# -----------------------------------

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Run a tool and return a JSON string result."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({
            "success": False,
            "error": f"Unknown tool '{tool_name}'. Available: {list(TOOL_FUNCTIONS.keys())}"
        })
    try:
        return json.dumps(TOOL_FUNCTIONS[tool_name](**tool_input))
    except TypeError as e:
        return json.dumps({"success": False, "error": f"Wrong arguments: {str(e)}"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Tool crashed: {str(e)}"})


# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------

SYSTEM_PROMPT = """You are Mini-Tutor, a patient and encouraging AI coding tutor for Python beginners.
Your goal is to help students UNDERSTAND and fix their own bugs — never to hand over fixed code directly.

RULES:
1. When a student submits code, ALWAYS call run_python first to see actual runtime behaviour.
2. NEVER reveal the corrected code. Use a Socratic question to guide the student to the fix.
3. Structure every reply EXACTLY like this:

   **Diagnosis:** (one sentence — what is wrong and on which line)
   **Question:** (one guiding question that nudges them toward the bug — not the answer)
   **Next Step:** (one small, concrete action to try)

4. If code runs fine but the student says output is wrong, ask what they expected.
5. If the student asks you to "just give the answer" or mentions graded work, redirect with a question.
6. Use lint_code if code runs but style/quality issues are worth mentioning.
7. Use doc_search if the student seems confused about a Python concept.
8. Tone: warm, clear, never condescending. You are an AI tutor — never pretend to be human.
9. Maximum 6 tool calls per turn."""


# -----------------------------------
# AGENT LOOP  (ReAct pattern — OpenAI/Grok format)
# -----------------------------------

def run_tutor_agent(
    student_message: str,
    conversation_history: list = None
) -> tuple:
    """
    Run the Mini-Tutor ReAct loop using Grok via the OpenAI-compatible API.

    Args:
        student_message:       Latest message from the student.
        conversation_history:  List of prior message dicts (role/content).

    Returns:
        (final_reply: str, updated_history: list)
    """

    client = OpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    if conversation_history is None:
        conversation_history = []

    # Build the messages list: system prompt + full history + new user message
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + conversation_history
        + [{"role": "user", "content": student_message}]
    )

    tool_call_count = 0
    final_reply = ""

    # --- ReAct loop ---
    while True:

        response = client.chat.completions.create(
            model=GROK_MODEL,
            max_tokens=1500,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        choice   = response.choices[0]
        message  = choice.message
        finish   = choice.finish_reason   # "stop" | "tool_calls" | "length"

        # Add assistant turn to messages
        messages.append(message)

        # -------------------------------------------
        # CASE 1: Done — no more tool calls
        # -------------------------------------------
        if finish == "stop" or finish == "length":
            final_reply = message.content or ""
            break

        # -------------------------------------------
        # CASE 2: Model wants to call tools
        # -------------------------------------------
        if finish == "tool_calls" and message.tool_calls:

            for tc in message.tool_calls:

                tool_call_count += 1

                if tool_call_count > MAX_TOOL_CALLS:
                    result_content = json.dumps({
                        "success": False,
                        "error": "Tool call limit reached — stopping further tool use."
                    })
                else:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    result_content = execute_tool(tc.function.name, args)

                # Tool results go back as role="tool" in OpenAI format
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result_content
                })

        else:
            # Unexpected finish reason
            final_reply = (
                "I ran into an unexpected state. Please try submitting your code again."
            )
            break

    # Build updated history (everything after the system prompt)
    updated_history = messages[1:]   # strip system prompt — caller manages it separately

    return final_reply, updated_history


# -----------------------------------
# CLI ENTRY POINT
# -----------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 52)
    print("  MINI-TUTOR v1  —  Grok API  —  CLI Mode")
    print("  Type 'quit' to exit.")
    print("=" * 52)

    history = []

    while True:
        print("\nPaste your Python code or question.")
        print("Press ENTER twice to submit.\n")

        lines      = []
        blank_count = 0

        while True:
            line = input()
            if line.lower() == "quit":
                print("\nGoodbye! Keep coding.")
                exit()
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
        print("-" * 52)
        print("TUTOR:\n")
        print(reply)
        print("-" * 52)