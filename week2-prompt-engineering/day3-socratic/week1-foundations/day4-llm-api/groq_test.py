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

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a patient Python tutor. Explain simply and end "
                    "with one question that helps the learner think."
                ),
            },
            {
                "role": "user",
                "content": "Why does Python use indentation instead of braces?",
            },
        ],
        temperature=0.4,
        max_tokens=180,
    )

    print(response.choices[0].message.content)

except Exception as exc:
    print("ERROR: Groq request failed.")
    print(exc)
