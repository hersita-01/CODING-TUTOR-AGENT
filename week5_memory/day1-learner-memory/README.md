# -----------------------------------
# WEEK 5 – MEMORY SUBSYSTEM
# week5-memory/ memory_aware_runner.py
#
# Thin wrapper around Week 2's run_python_safely() that
# automatically updates the learner's memory profile after
# every code execution.
#
# Week 2 safe_python_runner.py is NOT modified.
# This file owns all Week 5 concerns.
#
# Usage (from week4_mini_tutor.py or any future module):
#
#   from memory_aware_runner import run_and_remember
#
#   result = run_and_remember(
#       code         = student_code,
#       learner_name = "alice",
#       topic        = "for loops",   # optional
#       timeout_s    = 5,             # forwarded to run_python_safely
#   )
#   # result is the same RunResult as run_python_safely() returns
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

log = logging.getLogger("week5.memory_aware_runner")


# ============================================================
# WEEK 2 IMPORT
# Mirrors the same path-resolution pattern used in week4_mini_tutor.py.
# ============================================================

_here = Path(__file__).resolve().parent          # week5-memory/
_root = _here.parent                             # CODING-TUTOR-AGENT/

_w2_path = _root / "week2-prompt-engineering" / "day3-socratic"
if _w2_path.exists() and str(_w2_path) not in sys.path:
    sys.path.insert(0, str(_w2_path))

try:
    from safe_python_runner import run_python_safely, RunResult
    _WEEK2_AVAILABLE = True
    log.debug("Week 2 safe_python_runner loaded.")
except ImportError:
    _WEEK2_AVAILABLE = False
    log.warning("safe_python_runner.py not found — run_and_remember will raise.")


# ============================================================
# WEEK 5 MEMORY IMPORT
# ============================================================

if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

from memory_manager import MemoryManager

_memory_manager = MemoryManager()


# ============================================================
# PUBLIC API
# ============================================================

def run_and_remember(
    code:         str,
    learner_name: str,
    topic:        str = "",
    **kwargs: Any,
) -> "RunResult":
    """Execute Python code and record the outcome in the learner's profile.

    This is a drop-in replacement for run_python_safely() that adds
    automatic memory tracking.  All keyword arguments are forwarded
    to run_python_safely() unchanged (e.g. timeout_s, user_input).

    Parameters
    ----------
    code:
        Python source code to execute.
    learner_name:
        The learner's name.  Used to load or create their profile.
    topic:
        Optional topic label for this execution (e.g. "for loops").
        Recorded in recent_topics; also linked to any error that occurs.
    **kwargs:
        Forwarded verbatim to run_python_safely().

    Returns
    -------
    RunResult
        Exactly the same object run_python_safely() would return.
        The caller does not need to change how it reads the result.

    Raises
    ------
    ImportError
        If safe_python_runner.py cannot be found.
    """
    if not _WEEK2_AVAILABLE:
        raise ImportError(
            "safe_python_runner.py not found. "
            "Ensure it is at week2-prompt-engineering/day3-socratic/."
        )

    # ── Run the code (Week 2 handles all security, AST, timeout) ──────────
    result: RunResult = run_python_safely(code, **kwargs)

    # ── Update learner memory (Week 5 concern only) ────────────────────────
    try:
        profile = _memory_manager.get_or_create(learner_name)
        _memory_manager.update_from_run_result(
            profile    = profile,
            error_type = getattr(result, "error_type",    "") or "",
            error_msg  = getattr(result, "error_message", "") or "",
            topic      = topic,
            success    = getattr(result, "ok", False),
        )
    except Exception as exc:
        # Memory failure must never surface to the caller.
        log.warning(
            "Memory update failed for '%s' (topic=%r): %s",
            learner_name, topic, exc,
        )

    return result