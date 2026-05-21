import os
from google import genai
from dotenv import load_dotenv

# 1. Explicitly load the .env file from the current directory
load_dotenv(dotenv_path="./.env")

# 2. Extract the key manually using Python's os module
api_key_from_env = os.getenv("GEMINI_API_KEY")

# 3. Explicitly hand the key over to the Gemini client
client = genai.Client(api_key=api_key_from_env)

try:
    print("Sending secure request...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Give me a 1-sentence tip on secure coding.',
    )
    print("\n--- Success! ---")
    print(response.text)
    
except Exception as e:
    print("\n--- Something went wrong ---")
    print(e)