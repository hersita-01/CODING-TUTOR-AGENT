# -----------------------------------
# WEEK 3 - DAY 2
# ADVANCED TOOL SCHEMA SYSTEM
# -----------------------------------

import json

# -----------------------------------
# TOOL SCHEMA
# -----------------------------------

run_python_tool = {

    "type": "function",

    "function": {

        "name": "run_python",

        "description":
        (
            "Safely execute Python code written "
            "by a student inside a sandboxed "
            "environment and return execution "
            "results, output, or errors."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "code": {

                    "type": "string",

                    "description":
                    (
                        "The Python code submitted "
                        "by the learner."
                    )
                },

                "timeout_s": {

                    "type": "integer",

                    "description":
                    (
                        "Maximum execution time "
                        "before stopping execution."
                    ),

                    "default": 3,

                    "minimum": 1,

                    "maximum": 10
                },

                "capture_output": {

                    "type": "boolean",

                    "description":
                    (
                        "Whether standard output "
                        "should be captured. "
                        "Always True in this "
                        "implementation; reserved "
                        "for future use."
                    ),

                    "default": True
                }
            },

            "required": ["code"]
        }
    }
}

# -----------------------------------
# SAMPLE TOOL CALL
# -----------------------------------

sample_tool_call = {

    "tool_name": "run_python",

    "arguments": {

        "code":
        (
            "x = 10\n"
            "print(x + 5)"
        ),

        "timeout_s": 3,

        "capture_output": True
    }
}

# -----------------------------------
# DISPLAY TOOL SCHEMA
# -----------------------------------

print("\n===================================")
print("ADVANCED TOOL SCHEMA")
print("===================================\n")

print(json.dumps(run_python_tool, indent=4))

# -----------------------------------
# DISPLAY SAMPLE TOOL CALL
# -----------------------------------

print("\n===================================")
print("SAMPLE TOOL CALL")
print("===================================\n")

print(json.dumps(sample_tool_call, indent=4))

# -----------------------------------
# EXPLANATION SECTION
# -----------------------------------

print("\n===================================")
print("SCHEMA EXPLANATION")
print("===================================\n")

print("1. name              -> Tool identifier")
print("2. description       -> Explains tool purpose")
print("3. parameters        -> Accepted inputs")
print("4. required          -> Mandatory arguments")
print("5. default           -> Default parameter values")
print("6. minimum/maximum   -> Input validation")
print("7. capture_output    -> Controls output capture")

# -----------------------------------
# SIMULATED AI DECISION
# -----------------------------------

print("\n===================================")
print("AI TOOL DECISION")
print("===================================\n")

student_request = (
    "Run this Python program "
    "and show the output."
)

print("Student Request:")
print(student_request)

print("\nAI Decision:")
print(
    "The AI selects the "
    "'run_python' tool "
    "because code execution "
    "is required."
)

# -----------------------------------
# FINAL NOTE
# -----------------------------------

print("\n===================================")
print("DAY 2 LEARNING OUTCOME")
print("===================================\n")

print(
    "Today we learned how AI systems "
    "understand available tools using "
    "structured JSON schemas."
)