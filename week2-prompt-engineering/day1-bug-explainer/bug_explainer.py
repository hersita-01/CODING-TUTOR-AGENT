import os
import sys
import traceback
from dotenv import load_dotenv
from openai import OpenAI

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
# USER INPUT
# -----------------------------------

language = input("Enter programming language: ")

print("\nPaste your code below.")
print("Press ENTER twice when finished.\n")

lines = []

while True:

    line = input()

    if line == "":
        break

    lines.append(line)

student_code = "\n".join(lines)

if not language.strip() or not student_code.strip():
    print("ERROR: Language and code are required.")
    sys.exit(1)

# -----------------------------------
# AUTOMATIC ERROR DETECTION
# -----------------------------------

error_type = None
error_message = None

try:

    compile(student_code, "<string>", "exec")
    exec(student_code)

    print("\n✅ No runtime errors detected.")
    sys.exit(0)

except Exception as e:

    error_type = type(e).__name__
    error_message = str(e)

# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------

system_prompt = f"""
You are a patient and beginner-friendly {language} programming tutor.

Your task is to explain programming errors clearly for beginners.

Rules:
- Be calm and encouraging
- Avoid difficult jargon
- Explain what the error means
- Explain why the error happened
- Never directly provide the corrected code
- Keep explanations short and beginner-friendly
- End with ONE guiding question
- Encourage independent thinking
"""

# -----------------------------------
# USER PROMPT
# -----------------------------------

user_prompt = f"""
Programming Language:
{language}

Student Code:
{student_code}

Detected Error:
{error_type}: {error_message}

Explain this error simply for a beginner programmer.
"""

# -----------------------------------
# API CALL
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
        temperature=0.3,
        max_tokens=250
    )

    print("-----------------------------------")
    print("AI TUTOR RESPONSE")
    print("-----------------------------------\n")

    print(response.choices[0].message.content)

except Exception as e:

    print("\n-----------------------------------")
    print("SYSTEM ERROR")
    print("-----------------------------------")
    print(e)