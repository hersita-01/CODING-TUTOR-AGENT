# -----------------------------------
# WEEK 3 - DAY 3
# ADVANCED TOOL LOOP
# MULTILINE INPUT VERSION
# -----------------------------------

import subprocess
import tempfile
import os

# -----------------------------------
# TOOL
# -----------------------------------

def run_python(code, timeout_s=3):

    """
    Safely execute Python code
    inside a subprocess sandbox.
    """

    try:

        # Create temporary Python file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:

            temp_file.write(code)

            temp_path = temp_file.name

        # Run Python safely
        result = subprocess.run(

            ["python3", temp_path],

            capture_output=True,

            text=True,

            timeout=timeout_s
        )

        # Remove temporary file
        os.remove(temp_path)

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "error_type": "TimeoutError",
            "message":
            "Your program took too long to run."
        }

    except Exception as e:

        return {
            "success": False,
            "error_type": type(e).__name__,
            "message": str(e)
        }

# -----------------------------------
# AI CODING TUTOR
# -----------------------------------

print("\n===================================")
print("AI CODING TUTOR")
print("===================================")

# -----------------------------------
# MULTILINE INPUT
# -----------------------------------

print("\nPaste your Python code below.")
print("Press ENTER twice to finish.\n")

lines = []

blank_count = 0

while True:

    line = input()

    # Count blank lines
    if line == "":
        blank_count += 1
    else:
        blank_count = 0

    # Stop after two ENTER presses
    if blank_count == 2:
        break

    lines.append(line)

student_code = "\n".join(lines)

# -----------------------------------
# AI TOOL DECISION
# -----------------------------------

print("\n-----------------------------------")
print("AI Decision")
print("-----------------------------------")

print(
    "The tutor decided to use the "
    "'run_python' tool to analyze "
    "your code safely."
)

# -----------------------------------
# TOOL EXECUTION
# -----------------------------------

tool_result = run_python(student_code)

# -----------------------------------
# AI RESPONSE
# -----------------------------------

print("\n===================================")
print("AI TUTOR RESPONSE")
print("===================================\n")

# -----------------------------------
# SUCCESS CASE
# -----------------------------------

if tool_result["success"]:

    # Runtime error exists
    if tool_result["stderr"]:

        error_text = tool_result["stderr"]

        print(
            "Your program encountered an error.\n"
        )

        print("Python Error:\n")

        print(error_text)

        # -----------------------------------
        # SOCrATIC GUIDANCE
        # -----------------------------------

        if "NameError" in error_text:

            print("\nHint:")

            print(
                "A variable may have been "
                "used before being defined."
            )

            print("\nGuiding Question:")

            print(
                "Did you create every variable "
                "before using it?"
            )

        elif "TypeError" in error_text:

            print("\nHint:")

            print(
                "Two incompatible data types "
                "may be interacting."
            )

            print("\nGuiding Question:")

            print(
                "Are you combining numbers "
                "and strings together?"
            )

        elif "ZeroDivisionError" in error_text:

            print("\nHint:")

            print(
                "A number may be divided by zero."
            )

            print("\nGuiding Question:")

            print(
                "Can the denominator become zero?"
            )

        elif "IndexError" in error_text:

            print("\nHint:")

            print(
                "The program may be accessing "
                "an invalid list index."
            )

            print("\nGuiding Question:")

            print(
                "Does the index exist inside "
                "the list?"
            )

        else:

            print(
                "\nTry checking the line number "
                "mentioned in the error."
            )

    # Successful execution
    else:

        print(
            "Great! Your program executed "
            "successfully.\n"
        )

        print("Program Output:\n")

        print(tool_result["stdout"])

        print(
            "Your code completed without errors."
        )

# -----------------------------------
# TOOL FAILURE
# -----------------------------------

else:

    print(
        "The execution environment "
        "stopped the program safely.\n"
    )

    print(
        f"Error Type: "
        f"{tool_result['error_type']}"
    )

    print(
        f"Message: "
        f"{tool_result['message']}"
    )