# -----------------------------------
# WEEK 3 - DAY 1
# ADVANCED TOOL USE INTRO
# -----------------------------------

import traceback
import sys
import io

# -----------------------------------
# TOOL
# -----------------------------------

def run_python(code):

    """
    Executes Python code safely
    and returns structured results.
    """

    result = {
        "success": False,
        "output": "",
        "error_type": None,
        "error_message": None
    }

    try:

        # Redirect stdout to capture print() output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        local_scope = {}
        exec(code, {}, local_scope)

        # Restore stdout and read captured output
        sys.stdout = sys.__stdout__
        printed = captured_output.getvalue()

        result["success"] = True
        result["output"] = (
            printed if printed.strip()
            else "Code executed successfully."
        )

    except Exception as e:

        sys.stdout = sys.__stdout__
        result["error_type"] = type(e).__name__
        result["error_message"] = str(e)

    return result


# -----------------------------------
# USER INPUT
# -----------------------------------

print("Paste Python code below.")
print("Press ENTER twice when finished.\n")

lines = []
blank_count = 0

while True:

    line = input()

    if line == "":
        blank_count += 1
    else:
        blank_count = 0

    if blank_count == 2:
        break

    lines.append(line)

student_code = "\n".join(lines)

# -----------------------------------
# TOOL LOOP SIMULATION
# -----------------------------------

print("\n-----------------------------------")
print("AI DECIDES TO USE TOOL: run_python")
print("-----------------------------------")

tool_result = run_python(student_code)

# -----------------------------------
# FINAL RESULT
# -----------------------------------

print("\n-----------------------------------")
print("TOOL RESULT")
print("-----------------------------------")

if tool_result["success"]:

    print("STATUS : SUCCESS")
    print("OUTPUT :", tool_result["output"])

else:

    print("STATUS        : FAILED")
    print("ERROR TYPE    :", tool_result["error_type"])
    print("ERROR MESSAGE :", tool_result["error_message"])

# -----------------------------------
# AI RESPONSE SIMULATION
# -----------------------------------

print("\n-----------------------------------")
print("AI TUTOR RESPONSE")
print("-----------------------------------")

if tool_result["success"]:

    print("Your code executed successfully.")

else:

    print(
        f"The program encountered a "
        f"{tool_result['error_type']}."
    )

    print(
        "Try checking the part of your "
        "code related to this error."
    )