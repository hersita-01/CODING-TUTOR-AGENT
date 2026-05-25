import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read API key from .env
api_key = os.getenv("GROQ_API_KEY")

# Debug check
print("API Key Loaded:", api_key[:10], "...")

# Create Groq client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

try:
    print("\nSending request to Groq...\n")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": "Explain Python loops like I am 10 years old."
            }
        ],

        temperature=0.7,
        max_tokens=100
    )

    print("--- SUCCESS ---\n")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n--- ERROR ---")
    print(e)