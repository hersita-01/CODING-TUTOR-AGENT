# -----------------------------------
# WEEK 5 – DAY 4: CHUNKING EVALUATION
# week5-memory/day4-chunking-eval/ chunking_evaluator.py
#
# Evaluates DocumentChunker's three concrete strategies
# (section, sentence, fixed) on a set of tutorial documents
# and produces a ranked comparison with RAG-suitability scores.
#
# What this module does NOT do:
#   ✗ Implement new chunking algorithms  → uses document_chunker.py
#   ✗ Embed chunks                       → delegates to embedding_manager.py
#   ✗ Store in ChromaDB                  → that is Day 3 / Day 5
#   ✗ Perform retrieval                  → that is Day 5
#
# Architecture position:
#
#   DocumentChunker (Day 3)
#       ↓
#   ChunkingEvaluator         ← this file
#       ↓
#   EvaluationReport
#       ↓
#   evaluate_chunking.py      ← CLI runner
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import logging
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
import dataclasses
from typing import Any, Optional

log = logging.getLogger("week5.chunking_evaluator")

# ── Path setup ────────────────────────────────────────────────────────
# Mirrors the path setup used throughout the project so sibling
# modules resolve correctly regardless of launch directory.
_here  = Path(__file__).resolve().parent          # day4-chunking-eval/
_day3  = _here.parent / "day3-vector-store"
_day2  = _here.parent / "day2-embeddings"
_week5 = _here.parent

for _p in [str(_day3), str(_day2), str(_week5), str(_here)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from document_chunker  import ChunkStrategy, DocumentChunker, Chunk

# EmbeddingManager is optional — used only for embedding-time measurement.
# If Day 2 is not importable the evaluator still runs without timing.
try:
    from embedding_manager import EmbeddingManager
    _EMBEDDER_AVAILABLE = True
except ImportError:
    _EMBEDDER_AVAILABLE = False
    log.warning("EmbeddingManager not found — embedding timing will be skipped.")


# ============================================================
# CONSTANTS
# ============================================================

# Strategies compared in every evaluation run.
# "auto" is excluded deliberately — it selects one of the three
# concrete strategies, so including it would double-count results.
STRATEGIES: tuple[ChunkStrategy, ...] = ("section", "sentence", "fixed")

# RAG scoring weights — tune these to reflect retrieval priorities.
# All weights must sum to 1.0.
_W_CHUNK_COUNT    = 0.15   # more chunks → more granular retrieval (up to a point)
_W_AVG_SIZE       = 0.25   # chunks close to the ideal size embed better
_W_SIZE_VARIANCE  = 0.20   # low variance → predictable retrieval quality
_W_COMPLETENESS   = 0.20   # chunks with full sentences embed more semantically
_W_HEADING_RATE   = 0.10   # chunks that start with headings anchor meaning well
_W_DUPLICATE_RATE = 0.10   # duplicates waste vector space

# Ideal chunk size in characters for RAG — researched optimum for
# all-MiniLM-L6-v2 (384-d model, trained on sentences up to ~256 tokens).
IDEAL_CHUNK_SIZE   = 350    # chars ≈ ~70 tokens
MAX_CHUNK_SIZE     = 600    # above this embeddings start to lose precision
MIN_CHUNK_SIZE     = 80     # below this chunks lack semantic context


# ============================================================
# RESULT DATACLASSES
# ============================================================

@dataclass
class StrategyMetrics:
    """All measurable properties of one strategy's chunk output.

    Produced by ``ChunkingEvaluator._measure()`` for a single
    (strategy, document) combination.

    Attributes
    ----------
    strategy:         Name of the chunking strategy.
    source:           Document filename the chunks came from.
    chunk_count:      Total number of chunks produced.
    avg_size:         Mean character count per chunk.
    min_size:         Smallest chunk in characters.
    max_size:         Largest chunk in characters.
    size_variance:    Standard deviation of chunk sizes.
    empty_count:      Chunks with no text content.
    duplicate_count:  Chunks with identical text to another chunk.
    oversized_count:  Chunks exceeding MAX_CHUNK_SIZE characters.
    undersized_count: Chunks below MIN_CHUNK_SIZE characters.
    heading_rate:     Fraction of chunks that start with a heading.
    sentence_rate:    Fraction of chunks containing ≥2 full sentences.
    code_block_rate:  Fraction of chunks containing code.
    rag_score:        Composite RAG-suitability score in [0, 1].
    embed_time_s:     Seconds to embed all chunks (None if skipped).
    time_taken_s:     Total seconds for chunking + analysis.
    """

    strategy:         str
    source:           str
    chunk_count:      int
    avg_size:         float
    min_size:         int
    max_size:         int
    size_variance:    float
    empty_count:      int
    duplicate_count:  int
    oversized_count:  int
    undersized_count: int
    heading_rate:     float
    sentence_rate:    float
    code_block_rate:  float
    rag_score:        float
    embed_time_s:     Optional[float]
    time_taken_s:     float

    def as_dict(self) -> dict[str, Any]:
        """Return a flat dict for tabular display."""
        return {
            "strategy":         self.strategy,
            "source":           self.source,
            "chunks":           self.chunk_count,
            "avg_size":         round(self.avg_size),
            "min_size":         self.min_size,
            "max_size":         self.max_size,
            "size_variance":    round(self.size_variance, 1),
            "empty":            self.empty_count,
            "duplicates":       self.duplicate_count,
            "oversized":        self.oversized_count,
            "undersized":       self.undersized_count,
            "heading_rate":     f"{self.heading_rate:.0%}",
            "sentence_rate":    f"{self.sentence_rate:.0%}",
            "code_rate":        f"{self.code_block_rate:.0%}",
            "rag_score":        f"{self.rag_score:.3f}",
            "embed_time_s":     f"{self.embed_time_s:.2f}" if self.embed_time_s is not None else "n/a",
            "time_taken_s":     f"{self.time_taken_s:.3f}",
        }


@dataclass
class EvaluationReport:
    """Complete evaluation results for one or more documents.

    Attributes
    ----------
    sources:    Document filenames that were evaluated.
    metrics:    All StrategyMetrics objects, one per (strategy, source).
    winner:     Strategy name with the highest mean RAG score.
    ranked:     Strategy names ordered by mean RAG score (best first).
    summary:    Human-readable multi-line report string.
    generated_at: ISO timestamp of report generation.
    """

    sources:      list[str]
    metrics:      list[StrategyMetrics]
    winner:       str
    ranked:       list[str]
    summary:      str
    generated_at: str = field(default_factory=lambda: _iso_now())

    def mean_score(self, strategy: str) -> float:
        """Return the mean RAG score for a strategy across all sources."""
        scores = [m.rag_score for m in self.metrics if m.strategy == strategy]
        return sum(scores) / len(scores) if scores else 0.0


# ============================================================
# CHUNKING EVALUATOR
# ============================================================

class ChunkingEvaluator:
    """Evaluates DocumentChunker strategies for RAG suitability.

    Runs section, sentence, and fixed chunking on each document,
    computes per-strategy metrics, scores them for RAG fitness,
    and returns a ranked EvaluationReport.

    Parameters
    ----------
    chunker:
        DocumentChunker instance to use.  A default instance is
        created if not supplied.
    measure_embed_time:
        If True and EmbeddingManager is available, time how long
        it takes to embed all chunks per strategy.  Adds real model
        inference time to the report.

    Example
    -------
    >>> evaluator = ChunkingEvaluator()
    >>> report = evaluator.evaluate_file(Path("python_docs/loops.txt"))
    >>> print(report.summary)

    >>> report = evaluator.evaluate_folder(Path("python_docs/"))
    >>> print(report.winner)
    """

    def __init__(
        self,
        chunker:             Optional[DocumentChunker] = None,
        measure_embed_time:  bool                      = False,
    ) -> None:
        self._chunker            = chunker if chunker is not None else DocumentChunker()
        self._measure_embed_time = measure_embed_time and _EMBEDDER_AVAILABLE
        self._embedder           = EmbeddingManager() if self._measure_embed_time else None

        log.debug(
            "ChunkingEvaluator ready. embed_timing=%s",
            self._measure_embed_time,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def chunker(self) -> DocumentChunker:
        """Return the DocumentChunker instance used by this evaluator.

        Provides public access without exposing the private attribute
        directly, keeping the internal implementation replaceable.
        """
        return self._chunker

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_file(self, path: Path) -> EvaluationReport:
        """Evaluate all strategies on a single document file.

        Parameters
        ----------
        path:
            Path to a ``.txt`` tutorial document.

        Returns
        -------
        EvaluationReport  with metrics for all strategies on this file.
        """
        path = Path(path)
        if not path.exists() or not path.is_file():
            log.error("evaluate_file: '%s' not found or not a file.", path)
            return self._empty_report([str(path)], f"File not found: {path}")

        log.info("Evaluating '%s' …", path.name)

        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            log.error("Cannot read '%s': %s", path.name, exc)
            return self._empty_report([path.name], f"Cannot read file: {exc}")

        if not text.strip():
            log.warning("'%s' is empty — skipping.", path.name)
            return self._empty_report([path.name], "File is empty.")

        all_metrics = self._evaluate_text(text, source=path.name)
        return self._build_report([path.name], all_metrics)

    def evaluate_folder(self, folder: Path) -> EvaluationReport:
        """Evaluate all strategies on every ``.txt`` file in a folder.

        Hidden files (names starting with ``.``) are excluded.

        Parameters
        ----------
        folder:
            Directory containing ``.txt`` tutorial documents.

        Returns
        -------
        EvaluationReport  with aggregated metrics across all files.
        """
        folder = Path(folder)
        if not folder.is_dir():
            log.error("evaluate_folder: '%s' is not a directory.", folder)
            return self._empty_report([str(folder)], f"Not a directory: {folder}")

        txt_files = sorted(
            p for p in folder.glob("*.txt") if not p.name.startswith(".")
        )
        if not txt_files:
            log.warning("No .txt files found in '%s'.", folder)
            return self._empty_report([str(folder)], "No .txt files found.")

        log.info("Evaluating %d file(s) in '%s' …", len(txt_files), folder)

        all_metrics:  list[StrategyMetrics] = []
        sources:      list[str]             = []

        for path in txt_files:
            try:
                text = path.read_text(encoding="utf-8")
                if not text.strip():
                    log.warning("'%s' is empty — skipping.", path.name)
                    continue
                metrics = self._evaluate_text(text, source=path.name)
                all_metrics.extend(metrics)
                sources.append(path.name)
                log.info("'%s' evaluated.", path.name)
            except Exception as exc:
                log.error("Failed to evaluate '%s': %s", path.name, exc)

        if not all_metrics:
            return self._empty_report(sources, "No metrics could be computed.")

        return self._build_report(sources, all_metrics)

    def evaluate_text(self, text: str, source: str = "inline") -> EvaluationReport:
        """Evaluate all strategies on a raw text string.

        Useful for testing without writing files to disk.

        Parameters
        ----------
        text:   The document text to evaluate.
        source: Label used in the report.
        """
        if not text.strip():
            return self._empty_report([source], "Text is empty.")

        metrics = self._evaluate_text(text, source=source)
        return self._build_report([source], metrics)

    # ------------------------------------------------------------------
    # Core evaluation logic
    # ------------------------------------------------------------------

    def _evaluate_text(
        self,
        text:   str,
        source: str,
    ) -> list[StrategyMetrics]:
        """Run all strategies on one document and return their metrics.

        Evaluation flow for each strategy:
          1. chunk_text()        — split document using the strategy
          2. _time_embedding()   — optionally measure embed time (Day 2)
          3. _measure()          — compute size stats, quality counts,
                                   content rates, and RAG score

        Parameters
        ----------
        text:   Raw document text.
        source: Source label (filename) for the metrics.

        Returns
        -------
        list[StrategyMetrics]  One entry per strategy (skips failed ones).
        """
        results: list[StrategyMetrics] = []

        for strategy in STRATEGIES:
            t0 = time.perf_counter()

            # ── Chunk ─────────────────────────────────────────────────
            try:
                chunks = self._chunker.chunk_text(
                    text,
                    source   = source,
                    strategy = strategy,
                )
            except Exception as exc:
                log.error("Chunking failed for strategy '%s': %s", strategy, exc)
                continue

            if not chunks:
                log.warning("Strategy '%s' produced no chunks for '%s'.", strategy, source)
                continue

            # ── Measure embedding time (optional) ─────────────────────
            embed_time: Optional[float] = None
            if self._measure_embed_time and self._embedder is not None:
                embed_time = self._time_embedding(chunks)

            # ── Compute metrics ────────────────────────────────────────
            metrics = self._measure(chunks, strategy, source, embed_time)
            metrics = _replace(metrics, time_taken_s=round(time.perf_counter() - t0, 3))
            results.append(metrics)

            log.debug(
                "Strategy '%s' on '%s': %d chunks  rag_score=%.3f",
                strategy, source, metrics.chunk_count, metrics.rag_score,
            )

        return results

    def _measure(
        self,
        chunks:     list[Chunk],
        strategy:   str,
        source:     str,
        embed_time: Optional[float],
    ) -> StrategyMetrics:
        """Compute all metrics for a list of chunks.

        Delegates to DocumentChunker helper methods where they exist
        (chunk_statistics, validate_chunks), and falls back to inline
        computation for older chunker versions that pre-date those methods.
        This keeps the evaluator compatible with both Day 3 versions.

        Content rates (heading_rate, sentence_rate, code_block_rate) are
        always computed here because no chunker method exposes them directly.
        When the newer Chunk dataclass exposes contains_heading and
        sentence_count, those fields are read directly to stay DRY.

        Parameters
        ----------
        chunks:     Non-empty list of Chunk objects.
        strategy:   Strategy name label.
        source:     Document source label.
        embed_time: Seconds to embed all chunks, or None if not measured.

        Returns
        -------
        StrategyMetrics  with all fields populated.
        """
        sizes    = [c.char_count for c in chunks]
        texts    = [c.text       for c in chunks]
        n        = len(chunks)
        variance = _std_dev(sizes)   # computed once; used regardless of chunker version

        # ── Size statistics ───────────────────────────────────────────
        # Delegate to chunker.chunk_statistics() when available (added in
        # the Day 3 revision that introduced analysis helpers).  Falls back
        # to inline computation for older chunker versions.
        if callable(getattr(self._chunker, "chunk_statistics", None)):
            stats    = self._chunker.chunk_statistics(chunks)
            avg_size = float(stats.get("average_size", sum(sizes) / n))
        else:
            avg_size = sum(sizes) / n

        # ── Quality counts ────────────────────────────────────────────
        # Delegate to chunker.validate_chunks() when available.
        if callable(getattr(self._chunker, "validate_chunks", None)):
            validation       = self._chunker.validate_chunks(chunks, max_size=MAX_CHUNK_SIZE)
            empty_count      = validation.get("empty_chunks",     0)
            duplicate_count  = validation.get("duplicate_chunks", 0)
            oversized_count  = validation.get("oversized_chunks", 0)
            undersized_count = sum(1 for s in sizes if s < MIN_CHUNK_SIZE)
        else:
            empty_count      = sum(1 for t in texts if not t.strip())
            duplicate_count  = n - len(set(texts))
            oversized_count  = sum(1 for s in sizes if s > MAX_CHUNK_SIZE)
            undersized_count = sum(1 for s in sizes if s < MIN_CHUNK_SIZE)

        # ── Content rates ─────────────────────────────────────────────
        # These are computed inline — no existing chunker method exposes
        # per-strategy content rates directly.  The Chunk dataclass does
        # expose contains_heading and sentence_count in newer versions,
        # so use those fields when present to stay DRY.
        if hasattr(chunks[0], "contains_heading"):
            heading_count  = sum(1 for c in chunks if c.contains_heading)
            sentence_count = sum(1 for c in chunks if getattr(c, "sentence_count", 0) >= 2)
        else:
            heading_count  = sum(1 for t in texts if re.match(r"^#{1,6}\s", t))
            sentence_count = sum(1 for t in texts if len(re.findall(r"[.!?][\s\n]", t)) >= 2)
        code_count     = sum(1 for t in texts if "```" in t or re.search(r"(?m)^    \S", t))

        heading_rate  = heading_count  / n
        sentence_rate = sentence_count / n
        code_rate     = code_count     / n

        # ── RAG suitability score ─────────────────────────────────────
        # Composite score in [0, 1].  See _rag_score() for full rationale
        # and weight definitions.
        rag = _rag_score(
            chunk_count    = n,
            avg_size       = avg_size,
            size_variance  = variance,
            sentence_rate  = sentence_rate,
            heading_rate   = heading_rate,
            duplicate_count= duplicate_count,
        )

        return StrategyMetrics(
            strategy         = strategy,
            source           = source,
            chunk_count      = n,
            avg_size         = round(avg_size, 1),
            min_size         = min(sizes),
            max_size         = max(sizes),
            size_variance    = round(variance, 1),
            empty_count      = empty_count,
            duplicate_count  = duplicate_count,
            oversized_count  = oversized_count,
            undersized_count = undersized_count,
            heading_rate     = round(heading_rate, 3),
            sentence_rate    = round(sentence_rate, 3),
            code_block_rate  = round(code_rate, 3),
            rag_score        = round(rag, 4),
            embed_time_s     = embed_time,
            time_taken_s     = 0.0,   # set by caller after perf_counter
        )

    def _time_embedding(self, chunks: list[Chunk]) -> Optional[float]:
        """Time how long it takes to embed all chunks in this batch.

        Parameters
        ----------
        chunks:  Chunks to embed.

        Returns
        -------
        Seconds taken, or None on failure.
        """
        if self._embedder is None:
            return None
        try:
            texts = [c.text for c in chunks]
            t0    = time.perf_counter()
            self._embedder.embed_batch(texts)
            return round(time.perf_counter() - t0, 3)
        except Exception as exc:
            log.warning("Embedding timing failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Report builder
    # ------------------------------------------------------------------

    def _build_report(
        self,
        sources:     list[str],
        all_metrics: list[StrategyMetrics],
    ) -> EvaluationReport:
        """Aggregate metrics into a ranked EvaluationReport.

        Parameters
        ----------
        sources:     Document filenames that were evaluated.
        all_metrics: All StrategyMetrics across all (strategy, source) pairs.

        Returns
        -------
        EvaluationReport  with ranked strategies and a formatted summary.
        """
        # Compute mean RAG score per strategy across all sources.
        mean_scores: dict[str, float] = {}
        for strat in STRATEGIES:
            scores = [m.rag_score for m in all_metrics if m.strategy == strat]
            if scores:
                mean_scores[strat] = round(sum(scores) / len(scores), 4)

        if not mean_scores:
            return self._empty_report(sources, "No scores could be computed.")

        ranked = sorted(mean_scores, key=lambda s: mean_scores[s], reverse=True)
        winner = ranked[0]

        summary = _format_report(sources, all_metrics, mean_scores, ranked)

        log.info("Evaluation complete. Winner: '%s' (score=%.4f).", winner, mean_scores[winner])

        return EvaluationReport(
            sources  = sources,
            metrics  = all_metrics,
            winner   = winner,
            ranked   = ranked,
            summary  = summary,
        )

    def _empty_report(self, sources: list[str], message: str) -> EvaluationReport:
        """Return an empty report when evaluation cannot proceed."""
        return EvaluationReport(
            sources  = sources,
            metrics  = [],
            winner   = "n/a",
            ranked   = [],
            summary  = f"Evaluation could not complete: {message}",
        )


# ============================================================
# PRIVATE SCORING HELPERS
# ============================================================

def _rag_score(
    chunk_count:     int,
    avg_size:        float,
    size_variance:   float,
    sentence_rate:   float,
    heading_rate:    float,
    duplicate_count: int,
) -> float:
    """Compute a composite RAG-suitability score in [0, 1].

    Each factor is normalised to [0, 1] and weighted.  The weights
    are defined as module-level constants and can be tuned.

    Scoring rationale
    -----------------
    The score is a weighted sum of six normalised sub-scores, all in [0, 1].
    Weights are defined as module-level constants (_W_*) so they can be
    tuned without changing this function.

    chunk_count  (weight _W_CHUNK_COUNT = 0.15):
        5–30 chunks is a healthy range for a single tutorial document.
        Too few → retriever has no granularity; too many → context windows
        fill up with noise.  Sub-score = 1.0 in [5, 30], linear outside.

    avg_size  (weight _W_AVG_SIZE = 0.25):
        Chunks near IDEAL_CHUNK_SIZE (350 chars ≈ 70 tokens) embed best
        with all-MiniLM-L6-v2.  Very short chunks lack semantic context;
        very long chunks push past the model's effective token window.
        Sub-score = 1 − |avg_size − ideal| / ideal.

    size_variance  (weight _W_SIZE_VARIANCE = 0.20):
        Low variance → predictable retrieval quality.  High variance means
        some chunks dominate similarity rankings simply because they are
        long.  Sub-score = 1 − std_dev / (2 × ideal).

    sentence_rate  (weight _W_COMPLETENESS = 0.20):
        Fraction of chunks containing ≥2 full sentences.  Complete
        sentences embed with stronger and more consistent semantic signal
        than sentence fragments.  Sub-score = sentence_rate directly.

    heading_rate  (weight _W_HEADING_RATE = 0.10):
        Fraction of chunks that begin with a Markdown heading.  Headings
        anchor the semantic meaning of the chunk and make retrieval results
        easier to cite.  Sub-score = heading_rate directly.

    duplicate_count  (weight _W_DUPLICATE_RATE = 0.10):
        Duplicate chunks waste vector-store space and inflate match scores
        for repeated passages.  Sub-score = max(0, 1 − dups / 5).
    """
    # ── Chunk count score (optimal 5–30) ──────────────────────────────
    if 5 <= chunk_count <= 30:
        count_score = 1.0
    elif chunk_count < 5:
        count_score = chunk_count / 5.0
    else:
        count_score = max(0.0, 1.0 - (chunk_count - 30) / 50.0)

    # ── Average size score (optimal near IDEAL_CHUNK_SIZE) ────────────
    deviation   = abs(avg_size - IDEAL_CHUNK_SIZE)
    size_score  = max(0.0, 1.0 - deviation / IDEAL_CHUNK_SIZE)

    # ── Variance score (lower is better; normalise by IDEAL) ──────────
    variance_score = max(0.0, 1.0 - size_variance / (IDEAL_CHUNK_SIZE * 2))

    # ── Completeness score (fraction of sentence-complete chunks) ─────
    completeness_score = sentence_rate

    # ── Heading score ─────────────────────────────────────────────────
    heading_score = heading_rate

    # ── Duplicate penalty ─────────────────────────────────────────────
    # Normalise: 0 duplicates → 1.0;  5+ duplicates → 0.0
    dup_score = max(0.0, 1.0 - duplicate_count / 5.0)

    score = (
        _W_CHUNK_COUNT    * count_score
        + _W_AVG_SIZE     * size_score
        + _W_SIZE_VARIANCE* variance_score
        + _W_COMPLETENESS * completeness_score
        + _W_HEADING_RATE * heading_score
        + _W_DUPLICATE_RATE * dup_score
    )
    return max(0.0, min(1.0, score))


def _std_dev(values: list[int]) -> float:
    """Compute population standard deviation for a list of integers."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance ** 0.5


# ============================================================
# REPORT FORMATTER
# ============================================================

def _format_report(
    sources:     list[str],
    metrics:     list[StrategyMetrics],
    mean_scores: dict[str, float],
    ranked:      list[str],
) -> str:
    """Build a human-readable evaluation report string.

    Parameters
    ----------
    sources:     Evaluated document filenames.
    metrics:     All StrategyMetrics objects.
    mean_scores: Mean RAG score per strategy.
    ranked:      Strategy names in rank order (best first).

    Returns
    -------
    Multi-line string ready to print to stdout.
    """
    sep  = "=" * 60
    thin = "-" * 60
    lines: list[str] = []

    lines.append(sep)
    lines.append("  WEEK 5 DAY 4 — CHUNKING STRATEGY EVALUATION")
    lines.append(sep)
    lines.append(f"  Documents evaluated : {len(sources)}")
    lines.append(f"  Sources             : {', '.join(sources)}")
    lines.append("")

    # ── Per-strategy summary ─────────────────────────────────────────
    lines.append("  STRATEGY COMPARISON")
    lines.append(thin)

    # Determine whether any metric has embed timing so we show that column
    # only when --embed-timing was used.
    has_embed = any(m.embed_time_s is not None for m in metrics)

    header = (
        f"  {'Strategy':<12} {'Chunks':>6} {'AvgSize':>8} "
        f"{'Min':>6} {'Max':>6} {'Variance':>10} "
        f"{'Sent%':>7} {'Hdg%':>6} {'Dups':>5} {'RAG Score':>10}"
    )
    if has_embed:
        header += f" {'EmbedTime':>11}"
    lines.append(header)
    lines.append(thin)

    for strat in ranked:
        strat_metrics = [m for m in metrics if m.strategy == strat]
        if not strat_metrics:
            continue

        # Aggregate across all sources for this strategy.
        avg_chunks   = sum(m.chunk_count    for m in strat_metrics) / len(strat_metrics)
        avg_size     = sum(m.avg_size       for m in strat_metrics) / len(strat_metrics)
        avg_min      = sum(m.min_size       for m in strat_metrics) / len(strat_metrics)
        avg_max      = sum(m.max_size       for m in strat_metrics) / len(strat_metrics)
        avg_var      = sum(m.size_variance  for m in strat_metrics) / len(strat_metrics)
        avg_sent     = sum(m.sentence_rate  for m in strat_metrics) / len(strat_metrics)
        avg_hdg      = sum(m.heading_rate   for m in strat_metrics) / len(strat_metrics)
        total_dups   = sum(m.duplicate_count for m in strat_metrics)
        score        = mean_scores.get(strat, 0.0)
        embed_times  = [m.embed_time_s for m in strat_metrics if m.embed_time_s is not None]
        avg_embed    = sum(embed_times) / len(embed_times) if embed_times else None

        medal = "🥇" if strat == ranked[0] else ("🥈" if strat == ranked[1] else "🥉")

        row = (
            f"  {medal} {strat:<10} {avg_chunks:>6.1f} {avg_size:>8.0f} "
            f"{avg_min:>6.0f} {avg_max:>6.0f} {avg_var:>10.1f} "
            f"{avg_sent:>6.0%} {avg_hdg:>6.0%} "
            f"{total_dups:>5} {score:>10.4f}"
        )
        if has_embed:
            row += f"  {f'{avg_embed:.2f}s' if avg_embed is not None else 'n/a':>9}"
        lines.append(row)

    lines.append(thin)
    lines.append("")

    # ── Per-document breakdown ────────────────────────────────────────
    if len(sources) > 1:
        lines.append("  PER-DOCUMENT BREAKDOWN")
        lines.append(thin)
        for source in sources:
            lines.append(f"  {source}")
            for strat in ranked:
                m_list = [m for m in metrics if m.strategy == strat and m.source == source]
                if not m_list:
                    continue
                m = m_list[0]
                lines.append(
                    f"    {strat:<10}  chunks={m.chunk_count:>3}  "
                    f"avg_size={m.avg_size:>5.0f}  "
                    f"rag={m.rag_score:.4f}"
                )
            lines.append("")
        lines.append(thin)
        lines.append("")

    # ── Quality warnings ─────────────────────────────────────────────
    warnings: list[str] = []
    for m in metrics:
        if m.empty_count > 0:
            warnings.append(
                f"  ⚠  [{m.strategy}/{m.source}] {m.empty_count} empty chunk(s) detected."
            )
        if m.oversized_count > 0:
            warnings.append(
                f"  ⚠  [{m.strategy}/{m.source}] {m.oversized_count} oversized chunk(s) "
                f"(>{MAX_CHUNK_SIZE} chars)."
            )
        if m.undersized_count > 0:
            warnings.append(
                f"  ⚠  [{m.strategy}/{m.source}] {m.undersized_count} undersized chunk(s) "
                f"(<{MIN_CHUNK_SIZE} chars)."
            )
        if m.duplicate_count > 0:
            warnings.append(
                f"  ⚠  [{m.strategy}/{m.source}] {m.duplicate_count} duplicate chunk(s)."
            )

    if warnings:
        lines.append("  QUALITY WARNINGS")
        lines.append(thin)
        lines.extend(warnings)
        lines.append("")

    # ── Winner and recommendation ────────────────────────────────────
    winner      = ranked[0]
    winner_score = mean_scores[winner]
    lines.append("  RECOMMENDATION")
    lines.append(thin)
    lines.append(f"  Recommended strategy: {winner.upper()}  (RAG score: {winner_score:.4f})")
    lines.append("")
    lines.append(f"  {_recommendation_reason(winner, metrics)}")
    lines.append("")
    lines.append("  Scoring weights used:")
    lines.append(f"    chunk_count={_W_CHUNK_COUNT}  avg_size={_W_AVG_SIZE}  "
                 f"variance={_W_SIZE_VARIANCE}")
    lines.append(f"    completeness={_W_COMPLETENESS}  headings={_W_HEADING_RATE}  "
                 f"duplicates={_W_DUPLICATE_RATE}")
    lines.append("")
    lines.append("  Note: run with --embed-timing for embedding speed comparison.")
    lines.append(sep)

    return "\n".join(lines)


def _recommendation_reason(winner: str, metrics: list[StrategyMetrics]) -> str:
    """Return a one-sentence rationale for the winning strategy."""
    winner_metrics = [m for m in metrics if m.strategy == winner]
    if not winner_metrics:
        return ""

    avg_size  = sum(m.avg_size      for m in winner_metrics) / len(winner_metrics)
    avg_score = sum(m.rag_score     for m in winner_metrics) / len(winner_metrics)
    avg_sent  = sum(m.sentence_rate for m in winner_metrics) / len(winner_metrics)

    reasons = {
        "section":  (
            f"Section chunking produced well-scoped chunks averaging "
            f"{avg_size:.0f} chars, with {avg_sent:.0%} containing complete sentences. "
            "Heading anchors improve retrieval precision."
        ),
        "sentence": (
            f"Sentence chunking produced semantically complete chunks averaging "
            f"{avg_size:.0f} chars. Dense sentence coverage ({avg_sent:.0%}) "
            "maximises embedding quality."
        ),
        "fixed":    (
            f"Fixed chunking produced consistent {avg_size:.0f}-char chunks with "
            "predictable size distribution, giving stable retrieval performance."
        ),
    }
    return reasons.get(winner, f"'{winner}' achieved the highest mean RAG score ({avg_score:.4f}).")


# ============================================================
# PRIVATE UTILITIES
# ============================================================

def _iso_now() -> str:
    """Return current UTC time as ISO-8601 string."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _replace(m: StrategyMetrics, **kwargs: Any) -> StrategyMetrics:
    """Return a new StrategyMetrics with specified fields replaced."""
    return dataclasses.replace(m, **kwargs)