import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from safe_python_runner import run_python_safely

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY is missing from your .env file.")
    sys.exit(1)

# -----------------------------------
# CREATE GROQ CLIENT
# -----------------------------------

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# -----------------------------------
# GET STUDENT CODE
# -----------------------------------

print("Paste Python code below.")
print("Press ENTER twice to finish.\n")

lines = []

blank_count = 0

while True:

    line = input()

    if line == "":
        blank_count += 1
    else:
        blank_count = 0

    if blank_count == 2:
        break

    lines.append(line)

student_code = "\n".join(lines).strip()

if not student_code:

    print("ERROR: No Python code was entered.")
    sys.exit(1)

# -----------------------------------
# BASIC SECURITY CHECKS
# -----------------------------------

blocked_patterns = [

    "import os",
    "import subprocess",
    "import shutil",

    "os.remove",
    "os.rmdir",
    "os.system",

    "shutil.rmtree",

    "eval(",
    "exec("
]

for pattern in blocked_patterns:

    if pattern in student_code:

        print("\nSECURITY VIOLATION")

        print(
            f"Detected forbidden operation: {pattern}"
        )

        print(
            "\nThis tutor only supports "
            "safe Python debugging exercises."
        )

        sys.exit(1)

# -----------------------------------
# RUN CODE SAFELY
# -----------------------------------

result = run_python_safely(student_code)

# -----------------------------------
# SUCCESS CASE
# -----------------------------------

if result.ok:

    print("\n✅ No runtime errors detected.")

    if hasattr(result, "stdout"):

        if result.stdout:

            print("\nProgram Output:\n")

            print(result.stdout)

    sys.exit(0)

# -----------------------------------
# ERROR INFO
# -----------------------------------

error_type = result.error_type
error_message = result.error_message

# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------

system_prompt = """
You are a beginner-friendly Python tutor.

Your job is to help students understand
their errors without directly fixing them.

Rules:

- Analyze the error step-by-step.
- Explain what Python is complaining about.
- Explain why the error happened.
- Keep explanations beginner-friendly.
- Do not reveal hidden chain-of-thought.
- Summarize reasoning briefly.
- Never directly provide corrected code.
- End with ONE Socratic question.

Response Format:

Diagnosis:
...

Why It Happened:
...

Socratic Question:
...
"""

# -----------------------------------
# USER PROMPT
# -----------------------------------

user_prompt = f"""
Student Code:

{student_code}

Detected Error:

{error_type}: {error_message}

Tasks:

1. Analyze the error step-by-step.
2. Identify what operation failed.
3. Explain why Python raised the error.
4. Ask one Socratic question.
"""

# -----------------------------------
# SEND TO MODEL
# -----------------------------------

try:

    print("\n-----------------------------------")
    print("DETECTED ERROR")
    print("-----------------------------------")

    print(f"Error Type    : {error_type}")
    print(f"Error Message : {error_message}")

    print("\nAnalyzing with AI Tutor...\n")

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.2,

        max_tokens=250
    )

    print("-----------------------------------")
    print("AI TUTOR RESPONSE")
    print("-----------------------------------\n")

    print(
        response.choices[0].message.content
    )

# -----------------------------------
# API ERROR
# -----------------------------------

except Exception as e:

    print("\n-----------------------------------")
    print("SYSTEM ERROR")
    print("-----------------------------------")

    print(e)