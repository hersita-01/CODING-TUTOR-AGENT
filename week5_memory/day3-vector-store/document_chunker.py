# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ document_chunker.py
#
# DocumentChunker splits tutorial text into chunks suitable for
# embedding and storage in ChromaDB.
#
# Four chunking strategies:
#   section  (default) - split on any heading level (#, ##, ###, ####)
#   sentence           - group sentences up to max_chars (default 500)
#   fixed              - character count with word-boundary snapping
#   auto               - automatically selects the best strategy
#
# Each chunk carries metadata:
#   source, topic, difficulty, chunk_id, strategy, char_count,
#   quality_score, contains_heading, sentence_count
# -----------------------------------

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

log = logging.getLogger("week5.document_chunker")

ChunkStrategy = Literal["section", "sentence", "fixed", "auto"]

DEFAULT_STRATEGY         : ChunkStrategy = "section"
DEFAULT_CHUNK_SIZE       : int           = 512    # chars for fixed strategy
DEFAULT_OVERLAP          : int           = 64     # char overlap for fixed strategy
DEFAULT_SENTENCE_MAX_CHARS: int          = 500    # max chars per sentence group


# ============================================================
# CHUNK DATACLASS
# ============================================================

@dataclass
class Chunk:
    """A single text chunk with its metadata.

    Attributes
    ----------
    text:             The chunk content.
    chunk_id:         Unique identifier (used as ChromaDB document ID).
    source:           Filename the chunk came from (e.g. "loops.txt").
    topic:            Python topic label extracted from the document header.
    difficulty:       Difficulty label extracted from the document header.
    strategy:         Chunking strategy used to produce this chunk.
    char_count:       Number of characters in ``text``.
    quality_score:    Float 0–1 rating based on length, headings, sentences.
    contains_heading: True if the chunk starts with a Markdown heading.
    sentence_count:   Approximate number of sentences in the chunk.
    """
    text:             str
    chunk_id:         str
    source:           str           = ""
    topic:            str           = ""
    difficulty:       str           = "beginner"
    strategy:         ChunkStrategy = "section"
    char_count:       int           = field(init=False)
    quality_score:    float         = field(init=False)
    contains_heading: bool          = field(init=False)
    sentence_count:   int           = field(init=False)

    def __post_init__(self) -> None:
        self.char_count       = len(self.text)
        self.contains_heading = bool(re.match(r"^#{1,6}\s", self.text))
        self.sentence_count   = len(re.findall(r"[.!?][\s\n]", self.text)) + 1
        self.quality_score    = _score_chunk(self.text)

    def to_metadata(self) -> dict:
        """Return a flat dict suitable for ChromaDB metadata."""
        return {
            "source":           self.source,
            "topic":            self.topic,
            "difficulty":       self.difficulty,
            "chunk_id":         self.chunk_id,
            "strategy":         self.strategy,
            "char_count":       self.char_count,
            "quality_score":    round(self.quality_score, 4),
            "contains_heading": self.contains_heading,
            "sentence_count":   self.sentence_count,
        }


# ============================================================
# DOCUMENT CHUNKER
# ============================================================

class DocumentChunker:
    """Splits plain-text tutorial documents into embeddable chunks.

    Parameters
    ----------
    strategy:
        Default chunking strategy. ``"auto"`` selects the best strategy
        per document. Can be overridden per call.
    chunk_size:
        Character limit for fixed-size chunking.
    overlap:
        Character overlap between consecutive fixed-size chunks.
    sentence_max_chars:
        Maximum characters per sentence group (sentence strategy).

    Example
    -------
    >>> chunker = DocumentChunker()
    >>> chunks  = chunker.chunk_file(Path("python_docs/loops.txt"))
    >>> len(chunks)
    8
    """

    def __init__(
        self,
        strategy:           ChunkStrategy = DEFAULT_STRATEGY,
        chunk_size:         int            = DEFAULT_CHUNK_SIZE,
        overlap:            int            = DEFAULT_OVERLAP,
        sentence_max_chars: int            = DEFAULT_SENTENCE_MAX_CHARS,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")
        if overlap < 0:
            raise ValueError("overlap cannot be negative.")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size.")
        if sentence_max_chars <= 0:
            raise ValueError("sentence_max_chars must be greater than 0.")

        self._strategy            = strategy
        self._chunk_size          = chunk_size
        self._overlap             = overlap
        self._sentence_max_chars  = sentence_max_chars

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
                  Pass ``"auto"`` to let the chunker decide.

        Returns
        -------
        list[Chunk]  Non-empty chunks with metadata populated.
        """
        if not text or not text.strip():
            log.warning("chunk_text received empty text for source '%s'.", source)
            return []

        strat = strategy or self._strategy
        topic, difficulty, body = _parse_header(text)

        # Auto-select best strategy based on document structure.
        if strat == "auto":
            strat = self._choose_best_strategy(body)
            log.debug("Auto strategy selected '%s' for source '%s'.", strat, source)

        if strat == "section":
            raw_chunks = _split_by_section(body)
        elif strat == "sentence":
            raw_chunks = _split_by_sentence(body, self._sentence_max_chars)
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

    # ------------------------------------------------------------------
    # Analysis helpers
    # ------------------------------------------------------------------

    def chunk_statistics(self, chunks: list[Chunk]) -> dict:
        """Return summary statistics for a list of chunks.

        Parameters
        ----------
        chunks:
            List of Chunk objects to analyse.

        Returns
        -------
        dict with keys:
            chunks, average_size, largest, smallest, strategy
        """
        if not chunks:
            return {
                "chunks":       0,
                "average_size": 0,
                "largest":      0,
                "smallest":     0,
                "strategy":     "n/a",
            }

        sizes    = [c.char_count for c in chunks]
        strategy = chunks[0].strategy if chunks else "n/a"

        return {
            "chunks":       len(chunks),
            "average_size": round(sum(sizes) / len(sizes)),
            "largest":      max(sizes),
            "smallest":     min(sizes),
            "strategy":     strategy,
        }

    def preview_chunks(
        self,
        chunks:    list[Chunk],
        max_chars: int = 80,
    ) -> str:
        """Return a human-readable preview of all chunks.

        Useful for CLI inspection and debugging.

        Parameters
        ----------
        chunks:    List of Chunk objects to preview.
        max_chars: Maximum characters of chunk text to show per chunk.

        Returns
        -------
        str  Multi-line preview string, ready to print.
        """
        if not chunks:
            return "(no chunks)"

        lines: list[str] = []
        sep = "-" * (min(max_chars, 60))

        for i, chunk in enumerate(chunks):
            preview = chunk.text[:max_chars].replace("\n", " ")
            if len(chunk.text) > max_chars:
                preview += "…"
            lines.append(f"Chunk {i}  [{chunk.strategy} | {chunk.char_count} chars | "
                          f"score={chunk.quality_score:.2f}]")
            lines.append(preview)
            lines.append(sep)

        return "\n".join(lines)

    def compare_strategies(self, text: str) -> dict[str, int]:
        """Chunk the same text with all three concrete strategies and compare.

        Useful for choosing the best strategy for a document type and
        for project reports comparing retrieval accuracy per strategy.

        Parameters
        ----------
        text:  The document text to analyse.

        Returns
        -------
        dict mapping strategy name → number of chunks produced.

        Example
        -------
        >>> chunker.compare_strategies(text)
        {"section": 8, "sentence": 23, "fixed": 14}
        """
        results: dict[str, int] = {}
        for strat in ("section", "sentence", "fixed"):
            chunks = self.chunk_text(text, source="_compare", strategy=strat)  # type: ignore
            results[strat] = len(chunks)
            log.debug("compare_strategies: '%s' → %d chunks.", strat, len(chunks))
        return results

    def validate_chunks(
        self,
        chunks:   list[Chunk],
        max_size: int = DEFAULT_CHUNK_SIZE * 2,
    ) -> dict:
        """Validate a list of chunks and report quality issues.

        Parameters
        ----------
        chunks:   List of Chunk objects to inspect.
        max_size: Character count above which a chunk is flagged as oversized.

        Returns
        -------
        dict with keys:
            empty_chunks, duplicate_chunks, oversized_chunks
        """
        empty_count     = sum(1 for c in chunks if not c.text.strip())
        oversized_count = sum(1 for c in chunks if c.char_count > max_size)

        texts = [c.text for c in chunks if c.text.strip()]
        duplicate_count = len(texts) - len(set(texts))

        return {
            "empty_chunks":     empty_count,
            "duplicate_chunks": duplicate_count,
            "oversized_chunks": oversized_count,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _choose_best_strategy(self, body: str) -> ChunkStrategy:
        """Select the most appropriate chunking strategy for a document body.

        Decision rules (in priority order):
          1. Two or more headings (# / ## / ###) → section
          2. Ten or more sentence-ending punctuation marks → sentence
          3. Everything else → fixed

        Parameters
        ----------
        body:  The document body text (after header extraction).

        Returns
        -------
        ChunkStrategy  One of "section", "sentence", or "fixed".
        """
        heading_count  = len(re.findall(r"(?m)^#{1,6}\s", body))
        sentence_count = len(re.findall(r"[.!?]", body))

        if heading_count >= 2:
            return "section"
        if sentence_count >= 10:
            return "sentence"
        return "fixed"


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
        elif re.match(r"^#{2,6}\s", line):
            # ## or deeper heading starts the body — skip the h1 title line.
            body_start = i
            break

    body = "\n".join(lines[body_start:])
    return topic, difficulty, body


def _split_by_section(text: str) -> list[str]:
    """Split on any Markdown heading level (#, ##, ###, ####, #####).

    Supports all heading levels so tutorials using mixed heading depths
    are chunked correctly, not just those using exactly ##.
    """
    parts = re.split(r"(?m)^(?=#{1,6}\s)", text)
    return [p.strip() for p in parts if p.strip()]


def _split_by_sentence(text: str, max_chars: int = DEFAULT_SENTENCE_MAX_CHARS) -> list[str]:
    """Group sentences into chunks up to max_chars characters.

    Instead of a fixed group size (e.g. always 5 sentences), sentences
    are accumulated until adding the next would exceed max_chars.
    This produces naturally-sized chunks regardless of sentence length.

    Parameters
    ----------
    text:      Input text.
    max_chars: Maximum characters per chunk group.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    groups : list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        # If adding this sentence would exceed max_chars, flush current group.
        if current and current_len + sentence_len + 1 > max_chars:
            groups.append(" ".join(current))
            current     = []
            current_len = 0
        current.append(sentence)
        current_len += sentence_len + 1

    if current:
        groups.append(" ".join(current))

    return groups


def _split_fixed(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into fixed-size character chunks, snapping to word boundaries.

    Instead of cutting exactly at chunk_size characters (which can split
    words mid-way), the split point is moved back to the nearest space or
    newline so chunks always end on a complete word.

    Parameters
    ----------
    text:       Input text.
    chunk_size: Target maximum characters per chunk.
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

        # Snap end backwards to nearest whitespace to avoid splitting words.
        if end < length:
            snap = text.rfind(" ", start, end)
            if snap == -1:
                snap = text.rfind("\n", start, end)
            if snap > start:          # only snap if we found a boundary
                end = snap

        chunks.append(text[start:end].strip())
        start += (end - start) - overlap
        # Guard: always advance by at least 1 to prevent infinite loops.
        if start <= 0 or (end - start) - overlap <= 0:
            start = end

    return [c for c in chunks if c]


def _score_chunk(text: str) -> float:
    """Score a chunk's embedding quality on a 0.0–1.0 scale.

    Scoring factors:
      - Length:         optimal around 200–400 chars
      - Has heading:    +0.2 bonus (headings anchor semantic meaning)
      - Has sentences:  +0.2 bonus (complete thoughts embed better)
      - Has code block: +0.1 bonus (technical content is meaningful)

    Parameters
    ----------
    text:  The raw chunk text.

    Returns
    -------
    float  Quality score in [0.0, 1.0].
    """
    if not text.strip():
        return 0.0

    score = 0.0

    # Length score: 0–0.5 based on character count
    length = len(text)
    if 100 <= length <= 600:
        score += 0.5
    elif length < 100:
        score += length / 200.0          # short chunks score proportionally
    else:
        score += max(0.0, 0.5 - (length - 600) / 2000.0)   # penalise very long

    # Heading bonus
    if re.match(r"^#{1,6}\s", text):
        score += 0.2

    # Sentence bonus (at least two complete sentences)
    if len(re.findall(r"[.!?][\s\n]", text)) >= 2:
        score += 0.2

    # Code block bonus
    if "```" in text or re.search(r"(?m)^    \S", text):
        score += 0.1

    return round(min(score, 1.0), 4)


def _make_id(source: str, index: int) -> str:
    """Generate a deterministic chunk ID from source filename and index."""
    stem = Path(source).stem if source else "doc"
    return f"{stem}_chunk_{index:04d}"