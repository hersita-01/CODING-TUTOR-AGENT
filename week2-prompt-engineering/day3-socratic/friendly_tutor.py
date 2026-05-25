import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

print("Paste Python code. Type END to finish.\n")

lines = []

while True:

    line = input()

    if line.strip() == "END":
        break

    lines.append(line)

student_code = "\n".join(lines)

try:

    compile(student_code, "<string>", "exec")
    exec(student_code)

    print("No runtime errors detected.")
    exit()

except Exception as e:

    error_type = type(e).__name__
    error_message = str(e)

system_prompt = """
You are a supportive and encouraging Python tutor.

Rules:
- Help students feel comfortable
- Normalize mistakes
- Use beginner-friendly language
- Ask one guiding question
- Adapt to all Python errors
"""

user_prompt = f"""
Code:
{student_code}

Error:
{error_type}: {error_message}

Explain kindly and ask one supportive Socratic question.
"""

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)

print("\nFRIENDLY RESPONSE:\n")
print(response.choices[0].message.content)