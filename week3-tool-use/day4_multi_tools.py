# -----------------------------------
# WEEK 3 - DAY 4
# MULTI-TOOL AI CODING TUTOR
# -----------------------------------

import subprocess
import tempfile
import os

# -----------------------------------
# TOOL 1 : RUN PYTHON
# -----------------------------------

def run_python(code, timeout_s=3):

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:

            temp_file.write(code)

            temp_path = temp_file.name

        result = subprocess.run(

            ["python3", temp_path],

            capture_output=True,

            text=True,

            timeout=timeout_s
        )

        os.remove(temp_path)

        return {
            "tool": "run_python",
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:

        return {
            "tool": "run_python",
            "error":
            "Code execution timed out."
        }

# -----------------------------------
# TOOL 2 : LINT CODE
# -----------------------------------

def lint_code(code):

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:

            temp_file.write(code)

            temp_path = temp_file.name

        result = subprocess.run(

            ["ruff", "check", temp_path],

            capture_output=True,

            text=True
        )

        os.remove(temp_path)

        return {
            "tool": "lint_code",
            "lint_output": result.stdout,
            "lint_error": result.stderr
        }

    except Exception as e:

        return {
            "tool": "lint_code",
            "error": str(e)
        }

# -----------------------------------
# TOOL 3 : DOC SEARCH
# -----------------------------------

def doc_search(keyword):

    python_docs = {

        "list":
        "Lists store multiple items in order.",

        "dictionary":
        "Dictionaries store key-value pairs.",

        "for loop":
        "For loops repeat code over sequences.",

        "function":
        "Functions help organize reusable code.",

        "enumerate":
        (
            "enumerate() gives both index "
            "and value during iteration."
        ),

        "try":
        (
            "try-except handles runtime errors."
        )
    }

    result = python_docs.get(

        keyword.lower(),

        "No matching documentation found."
    )

    return {
        "tool": "doc_search",
        "result": result
    }

# -----------------------------------
# AI CODING TUTOR
# -----------------------------------

print("\n===================================")
print("AI CODING TUTOR")
print("===================================")

print("\nChoose an option:\n")

print("1. Run Python Code")
print("2. Lint Python Code")
print("3. Search Python Docs")

choice = input("\nEnter choice: ")

# -----------------------------------
# TOOL 1
# -----------------------------------

if choice == "1":

    print("\nPaste Python code below.")
    print("Press ENTER twice to finish.\n")

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

    print("\nAI selects tool: run_python")

    result = run_python(student_code)

    print("\n===================================")
    print("TOOL RESULT")
    print("===================================\n")

    if result.get("stderr"):

        print("Your code produced an error:\n")

        print(result["stderr"])

    else:

        print("Program Output:\n")

        print(result["stdout"])

# -----------------------------------
# TOOL 2
# -----------------------------------

elif choice == "2":

    print("\nPaste Python code below.")
    print("Press ENTER twice to finish.\n")

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

    print("\nAI selects tool: lint_code")

    result = lint_code(student_code)

    print("\n===================================")
    print("LINT RESULT")
    print("===================================\n")

    print(result["lint_output"])

# -----------------------------------
# TOOL 3
# -----------------------------------

elif choice == "3":

    keyword = input(
        "\nEnter Python topic: "
    )

    print("\nAI selects tool: doc_search")

    result = doc_search(keyword)

    print("\n===================================")
    print("DOCUMENTATION RESULT")
    print("===================================\n")

    print(result["result"])

# -----------------------------------
# INVALID OPTION
# -----------------------------------

else:

    print("\nInvalid option selected.")