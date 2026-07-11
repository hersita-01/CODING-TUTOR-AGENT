"""
rag_context_builder.py

Week 5 / Day 5 - Memory + RAG Integration
------------------------------------------
Retrieves relevant documentation chunks for a student's message using the
existing `rag_search()` tool (Week 5 / Day 3) and formats them for
injection into the tutor's prompt.

This module does not implement retrieval itself -- it is a thin,
presentation-focused wrapper around `rag_search_tool.rag_search()` so that
retrieval logic (embeddings, ChromaDB, chunking) stays owned entirely by
Day 2/3 and is never duplicated or modified here.

Import note
------------
The project's folder names (e.g. `week5-memory`, `day3-vector-store`)
contain hyphens and are therefore not valid Python package names
(`import week5-memory.day3-vector-store` is a SyntaxError). Consistent with
how cross-folder imports must already be done elsewhere in this codebase,
this module adds the sibling directory to `sys.path` at import time and
then imports `rag_search_tool` as a plain top-level module.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path bootstrap: make `week5-memory/day3-vector-store` importable
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WEEK5_DIR = os.path.dirname(_THIS_DIR)  # .../week5-memory
_DAY3_DIR = os.path.join(_WEEK5_DIR, "day3-vector-store")

if _DAY3_DIR not in sys.path:
    sys.path.insert(0, _DAY3_DIR)

try:
    from rag_search_tool import rag_search  # type: ignore
except ImportError as exc:  # pragma: no cover - defensive import guard
    logger.error(
        "Could not import rag_search from %s. Ensure day3-vector-store/"
        "rag_search_tool.py exists and exposes a `rag_search()` function. "
        "Error: %s",
        _DAY3_DIR,
        exc,
    )

    def rag_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:  # type: ignore
        """Fallback stub used only if the real rag_search_tool is missing.

        Returns an empty result set so the rest of the pipeline can still
        run (degraded, without retrieved documentation) instead of crashing.
        """
        logger.warning("rag_search fallback stub invoked -- no results returned.")
        return []


# Cap on how many chunks we ever inject into a prompt, regardless of what
# rag_search returns, to keep context windows small and relevant.
DEFAULT_TOP_K = 4
MAX_CHUNK_CHARS = 600


def _format_chunk(index: int, chunk: Dict[str, Any]) -> str:
    """Format a single retrieved chunk as a labeled, truncated snippet.

    Args:
        index: 1-based position of this chunk in the result list.
        chunk: A retrieval result. Expected (but defensively read) keys:
            "text" (str), "source" (str), "score" (float).

    Returns:
        A formatted string block for this chunk.
    """
    text = str(chunk.get("text", "")).strip()
    if len(text) > MAX_CHUNK_CHARS:
        text = text[:MAX_CHUNK_CHARS].rstrip() + "..."

    metadata = chunk.get("metadata")
    if isinstance(metadata, dict):
        source = chunk.get("source") or metadata.get("source")
    else:
        source = chunk.get("source")
    source = source or "unknown source"

    score = chunk.get("similarity")

    score_str = (
        f" (similarity: {score:.2f})"
        if isinstance(score, (int, float))
        else ""
    )

    return f"[{index}] Source: {source}{score_str}\n{text}"


def build_rag_context(student_message: str, top_k: int = DEFAULT_TOP_K) -> str:
    """Retrieve and format documentation relevant to a student's message.

    This is the single public entry point for Day 5's RAG requirement. It:
        1. Calls the existing `rag_search()` tool with the student's message.
        2. Retrieves the top-k relevant chunks.
        3. Formats them into a labeled block suitable for prompt injection.

    Args:
        student_message: The raw message/question from the student.
        top_k: Maximum number of chunks to retrieve and include.

    Returns:
        A formatted string block ready for injection into the tutor prompt.
        Returns a clear "no documentation found" message if retrieval
        yields nothing, rather than an empty string, so the calling prompt
        is never silently missing a section.

    Example:
        >>> context = build_rag_context("Why does my for loop skip the last item?")
        >>> print(context)
        ## Relevant Documentation
        [1] Source: python_loops.md (similarity: 0.87)
        A for loop in Python iterates ...
    """
    if not student_message or not student_message.strip():
        logger.warning("build_rag_context called with empty student_message")
        return "## Relevant Documentation\nNo query provided; skipping retrieval."

    try:
        results = rag_search(student_message, top_k=top_k)
    except TypeError:
        # In case the existing rag_search() signature doesn't accept top_k.
        logger.debug("rag_search() does not accept top_k; retrying without it.")
        results = rag_search(student_message)
    except Exception:  # noqa: BLE001 - retrieval must never crash the tutor
        logger.exception("rag_search() raised an exception during retrieval.")
        results = []

    if not results.get("success", False):
        logger.info(
            "No RAG results found for message: %.60s",
            student_message,
        )

        return (
            "## Relevant Documentation\n"
            "No directly relevant documentation was found for this question. "
            "Rely on general Python knowledge and Socratic questioning."
        )

    chunks = results.get("chunks", [])

    valid_chunks = [
        chunk
        for chunk in chunks[:top_k]
        if isinstance(chunk, dict)
    ]

    if not valid_chunks:
        logger.warning(
            "rag_search returned no valid chunks for message: %.60s",
            student_message,
        )

        return (
            "## Relevant Documentation\n"
            "No valid documentation chunks were returned. "
            "Rely on general Python knowledge and Socratic questioning."
        )

    formatted_chunks = [
        _format_chunk(i, chunk)
        for i, chunk in enumerate(valid_chunks, start=1)
    ]

    context = "## Relevant Documentation\n" + "\n\n".join(
        formatted_chunks
    )

    logger.debug(
        "Built RAG context from %d chunk(s) (%d chars total)",
        len(formatted_chunks),
        len(context),
    )

    return context
    