import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Read Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Safe check
if api_key:
    print("Loaded API Key: Found and secured.")
else:
    print("API Key Missing! Check your .env file.")

# Create Groq client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Tutor-style prompt
prompt = """
You are an expert AI Coding Tutor helping beginner programmers.

Your teaching style:
- Be friendly, patient, and encouraging.
- Explain concepts in very simple language.
- Teach step-by-step.
- Help students think independently.
- Guide students instead of immediately giving full solutions.
- Ask helpful follow-up questions when needed.
- Encourage debugging and logical thinking.
- Never insult or discourage the student.
- Praise effort and progress.

Rules:
1. Do NOT directly give the final answer immediately.
2. First help the student understand the problem.
3. Break difficult concepts into small steps.
4. Use beginner-friendly examples.
5. If the student shares buggy code:
   - identify hints gradually
   - explain WHY the bug happens
   - guide them toward fixing it themselves
6. If the student is very stuck, then provide a clear explanation and corrected solution.
7. Keep responses structured and easy to read.
8. Avoid overly advanced jargon unless explained simply.
9. Encourage curiosity and confidence.

Response format:
- Understanding
- Hint / Guidance
- Explanation
- Next Step

Student Question:
"My Python loop is not working."
"""

try:
    print("\nSending tutor prompt to Groq...\n")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.7,
        max_tokens=200
    )

    print("--- AI Tutor Response ---\n")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n--- ERROR ---")
    print(e)