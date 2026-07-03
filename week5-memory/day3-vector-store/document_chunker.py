# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ document_chunker.py
#
# DocumentChunker splits tutorial text into chunks suitable for
# embedding and storage in ChromaDB.
#
# Three chunking strategies:
#   section  (default) - split on ## headings
#   sentence           - split on sentence boundaries
#   fixed              - split on character count
#
# Each chunk carries metadata:
#   source, topic, difficulty, chunk_id, strategy, char_count
# -----------------------------------

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

log = logging.getLogger("week5.document_chunker")

ChunkStrategy = Literal["section", "sentence", "fixed"]

DEFAULT_STRATEGY   : ChunkStrategy = "section"
DEFAULT_CHUNK_SIZE : int           = 512    # chars for fixed strategy
DEFAULT_OVERLAP    : int           = 64     # char overlap for fixed strategy


# ============================================================
# CHUNK DATACLASS
# ============================================================

@dataclass
class Chunk:
    """A single text chunk with its metadata.

    Attributes
    ----------
    text:       The chunk content.
    chunk_id:   Unique identifier (used as ChromaDB document ID).
    source:     Filename the chunk came from (e.g. "loops.txt").
    topic:      Python topic label extracted from the document header.
    difficulty: Difficulty label extracted from the document header.
    strategy:   Chunking strategy used to produce this chunk.
    char_count: Number of characters in ``text``.
    """
    text:       str
    chunk_id:   str
    source:     str                    = ""
    topic:      str                    = ""
    difficulty: str                    = "beginner"
    strategy:   ChunkStrategy         = "section"
    char_count: int                    = field(init=False)

    def __post_init__(self) -> None:
        self.char_count = len(self.text)

    def to_metadata(self) -> dict[str, str]:
        """Return a flat dict suitable for ChromaDB metadata."""
        return {
            "source":     self.source,
            "topic":      self.topic,
            "difficulty": self.difficulty,
            "chunk_id":   self.chunk_id,
            "strategy":   self.strategy,
            "char_count": self.char_count,
        }


# ============================================================
# DOCUMENT CHUNKER
# ============================================================

class DocumentChunker:
    """Splits plain-text tutorial documents into embeddable chunks.

    Parameters
    ----------
    strategy:
        Default chunking strategy.  Can be overridden per call.
    chunk_size:
        Character limit for fixed-size chunking.
    overlap:
        Character overlap between consecutive fixed-size chunks.

    Example
    -------
    >>> chunker = DocumentChunker()
    >>> chunks  = chunker.chunk_file(Path("python_docs/loops.txt"))
    >>> len(chunks)
    8
    """

    def __init__(
        self,
        strategy:   ChunkStrategy = DEFAULT_STRATEGY,
        chunk_size: int            = DEFAULT_CHUNK_SIZE,
        overlap:    int            = DEFAULT_OVERLAP,
    ) -> None:
        self._strategy   = strategy
        self._chunk_size = chunk_size
        self._overlap    = overlap

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk_text(
        self,
        text:     str,
        source:   str           = "",
        strategy: ChunkStrategy = None,  # type: ignore[assignment]
    ) -> list[Chunk]:
        """Chunk a raw text string using the specified strategy.

        Parameters
        ----------
        text:     The full document text.
        source:   Filename label stored in metadata.
        strategy: Override the instance default strategy.

        Returns
        -------
        list[Chunk]  Non-empty chunks with metadata populated.
        """
        if not text or not text.strip():
            log.warning("chunk_text received empty text for source '%s'.", source)
            return []

        strat = strategy or self._strategy
        topic, difficulty, body = _parse_header(text)

        if strat == "section":
            raw_chunks = _split_by_section(body)
        elif strat == "sentence":
            raw_chunks = _split_by_sentence(body)
        elif strat == "fixed":
            raw_chunks = _split_fixed(body, self._chunk_size, self._overlap)
        else:
            log.warning("Unknown strategy '%s' — falling back to section.", strat)
            raw_chunks = _split_by_section(body)

        chunks: list[Chunk] = []
        for i, raw in enumerate(raw_chunks):
            raw = raw.strip()
            if not raw:
                continue
            chunks.append(Chunk(
                text       = raw,
                chunk_id   = _make_id(source, i),
                source     = source,
                topic      = topic,
                difficulty = difficulty,
                strategy   = strat,
            ))

        log.debug(
            "Chunked '%s' → %d chunks using '%s' strategy.",
            source, len(chunks), strat,
        )
        return chunks

    def chunk_file(
        self,
        path:     Path,
        strategy: ChunkStrategy = None,  # type: ignore[assignment]
    ) -> list[Chunk]:
        """Read a .txt file and chunk its contents.

        Parameters
        ----------
        path:     Absolute or relative path to the tutorial file.
        strategy: Override the instance default strategy.

        Returns
        -------
        list[Chunk]  Empty list if the file cannot be read.
        """
        path = Path(path)
        if not path.exists():
            log.error("chunk_file: file not found: %s", path)
            return []

        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            log.error("chunk_file: cannot read '%s': %s", path, exc)
            return []

        return self.chunk_text(text, source=path.name, strategy=strategy)

    def chunk_files(
        self,
        paths:    list[Path],
        strategy: ChunkStrategy = None,  # type: ignore[assignment]
    ) -> list[Chunk]:
        """Chunk multiple files and return all chunks as a flat list."""
        all_chunks: list[Chunk] = []
        for path in paths:
            all_chunks.extend(self.chunk_file(path, strategy=strategy))
        return all_chunks


# ============================================================
# PRIVATE CHUNKING STRATEGIES
# ============================================================

def _parse_header(text: str) -> tuple[str, str, str]:
    """Extract topic, difficulty, and body from a tutorial document.

    Expected header format (first few lines):
        # Title
        topic: loops
        difficulty: beginner

    Returns
    -------
    (topic, difficulty, body_text)
    """
    topic      = "general"
    difficulty = "beginner"
    lines      = text.splitlines()
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped.startswith("topic:"):
            topic = line.split(":", 1)[1].strip()
        elif stripped.startswith("difficulty:"):
            difficulty = line.split(":", 1)[1].strip()
        elif line.startswith("## "):
            body_start = i
            break

    body = "\n".join(lines[body_start:])
    return topic, difficulty, body


def _split_by_section(text: str) -> list[str]:
    """Split on ## headings — each heading starts a new chunk.

    This is the default strategy because tutorial documents are already
    organised into meaningful sections that map well to individual topics.
    """
    # Split on lines starting with ##
    parts = re.split(r"(?m)^(?=## )", text)
    return [p.strip() for p in parts if p.strip()]


def _split_by_sentence(text: str) -> list[str]:
    """Split on sentence boundaries (. ! ?).

    Groups sentences into chunks of at most 5 sentences to keep
    each chunk focused while retaining context.
    """
    # Simple sentence splitter — handles common abbreviations imperfectly
    # but is good enough for clean tutorial text.
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    GROUP_SIZE = 5
    groups: list[str] = []
    for i in range(0, len(sentences), GROUP_SIZE):
        group = " ".join(sentences[i:i + GROUP_SIZE])
        groups.append(group)

    return groups


def _split_fixed(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into fixed-size character chunks with optional overlap.

    Parameters
    ----------
    text:       Input text.
    chunk_size: Maximum characters per chunk.
    overlap:    Characters shared between adjacent chunks.

    Raises
    ------
    ValueError
        If overlap >= chunk_size, which would cause an infinite loop.
    """
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})."
        )

    chunks: list[str] = []
    start  = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if start >= length:
            break

    return chunks


def _make_id(source: str, index: int) -> str:
    """Generate a deterministic chunk ID from source filename and index."""
    stem = Path(source).stem if source else "doc"
    return f"{stem}_chunk_{index:04d}"