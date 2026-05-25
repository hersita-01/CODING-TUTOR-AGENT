import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from safe_python_runner import run_python_safely

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY is missing from your .env file.")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

print("Paste Python code. Type END to finish.\n")

lines = []

while True:

    line = input()

    if line.strip() == "END":
        break

    lines.append(line)

student_code = "\n".join(lines).strip()

if not student_code:
    print("ERROR: No Python code was entered.")
    sys.exit(1)

result = run_python_safely(student_code)
if result.ok:
    print("No runtime errors detected.")
    sys.exit(0)

error_type = result.error_type
error_message = result.error_message

system_prompt = """
You are a strict Socratic Python tutor.

Rules:
- ONLY ask questions
- Never explain directly
- Never provide fixes
- Encourage independent reasoning
- Adapt to all Python errors
"""

user_prompt = f"""
Code:
{student_code}

Error:
{error_type}: {error_message}

Ask only ONE Socratic debugging question.
"""

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.1,
    max_tokens=80
)

print("\nSTRICT SOCRATIC RESPONSE:\n")
print(response.choices[0].message.content)
