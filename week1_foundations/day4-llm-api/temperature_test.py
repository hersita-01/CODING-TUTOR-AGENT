# temperature_test.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load the environment file
load_dotenv(dotenv_path="./.env")

# 2. Read the key using your exact spelling
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY is missing from your .env file!")
    exit(1)

# 3. Initialize the client to target the GROQ platform instead of xAI
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

prompt = "Write a one-sentence tagline for a coffee brand made for programmers."
model_name = "llama-3.1-8b-instant"  # Super fast model on Groq's platform

print("==================================================")
print("🧪 Running Groq Temperature Comparison Test")
print("==================================================\n")

# --- TEST 1: Low Temperature (Precise, Focused, Predictable) ---
try:
    print(f"Sending Request 1 to Groq using {model_name} (Temp = 0.0)...")
    response_cold = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    print("\n[Low Temperature Output (0.0)]:")
    print(response_cold.choices[0].message.content)
    print("-" * 50)
    
except Exception as e:
    print(f"Test 1 Failed: {e}")

# --- TEST 2: High Temperature (Creative, Fluid, Varied) ---
try:
    print(f"\nSending Request 2 to Groq using {model_name} (Temp = 1.0)...")
    response_hot = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )
    print("\n[High Temperature Output (1.0)]:")
    print(response_hot.choices[0].message.content)
    print("=" * 50)

except Exception as e:
    print(f"Test 2 Failed: {e}")
