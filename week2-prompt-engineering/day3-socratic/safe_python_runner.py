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


def run_python_safely(code: str, timeout_s: int = 3) -> RunResult:
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
