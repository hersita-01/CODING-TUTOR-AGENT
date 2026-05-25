# tokens_test.py
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY is missing from your .env file.")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

prompt = "Explain Python loops in deep, comprehensive detail. Write at least three paragraphs."
model_name = "llama-3.1-8b-instant"

print("==================================================")
print("🧪 Running Groq Max Tokens Constraint Test")
print("==================================================\n")

try:
    print("Sending request with max_tokens set to 25...")
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=25  # Strict cutoff limit!
    )
    
    print("\n[Output constrained by max_tokens=25]:")
    print(response.choices[0].message.content)
    print("\n" + "-" * 50)
    
    # Check why the loop stopped generating
    finish_reason = response.choices[0].finish_reason
    print(f"Loop termination reason: {finish_reason}")
    print("*" * 50)
    
    if finish_reason == "length":
        print("💡 Notice how the sentence cut off abruptly? The 'length' reason")
        print("tells us Grok wanted to say more but hit our token wall.")

except Exception as e:
    print(f"Test Failed: {e}")
