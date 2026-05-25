import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Create Groq client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Example buggy code
buggy_code = """
numbers = [1, 2, 3]
print(numbers[5])
"""

# Example error message
error_message = "IndexError: list index out of range"

# System prompt
system_prompt = """
You are a beginner-friendly Python coding tutor.

Your job is to explain Python errors in simple English.

Rules:
- Be calm, supportive, and encouraging
- Avoid difficult technical jargon
- Explain what Python is complaining about
- Explain why the error happened conceptually
- Never directly provide the corrected code
- Keep explanations short and beginner-friendly
- Encourage the student to think independently
- End with one guiding question
- Remind the student that debugging is a normal part of programming
"""

# User prompt
user_prompt = f"""
Code:
{buggy_code}

Error:
{error_message}

Explain this error simply for a beginner.
"""

try:
    print("Sending Bug Explainer request to Groq...\n")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )

    print("--- AI Bug Explanation ---\n")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n--- ERROR ---")
    print(e)