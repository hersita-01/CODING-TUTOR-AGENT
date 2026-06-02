import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    ok: bool
    error_type: str = ""
    error_message: str = ""
    output: str = ""


# SECURITY VALIDATION
# Blocks dangerous student-code patterns before compilation or execution.
BLOCKED_PATTERNS = [
    "import os",
    "import subprocess",
    "import shutil",
    "os.remove",
    "os.rmdir",
    "os.system",
    "shutil.rmtree",
    "eval(",
    "exec(",
]


def run_python_safely(code: str, timeout_s: int = 3) -> RunResult:
    # SECURITY VALIDATION
    # Compact matching catches simple spacing tricks such as "import    os".
    compact_code = "".join(code.split())
    for pattern in BLOCKED_PATTERNS:
        compact_pattern = "".join(pattern.split())
        if compact_pattern in compact_code:
            return RunResult(
                ok=False,
                error_type="SecurityViolation",
                error_message=(
                    f"Detected forbidden operation: {pattern}. "
                    "This tutor only allows safe programming exercises."
                ),
            )

    # SECURITY VALIDATION
    # Syntax is checked before execution so invalid code never reaches subprocess.run.
    try:
        compile(code, "<student_code>", "exec")
    except SyntaxError as syntax_error:
        return RunResult(
            ok=False,
            error_type="SyntaxError",
            error_message=str(syntax_error),
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        script_path = Path(temp_dir) / "student_code.py"
        script_path.write_text(code, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=temp_dir,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                ok=False,
                error_type="TimeoutError",
                error_message=f"Code ran for more than {timeout_s} seconds.",
            )

    output = (completed.stdout + completed.stderr).strip()
    if completed.returncode == 0:
        return RunResult(ok=True, output=output)

    error_type = "RuntimeError"
    error_message = output.splitlines()[-1] if output else "Python exited with an error."

    if ": " in error_message:
        possible_type, message = error_message.split(": ", 1)
        if possible_type.endswith("Error") or possible_type.endswith("Exception"):
            error_type = possible_type
            error_message = message

    return RunResult(
        ok=False,
        error_type=error_type,
        error_message=error_message,
        output=output,
    )
