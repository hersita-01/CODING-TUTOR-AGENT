import os
import sys
import time

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

MODEL_NAME = "llama-3.1-8b-instant"
MAX_TOKENS = 180

prompt = input("Ask the tutor a Python question: ").strip()
if not prompt:
    print("ERROR: Please enter a question.")
    sys.exit(1)

messages = [
    {
        "role": "system",
        "content": (
            "You are a concise Python tutor. Give one short explanation, "
            "then ask one Socratic follow-up question."
        ),
    },
    {"role": "user", "content": prompt},
]

try:
    started_at = time.time()
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.3,
        max_tokens=MAX_TOKENS,
        stream=True,
    )

    print("\nTutor response:\n")
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)

    elapsed = time.time() - started_at
    print(f"\n\nModel: {MODEL_NAME}")
    print(f"Max tokens requested: {MAX_TOKENS}")
    print(f"Elapsed time: {elapsed:.2f}s")

except Exception as exc:
    print("ERROR: Streaming tutor request failed.")
    print(exc)
