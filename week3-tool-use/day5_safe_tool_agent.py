# -----------------------------------
# WEEK 3 - DAY 5
# SAFE MULTI-TOOL AI CODING TUTOR
# FINAL IMPROVED VERSION
# -----------------------------------

import subprocess
import tempfile
import os

# -----------------------------------
# TOOL 1 : RUN PYTHON
# -----------------------------------

def run_python(code, timeout_s=3):

    # Handle missing input
    if not code.strip():

        return {
            "success": False,
            "error":
            "No Python code was provided."
        }

    try:

        # Create temporary Python file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:

            temp_file.write(code)

            temp_path = temp_file.name

        # Safe subprocess execution
        result = subprocess.run(

            ["python3", temp_path],

            capture_output=True,

            text=True,

            timeout=timeout_s
        )

        # Delete temp file
        os.remove(temp_path)

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    # Infinite loop protection
    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "error":
            "Execution stopped: possible infinite loop detected."
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

# -----------------------------------
# TOOL 2 : LINT CODE
# -----------------------------------

def lint_code(code):

    if not code.strip():

        return {
            "success": False,
            "error":
            "No code was provided for linting."
        }

    try:

        # Create temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:

            temp_file.write(code)

            temp_path = temp_file.name

        # Run Ruff linter
        result = subprocess.run(

            [
                "ruff",
                "check",
                temp_path,
                "--select",
                "E,F,W"
            ],

            capture_output=True,

            text=True
        )

        os.remove(temp_path)

        return {
            "success": True,
            "lint_output": result.stdout,
            "lint_error": result.stderr
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

# -----------------------------------
# TOOL 3 : DOC SEARCH
# -----------------------------------

def doc_search(keyword):

    if not keyword.strip():

        return {
            "success": False,
            "error":
            "No keyword provided."
        }

    python_docs = {

        "list":
        "Lists store multiple items in order.",

        "dictionary":
        "Dictionaries store key-value pairs.",

        "function":
        "Functions organize reusable code.",

        "loop":
        "Loops repeat code multiple times.",

        "for loop":
        "For loops iterate over sequences.",

        "while loop":
        "While loops run until a condition changes.",

        "try":
        "try-except handles runtime errors.",

        "enumerate":
        (
            "enumerate() gives both index "
            "and value during iteration."
        ),

        "tuple":
        "Tuples store ordered immutable data.",

        "set":
        "Sets store unique unordered values.",

        "class":
        "Classes are blueprints for objects.",

        "inheritance":
        "Inheritance allows one class to reuse another class.",

        "exception":
        "Exceptions are runtime errors in Python.",

        "string":
        "Strings store text data.",

        "integer":
        "Integers store whole numbers.",

        "float":
        "Floats store decimal numbers."
    }

    keyword = keyword.lower()

    matches = []

    # Search related topics
    for topic, explanation in python_docs.items():

        if keyword in topic:

            matches.append(
                {
                    "topic": topic,
                    "explanation": explanation
                }
            )

    # No results
    if not matches:

        return {
            "success": True,
            "results":
            ["No matching documentation found."]
        }

    return {
        "success": True,
        "results": matches
    }

# -----------------------------------
# TOOL REGISTRY
# -----------------------------------

TOOLS = {

    "run_python": run_python,

    "lint_code": lint_code,

    "doc_search": doc_search
}

# -----------------------------------
# TOOL EXECUTOR
# -----------------------------------

def execute_tool(tool_name, argument):

    # Prevent hallucinated tools
    if tool_name not in TOOLS:

        return {
            "success": False,
            "error":
            f"Unknown tool: {tool_name}"
        }

    try:

        tool_function = TOOLS[tool_name]

        return tool_function(argument)

    except Exception as e:

        return {
            "success": False,
            "error":
            f"Tool crashed: {str(e)}"
        }

# -----------------------------------
# MULTILINE INPUT
# -----------------------------------

def get_multiline_input():

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

    return "\n".join(lines)

# -----------------------------------
# AI CODING TUTOR
# -----------------------------------

print("\n===================================")
print("SAFE AI CODING TUTOR")
print("===================================")

print("\nAvailable Tools:\n")

print("1. run_python")
print("2. lint_code")
print("3. doc_search")

choice = input("\nSelect tool: ")

# -----------------------------------
# TOOL MAPPING
# -----------------------------------

tool_mapping = {

    "1": "run_python",

    "2": "lint_code",

    "3": "doc_search"
}

tool_name = tool_mapping.get(choice)

# Invalid selection
if not tool_name:

    print("\nInvalid tool selection.")
    exit()

# -----------------------------------
# USER INPUT
# -----------------------------------

if tool_name == "doc_search":

    argument = input(
        "\nEnter Python topic: "
    )

else:

    argument = get_multiline_input()

# -----------------------------------
# TOOL EXECUTION
# -----------------------------------

print(f"\nAI selects tool: {tool_name}")

result = execute_tool(
    tool_name,
    argument
)

# -----------------------------------
# FINAL RESPONSE
# -----------------------------------

print("\n===================================")
print("AI RESPONSE")
print("===================================\n")

if result["success"]:

    # -----------------------------------
    # RUN PYTHON OUTPUT
    # -----------------------------------

    if tool_name == "run_python":

        if result["stderr"]:

            print("Python Error:\n")

            print(result["stderr"])

            # Beginner hints
            error_text = result["stderr"]

            if "NameError" in error_text:

                print("\nHint:")

                print(
                    "A variable may have been "
                    "used before being defined."
                )

            elif "TypeError" in error_text:

                print("\nHint:")

                print(
                    "You may be combining "
                    "incompatible data types."
                )

            elif "ZeroDivisionError" in error_text:

                print("\nHint:")

                print(
                    "A number cannot be "
                    "divided by zero."
                )

            elif "IndexError" in error_text:

                print("\nHint:")

                print(
                    "The list index may "
                    "not exist."
                )

            elif "SyntaxError" in error_text:

                print("\nHint:")

                print(
                    "There may be a typo "
                    "or missing symbol."
                )

        else:

            print("Program Output:\n")

            print(result["stdout"])

            print(
                "Your code executed successfully."
            )

    # -----------------------------------
    # LINT OUTPUT
    # -----------------------------------

    elif tool_name == "lint_code":

        if result["lint_output"]:

            print("Lint Analysis:\n")

            print(result["lint_output"])

        else:

            print(
                "All checks passed successfully."
            )

    # -----------------------------------
    # DOC SEARCH OUTPUT
    # -----------------------------------

    elif tool_name == "doc_search":

        print("Documentation Results:\n")

        for item in result["results"]:

            if isinstance(item, dict):

                print(
                    f"Topic: {item['topic']}"
                )

                print(
                    f"Explanation: "
                    f"{item['explanation']}"
                )

                print()

            else:

                print(item)

# -----------------------------------
# ERROR HANDLING
# -----------------------------------

else:

    print("Error:\n")

    print(result["error"])

# -----------------------------------
# FINAL MESSAGE
# -----------------------------------

print("\n===================================")

print(
    "Debugging is a normal part "
    "of programming."
)

print(
    "Keep experimenting and learning!"
)

print("===================================")