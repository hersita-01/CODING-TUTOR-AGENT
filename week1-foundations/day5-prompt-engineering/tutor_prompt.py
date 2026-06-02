import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY is missing.")
    sys.exit(1)

# -----------------------------------
# CREATE GROQ CLIENT
# -----------------------------------

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# -----------------------------------
# SYSTEM PROMPT
# Defines behavior/personality
# -----------------------------------

system_prompt = """
You are an expert AI Coding Tutor.

Your teaching style:
- Friendly and patient
- Explain concepts simply
- Teach step-by-step
- Encourage logical thinking
- Help students debug independently
- Use beginner-friendly examples

Rules:
1. Do not immediately give the final answer.
2. Guide the learner first.
3. Explain WHY things happen.
4. Ask helpful follow-up questions.
5. Encourage curiosity and confidence.

Response format:

Understanding:
...

Hint:
...

Explanation:
...

Next Step:
...
"""

# -----------------------------------
# USER PROMPT
# Defines the task/question
# -----------------------------------

user_prompt = """
My Python loop is not working.
"""
#user_prompt = "What is a Python function?"
#user_prompt = "Why am I getting NameError?"

# -----------------------------------
# SEND REQUEST
# -----------------------------------

try:

    print("\nSending request to Groq...\n")

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.7,
        max_tokens=200
    )

    print("===== AI TUTOR RESPONSE =====\n")

    print(response.choices[0].message.content)

except Exception as e:

    print("\nERROR:")
    print(e)