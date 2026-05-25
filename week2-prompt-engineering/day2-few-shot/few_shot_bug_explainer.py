import os
import signal
import sys
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------------
# LOAD API KEY & INITIALIZE CLIENT
# -----------------------------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file.")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Operational security blocks to safe-keep your hosting platform hardware
blocked_keywords = [
    "os.remove", "os.rmdir", "os.system", "shutil", 
    "subprocess", "sys.exit", "open", "eval("
]

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution exceeded the safety limits (3-second timeout).")

# -----------------------------------
# GET STUDENT CODE VIA CONSECUTIVE DOUBLE ENTER
# -----------------------------------
print("\n======================================================================")
print("🐍 Socratic Python Tutor Sandbox Engine (Consecutive Double Enter)")
print("======================================================================")
print("Paste your Python code below.")
print("👉 Press ENTER twice consecutively on a blank line to execute.\n")

lines = []
blank_count = 0

while True:
    line = input()
    
    # Check if the line is completely empty (just an Enter keypress)
    if line.strip() == "":
        blank_count += 1
    else:
        # Reset the counter if they typed actual code characters
        blank_count = 0
        
    # If they hit Enter consecutively twice, break out!
    if blank_count == 2:
        break
        
    lines.append(line)

student_code = "\n".join(lines)

# Check Empty Input
if not student_code.strip():
    print("\n❌ ERROR: No code entered. Aborting session.")
    sys.exit(1)

# Security Keyword Screening
for keyword in blocked_keywords:
    if keyword in student_code:
        print(f"\n⚠️ Security Block: Unsupported system keyword detected ('{keyword}').")
        sys.exit(1)

if "input(" in student_code:
    print("\n⚠️ Input Constraint: Interactive input() workflows are not supported yet.")
    sys.exit(1)

# -----------------------------------
# CODE VALIDATION & EXECUTION ENGINE
# -----------------------------------
error_type = ""
error_message = ""
line_number = "Unknown"

try:
    print("\n🔨 Compiling and evaluating your code structures...")
    
    # 1. Catch structural compilation errors (SyntaxError, IndentationError)
    compiled_code = compile(student_code, "<string>", "exec")

    # 2. Arm the hardware execution safety timer (3 seconds max runtime)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(3)

    # 3. Execute inside an isolated scope map
    local_scope = {}
    exec(compiled_code, {}, local_scope)

    # 4. Disarm the timer safely if code completes
    signal.alarm(0)

    print("\n✅ Execution Success: No errors found during tracking analysis.")
    print("Keep in mind, hidden logical or structural bugs might still exist!")
    sys.exit(0)

except (SyntaxError, IndentationError) as se:
    # Catch syntax/tab tracking blocks before execution starts
    signal.alarm(0)
    error_type = type(se).__name__
    error_message = se.msg
    line_number = se.lineno

except Exception as e:
    # Catch active runtime faults (NameError, TypeError, IndexError, etc.)
    signal.alarm(0)
    error_type = type(e).__name__
    error_message = str(e)
    
    # Climb down the traceback framework stack mapping to find the user's line fault
    exc_type, exc_obj, exc_tb = sys.exc_info()
    if exc_tb is not None:
        tb = exc_tb
        while tb.tb_next:
            tb = tb.tb_next
        line_number = tb.tb_lineno

# -----------------------------------
# DISPLAY LOCAL DIAGNOSTIC RESULTS
# -----------------------------------
print("\n--------------------------------------------------")
print("🚨 INTERCEPTED CODE FAULT STATUS")
print("--------------------------------------------------")
print(f"Exception Class : {error_type}")
print(f"Fault Details   : {error_message}")
print(f"Target Line     : Line {line_number}")

# -----------------------------------
# SYSTEM ENGINE RULES & TARGETED AI GENERATION
# -----------------------------------
system_prompt = """You are a supportive, insightful Python tutor focused on the Socratic method.
Your goal is to help students learn how to debug by guiding their thought process, not by giving away the solution.

Follow these strict operational constraints:
1. Briefly summarize the error class in warm, beginner-friendly terms (e.g., "NameError means Python looked for a name it doesn't recognize").
2. Explain specifically why this happens in reference to their line location context.
3. NEVER provide explicit blocks of corrected code or complete fixed lines.
4. Conclude your statement by asking exactly ONE targeted debugging question designed to challenge their code's structural logic."""

user_prompt = f"""Student Source Code:
\"\"\"
{student_code}
\"\"\"

Exception Class: {error_type}
Fault Details: {error_message}
Trigger Line Location: Line {line_number}

Tasks:
1. Explain what this error class signifies simply.
2. Explain why it failed on Line {line_number}.
3. Ask one clean, tailored question to spark discovery."""

# -----------------------------------
# DELIVER DATA TO GROQ INFERENCE WEB
# -----------------------------------
try:
    print("\n🤖 Consulting Socratic Agent for review...\n")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,   # Precision deterministic weighting
        max_tokens=220     # Room for expressive Socratic dialogue
    )

    print("----------------------------------------------------------------------")
    print("💡 AI SOCRATIC TUTOR RESPONSE")
    print("----------------------------------------------------------------------\n")
    print(response.choices[0].message.content)
    print("\n======================================================================")

except Exception as api_err:
    print("\n❌ API Communication Error encountered during generation:")
    print(api_err)