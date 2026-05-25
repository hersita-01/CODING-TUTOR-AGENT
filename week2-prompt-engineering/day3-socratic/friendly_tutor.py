import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY is missing from your .env file.")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

question = input("What Python concept should the tutor explain? ").strip()
if not question:
    print("ERROR: Please enter a Python concept or question.")
    sys.exit(1)

system_prompt = """
You are a friendly Python tutor for beginners.

Rules:
- Explain in simple language
- Use one tiny example
- Avoid advanced jargon
- End with one check-your-understanding question
"""

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ],
    temperature=0.4,
    max_tokens=220,
)

print("\nFRIENDLY TUTOR RESPONSE:\n")
print(response.choices[0].message.content)
