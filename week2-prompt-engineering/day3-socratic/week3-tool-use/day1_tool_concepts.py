"""
week3-tool-use/day1-notes/day1_groq_tool_use_test.py

Day 1 — Groq Tool Use: Connection and concept test.

This file does NOT build the full tutor yet.
It proves three things:
  1. Your GROQ_API_KEY works with tool use
  2. You can define a tool and send it to the model
  3. You can read back whether the model wanted to call a tool

No safe_python_runner is needed yet — that comes on Day 3.
Run this file and read every print statement carefully.
They explain exactly what the model sent back.
"""

import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# SETUP — same as every file in your project
# ---------------------------------------------------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY is missing from your .env file.")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# STEP 1 — Define one tool
#
# This is just a description. You are telling the model:
#   "A function called run_python exists.
#    It takes a code string and an optional timeout.
#    Call it when you need to execute Python code."
#
# The model does NOT call it. YOU call it when the model asks.
# ---------------------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Safely execute a Python code snippet in a sandbox and "
                "return its stdout output or any error message. "
                "Use this whenever you need to know what a piece of "
                "Python code actually does or produces."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code snippet to execute.",
                    },
                    "timeout_s": {
                        "type": "integer",
                        "description": (
                            "Maximum seconds to allow the code to run. "
                            "Defaults to 3. Never set above 10."
                        ),
                    },
                },
                "required": ["code"],
            },
        },
    }
]

# ---------------------------------------------------------------------------
# STEP 2 — Send a question that should trigger a tool call
#
# We ask the model what a piece of code prints.
# A smart model will realise it should RUN the code to know for sure,
# and will call run_python rather than guessing.
# ---------------------------------------------------------------------------

question = "What does this Python code print? Explain the result.\n\nprint(2 ** 10)"

messages = [
    {"role": "user", "content": question}
]

print("=" * 50)
print("DAY 1 — GROQ TOOL USE TEST")
print("=" * 50)
print(f"\nQuestion sent to model:\n  {question}\n")

# ---------------------------------------------------------------------------
# STEP 3 — Call the API with tools
# ---------------------------------------------------------------------------

try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # model decides when to use tools
        max_tokens=500,
        temperature=0.2,
    )
except Exception as exc:
    print(f"ERROR: API call failed — {exc}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# STEP 4 — Inspect what the model sent back
#
# There are exactly two possible outcomes:
#   A) model.tool_calls is not None  → model wants to call run_python
#   B) model.tool_calls is None      → model answered directly in text
# ---------------------------------------------------------------------------

message = response.choices[0].message
finish_reason = response.choices[0].finish_reason

print("-" * 50)
print("RAW RESPONSE INSPECTION")
print("-" * 50)
print(f"  finish_reason : {finish_reason}")
print(f"  tool_calls    : {message.tool_calls}")
print(f"  content       : {message.content}")
print()

# ---------------------------------------------------------------------------
# STEP 5 — Handle both outcomes and explain what happened
# ---------------------------------------------------------------------------

if message.tool_calls:
    # ── Outcome A: model wants to call a tool ────────────────────────────────
    print("-" * 50)
    print("OUTCOME: Model requested a tool call")
    print("-" * 50)

    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        tool_id   = tool_call.id

        print(f"\n  Tool requested : {tool_name}")
        print(f"  Tool call ID   : {tool_id}")
        print(f"  Arguments      : {json.dumps(tool_args, indent=4)}")

        print("\n  What this means:")
        print(f"  The model wants to run: {tool_args.get('code', '')!r}")
        print(f"  With timeout          : {tool_args.get('timeout_s', 3)} seconds")
        print()
        print("  On Day 3 you will:")
        print("  1. Pass this code to run_python_safely() from safe_python_runner.py")
        print("  2. Get back the output")
        print("  3. Append it to messages and call the API again")
        print("  4. The model will then explain the result to the student")

    # ── Show what the Day 3 tool result message will look like ────────────────
    print()
    print("-" * 50)
    print("PREVIEW: What a tool result message looks like (Day 3)")
    print("-" * 50)

    example_result_message = {
        "role": "tool",
        "tool_call_id": message.tool_calls[0].id,
        "content": "1024",   # this is what run_python_safely() would return
    }

    print("\n  You would append this to messages and call the API again:")
    print(f"\n  {json.dumps(example_result_message, indent=4)}")

else:
    # ── Outcome B: model answered directly ───────────────────────────────────
    print("-" * 50)
    print("OUTCOME: Model answered directly without calling a tool")
    print("-" * 50)
    print(f"\n  Model answer:\n  {message.content}")
    print()
    print("  This is fine — the model decided it already knew the answer.")
    print("  On Day 3, with a more complex question, it will call the tool.")

# ---------------------------------------------------------------------------
# STEP 6 — Summary of what you just learned
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("DAY 1 SUMMARY — KEY CONCEPTS")
print("=" * 50)
print("""
1. TOOL DEFINITION
   A JSON object with: name, description, parameters.
   It is a description — not actual code the model runs.

2. finish_reason == "tool_calls"
   The model wants to call a function.
   You run it. You send the result back.

3. finish_reason == "stop"
   The model gave a text answer.
   Show it to the student. You are done.

4. message.tool_calls
   Contains: tool name, tool id, arguments as a JSON string.
   Always use json.loads() on tool_call.function.arguments.

5. Tool result message format
   role        : "tool"
   tool_call_id: the id from the tool_call
   content     : your result as a string

6. The loop (Day 3)
   Keep calling the API until finish_reason == "stop".
   Append every tool result to messages before each call.
""")