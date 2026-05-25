
# -----------------------------------
# Enter programming language:
#python
#Paste your code below:
#age = "20"
#print(age + 5)
#Enter the error message:
#TypeError: can only concatenate str (not "int") to str
# -----------------------------------

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY is missing from your .env file.")
    sys.exit(1)

# -----------------------------------
# CREATE GROQ CLIENT
# -----------------------------------

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# -----------------------------------
# USER INPUT
# -----------------------------------

language = input("Enter programming language: ")

print("\nPaste your code below:")
student_code = input()

error_message = input("\nEnter the error message: ")

if not language.strip() or not student_code.strip() or not error_message.strip():
    print("ERROR: Language, code, and error message are all required.")
    sys.exit(1)

# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------

system_prompt = f"""
You are a patient and beginner-friendly {language} programming tutor.

Your task is to explain programming errors clearly for beginners.

Rules:
- Be calm and encouraging
- Avoid difficult jargon
- Explain what the error means
- Explain why the error happened
- Never directly provide the final corrected code
- Keep explanations beginner-friendly
- End with one guiding question
- Remind the student that debugging is a normal part of programming
"""

# -----------------------------------
# USER PROMPT
# -----------------------------------

user_prompt = f"""
Programming Language:
{language}

Student Code:
{student_code}

Error Message:
{error_message}

Explain this error simply for a beginner programmer.
"""

# -----------------------------------
# API CALL
# -----------------------------------

try:

    print("\nAnalyzing error with AI tutor...\n")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=250
    )

    print("----- AI Tutor Explanation -----\n")

    print(response.choices[0].message.content)

except Exception as e:

    print("\n----- ERROR -----")
    print(e)
