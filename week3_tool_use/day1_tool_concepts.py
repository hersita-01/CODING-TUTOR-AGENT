
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

# ------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not found in .env")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "llama-3.3-70b-versatile"

# ------------------------------------------------------------------
# Tool Definition
# ------------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute Python code safely and return output."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    },
                    "timeout_s": {
                        "type": "integer",
                        "description": "Execution timeout in seconds"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# ------------------------------------------------------------------
# User Question
# ------------------------------------------------------------------

question = """
What does this Python code print? Explain the result.

print(2 ** 10)
"""

messages = [
    {
        "role": "user",
        "content": question
    }
]

print("=" * 60)
print("DAY 1 - GROQ TOOL USE TEST")
print("=" * 60)

# ------------------------------------------------------------------
# API Call
# ------------------------------------------------------------------

try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2,
        max_tokens=500
    )

except Exception as e:
    print("\nAPI ERROR:")
    print(e)
    sys.exit(1)

# ------------------------------------------------------------------
# Inspect Response
# ------------------------------------------------------------------

message = response.choices[0].message
finish_reason = response.choices[0].finish_reason

print("\nFinish Reason:", finish_reason)
print("\nMessage Content:")
print(message.content)

print("\nTool Calls:")
print(message.tool_calls)

# ------------------------------------------------------------------
# Tool Call Handling
# ------------------------------------------------------------------

if message.tool_calls:

    print("\nMODEL REQUESTED TOOL CALL\n")

    for tool_call in message.tool_calls:

        try:
            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("Tool Name :", tool_name)
            print("Tool ID   :", tool_call.id)

            print("\nArguments:")
            print(json.dumps(arguments, indent=4))

            print("\nCode To Execute:")
            print(arguments.get("code"))

            print(
                "\nLater on Day 3 you will pass "
                "this code into safe_python_runner.py"
            )

        except Exception as e:
            print("Error parsing tool call:", e)

else:

    print("\nMODEL ANSWERED DIRECTLY\n")

    if message.content:
        print(message.content)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("""
1. Tools are descriptions of functions.

2. If finish_reason == "tool_calls":
   The model wants you to execute a tool.

3. If finish_reason == "stop":
   The model answered directly.

4. Tool arguments arrive as JSON.

5. Use json.loads() to parse them.

6. On Day 3:
   - Execute tool
   - Append tool result
   - Call model again
   - Get final answer
""")