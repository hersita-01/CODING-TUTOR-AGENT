# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ rag_search_tool.py
#
# Semantic search over the ChromaDB vector store.
#
# Public API:
#   rag_search(query, top_k=5) -> dict
#
# Designed to be plugged into tool_dispatcher on Day 5 with zero
# changes to this file — the function signature and return schema
# are intentionally stable.
#
# Mirrors the architecture of Week 3's doc_search_tool.py but
# uses local ChromaDB instead of internet requests.
# -----------------------------------

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("week5.rag_search_tool")

# ── Path setup ────────────────────────────────────────────────────────
_here  = Path(__file__).resolve().parent
_day2  = _here.parent / "day2-embeddings"
_week5 = _here.parent

for _p in [str(_here), str(_day2), str(_week5)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chroma_manager    import ChromaManager
from embedding_manager import EmbeddingManager


# ============================================================
# MODULE-LEVEL SINGLETONS
# Loaded once and reused across all calls — avoids reloading
# the embedding model on every search.
# ============================================================

_embedder : Optional[EmbeddingManager] = None
_chroma   : Optional[ChromaManager]   = None


def _get_embedder() -> EmbeddingManager:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingManager()
    return _embedder


def _get_chroma() -> ChromaManager:
    global _chroma
    if _chroma is None:
        _chroma = ChromaManager()
    return _chroma


# ============================================================
# PUBLIC API
# ============================================================

def rag_search(
    query:          str,
    top_k:          int            = 5,
    topic:          Optional[str]  = None,
    difficulty:     Optional[str]  = None,
    min_similarity: float          = 0.0,
) -> dict[str, Any]:
    """Perform semantic search over the indexed Python tutorial corpus.

    Embeds the query using EmbeddingManager (Day 2), queries ChromaDB
    (Day 3), and returns a structured result ready for injection into
    a tutor system prompt or tool response.

    Parameters
    ----------
    query:
        The natural language question or error message to search for.
    top_k:
        Maximum number of results to return.
    topic:
        Optional topic filter (e.g. ``"loops"``).  Only chunks with
        matching ``topic`` metadata are returned.
    difficulty:
        Optional difficulty filter (e.g. ``"beginner"``).
    min_similarity:
        Optional minimum similarity threshold in [0, 1].  Chunks whose
        similarity (1 - cosine_distance) falls below this value are
        discarded.  Defaults to 0.0 (no filtering).

    Returns
    -------
    dict with keys:
        success   (bool)       — True if at least one result found
        query     (str)        — the original query
        chunks    (list[dict]) — retrieved chunks with text + metadata
        sources   (list[str])  — unique source filenames
        summary   (str)        — human-readable summary of results
        error     (str)        — populated only on failure
    """
    if not query or not query.strip():
        return _failure_result(query or "", "Query must be a non-empty string.")

    embedder = _get_embedder()
    chroma   = _get_chroma()

    # ── 1. Embed the query ────────────────────────────────────────────
    query_vec = embedder.embed_text(query.strip())
    if not query_vec:
        return _failure_result(query, "Failed to embed query — empty vector returned.")

    # ── 2. Build optional metadata filter ────────────────────────────
    where = _build_metadata_filter(topic=topic, difficulty=difficulty)

    # ── 3. Query ChromaDB ─────────────────────────────────────────────
    raw = chroma.query(query_embedding=query_vec, top_k=top_k, where=where)

    if not raw["documents"]:
        return _failure_result(
            query,
            "No results found. Ensure documents have been indexed via ingest_documents.py."
        )

    # ── 4. Build structured result (apply similarity threshold) ───────
    chunks: list[dict[str, Any]] = []
    sources: set[str]            = set()

    for doc, meta, dist in zip(
        raw["documents"], raw["metadatas"], raw["distances"]
    ):
        similarity = round(1.0 - float(dist), 4)
        # ChromaDB cosine distance: 0=identical, 1=orthogonal
        # similarity = 1 - distance
        if similarity < min_similarity:
            log.debug(
                "Discarding chunk (similarity=%.4f < min_similarity=%.4f).",
                similarity, min_similarity,
            )
            continue

        source = meta.get("source", "unknown") if meta else "unknown"
        sources.add(source)
        chunks.append({
            "text":       doc,
            "source":     source,
            "topic":      meta.get("topic", "")      if meta else "",
            "difficulty": meta.get("difficulty", "") if meta else "",
            "chunk_id":   meta.get("chunk_id", "")   if meta else "",
            "similarity": similarity,
        })

    summary = _build_summary(query, chunks)
    log.info(
        "rag_search('%s') → %d results from %d sources.",
        query[:60], len(chunks), len(sources),
    )

    return {
        "success": True,
        "query":   query,
        "chunks":  chunks,
        "sources": sorted(sources),
        "summary": summary,
        "error":   "",
    }


# ============================================================
# PRIVATE HELPERS
# ============================================================

def _build_metadata_filter(
    topic:      Optional[str] = None,
    difficulty: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Build a ChromaDB metadata filter dict from optional keyword filters.

    Adding a new filter field in future only requires extending this function.
    The public rag_search() API does not need to change.

    Parameters
    ----------
    topic:      Filter by topic label (e.g. "loops").
    difficulty: Filter by difficulty label (e.g. "beginner").

    Returns
    -------
    dict suitable for ChromaDB where argument, or None if no filters.
    """
    filters: list[dict[str, str]] = []
    if topic:
        filters.append({"topic": topic})
    if difficulty:
        filters.append({"difficulty": difficulty})

    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"": filters}


def _build_summary(query: str, chunks: list[dict[str, Any]]) -> str:
    """Build a concise human-readable summary of retrieved chunks."""
    if not chunks:
        return f"No results found for: {query}"

    lines = [f"Found {len(chunks)} result(s) for: {query}", ""]
    for i, chunk in enumerate(chunks, 1):
        preview = chunk["text"][:120].replace("\n", " ")
        lines.append(
            f"{i}. [{chunk['source']} | {chunk['topic']} | "
            f"similarity={chunk['similarity']:.3f}]"
        )
        lines.append(f"   {preview}...")
        lines.append("")
    return "\n".join(lines).strip()


def _failure_result(query: str, error: str) -> dict[str, Any]:
    """Return a standardised failure result."""
    log.warning("rag_search failed: %s", error)
    return {
        "success": False,
        "query":   query,
        "chunks":  [],
        "sources": [],
        "summary": "",
        "error":   error,
    }