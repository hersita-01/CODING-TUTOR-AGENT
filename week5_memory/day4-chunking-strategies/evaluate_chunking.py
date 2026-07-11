# -----------------------------------
# WEEK 5 – DAY 4: CHUNKING EVALUATION
# week5-memory/day4-chunking-eval/ evaluate_chunking.py
#
# CLI entry point for the chunking strategy evaluation.
#
# Usage:
#   cd week5-memory/day4-chunking-eval
#   python evaluate_chunking.py
#   python evaluate_chunking.py --docs-dir ../day3-vector-store/python_docs
#   python evaluate_chunking.py --file ../day3-vector-store/python_docs/loops.txt
#   python evaluate_chunking.py --preview
#   python evaluate_chunking.py --embed-timing
#   python evaluate_chunking.py --strategy section
#   python evaluate_chunking.py --save-report report.txt
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────
_here  = Path(__file__).resolve().parent
_day3  = _here.parent / "day3-vector-store"
_day2  = _here.parent / "day2-embeddings"
_week5 = _here.parent

for _p in [str(_here), str(_day3), str(_day2), str(_week5)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chunking_evaluator import ChunkingEvaluator, EvaluationReport, STRATEGIES
from document_chunker   import ChunkStrategy, DocumentChunker

logging.basicConfig(
    level  = logging.WARNING,
    format = "%(levelname)s  %(name)s  %(message)s",
)
log = logging.getLogger("evaluate_chunking")


# ============================================================
# DEFAULT PATHS
# ============================================================

_DEFAULT_DOCS_DIR = _day3 / "python_docs"


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Entry point for the Day 4 chunking evaluation CLI."""

    parser = argparse.ArgumentParser(
        description = "Week 5 Day 4 — Chunking Strategy Evaluator",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = """
Examples:
  python evaluate_chunking.py
  python evaluate_chunking.py --file python_docs/loops.txt
  python evaluate_chunking.py --preview --strategy section
  python evaluate_chunking.py --embed-timing --save-report report.txt
        """,
    )

    # ── Input source ─────────────────────────────────────────────────
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--docs-dir",
        type    = Path,
        default = _DEFAULT_DOCS_DIR,
        help    = f"Directory of .txt tutorial files (default: {_DEFAULT_DOCS_DIR})",
    )
    source_group.add_argument(
        "--file",
        type = Path,
        help = "Evaluate a single .txt file instead of a directory.",
    )

    # ── Evaluation options ────────────────────────────────────────────
    parser.add_argument(
        "--preview",
        action = "store_true",
        help   = "Print a preview of generated chunks for each strategy.",
    )
    parser.add_argument(
        "--preview-chars",
        type    = int,
        default = 100,
        help    = "Maximum characters to show per chunk in preview (default: 100).",
    )
    parser.add_argument(
        "--strategy",
        choices = list(STRATEGIES),
        default = None,
        help    = "Preview and detail a single strategy only.",
    )
    parser.add_argument(
        "--embed-timing",
        action = "store_true",
        help   = "Measure embedding time per strategy (requires sentence-transformers).",
    )
    parser.add_argument(
        "--chunk-size",
        type    = int,
        default = 512,
        help    = "Character limit for fixed-size chunking (default: 512).",
    )
    parser.add_argument(
        "--overlap",
        type    = int,
        default = 64,
        help    = "Character overlap for fixed-size chunking (default: 64).",
    )

    # ── Output options ────────────────────────────────────────────────
    parser.add_argument(
        "--save-report",
        type = Path,
        help = "Save the evaluation report to a text file.",
    )
    parser.add_argument(
        "--verbose",
        action = "store_true",
        help   = "Enable DEBUG logging.",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # ── Banner ───────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  WEEK 5 DAY 4 — Chunking Strategy Evaluator")
    print("=" * 60)

    # ── Determine and validate input ─────────────────────────────────
    single_file: Path | None = args.file
    docs_dir:    Path | None = None if single_file else args.docs_dir

    if single_file:
        if not single_file.exists() or not single_file.is_file():
            log.error("File not found or not a file: '%s'.", single_file)
            sys.exit(1)
        print(f"  Mode         : single file")
        print(f"  File         : {single_file}")
    else:
        if not docs_dir.is_dir():
            log.error("Not a directory: '%s'.", docs_dir)
            sys.exit(1)
        txt_files = [p for p in docs_dir.glob("*.txt") if not p.name.startswith(".")]
        if not txt_files:
            log.error("No .txt tutorial files found in '%s'.", docs_dir)
            sys.exit(1)
        print(f"  Mode         : directory")
        print(f"  Docs dir     : {docs_dir}")
        print(f"  Files found  : {len(txt_files)}")

    print(f"  Embed timing : {args.embed_timing}")
    print(f"  Preview      : {args.preview}")
    if args.strategy:
        print(f"  Strategy     : {args.strategy} (detailed)")
    print()

    # ── Build evaluator ───────────────────────────────────────────────
    try:
        chunker = DocumentChunker(
            chunk_size = args.chunk_size,
            overlap    = args.overlap,
        )
        evaluator = ChunkingEvaluator(
            chunker            = chunker,
            measure_embed_time = args.embed_timing,
        )
    except ValueError as exc:
        log.error("Invalid chunker settings: %s", exc)
        sys.exit(1)
    except Exception as exc:
        log.error("Failed to initialise evaluator: %s", exc)
        sys.exit(1)

    # ── Run evaluation ────────────────────────────────────────────────
    t0 = time.perf_counter()

    if single_file:
        report = evaluator.evaluate_file(single_file)
    else:
        report = evaluator.evaluate_folder(docs_dir)

    elapsed = time.perf_counter() - t0

    # ── Print main report ─────────────────────────────────────────────
    print(report.summary)
    print(f"  Total evaluation time: {elapsed:.2f}s")
    print()

    # ── Optional chunk preview ────────────────────────────────────────
    if args.preview:
        _print_previews(
            evaluator  = evaluator,
            report     = report,
            single_file= single_file,
            docs_dir   = docs_dir,
            strategy   = args.strategy,
            max_chars  = args.preview_chars,
        )

    # ── Optional single-strategy detail ──────────────────────────────
    if args.strategy and not args.preview:
        _print_strategy_detail(report, args.strategy)

    # ── Save report ───────────────────────────────────────────────────
    if args.save_report:
        _save_report(report, args.save_report, elapsed)


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _print_previews(
    evaluator:   ChunkingEvaluator,
    report:      EvaluationReport,
    single_file: Path | None,
    docs_dir:    Path | None,
    strategy:    str | None,
    max_chars:   int,
) -> None:
    """Print chunk previews for each strategy using DocumentChunker directly.

    Parameters
    ----------
    evaluator:   ChunkingEvaluator instance (owns the chunker).
    report:      Completed evaluation report.
    single_file: Path to a single file, or None.
    docs_dir:    Path to docs directory, or None.
    strategy:    If set, only preview this strategy.
    max_chars:   Characters to show per chunk.
    """
    chunker = evaluator.chunker

    # Determine which files to preview.
    if single_file:
        files_to_preview = [single_file] if single_file.exists() else []
    elif docs_dir and docs_dir.is_dir():
        files_to_preview = sorted(
            p for p in docs_dir.glob("*.txt") if not p.name.startswith(".")
        )
    else:
        files_to_preview = []

    if not files_to_preview:
        print("  (no files to preview)")
        return

    strats_to_show = [strategy] if strategy else list(STRATEGIES)

    for path in files_to_preview:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"  Cannot read '{path.name}': {exc}")
            continue

        print(f"{'─' * 60}")
        print(f"  CHUNK PREVIEWS  —  {path.name}")
        print(f"{'─' * 60}")

        for strat in strats_to_show:
            try:
                chunks = chunker.chunk_text(text, source=path.name, strategy=strat)
            except Exception as exc:
                print(f"  [{strat}] Chunking failed: {exc}")
                continue

            print(f"\n  Strategy: {strat.upper()}  ({len(chunks)} chunks)")
            print(f"  {'─' * 40}")

            for i, chunk in enumerate(chunks[:5]):    # preview first 5 only
                preview = chunk.text[:max_chars].replace("\n", " ")
                if len(chunk.text) > max_chars:
                    preview += "…"
                print(f"  [{i:02d}] {chunk.char_count:>4} chars  {preview}")

            if len(chunks) > 5:
                print(f"  … and {len(chunks) - 5} more chunks.")
        print()


def _print_strategy_detail(report: EvaluationReport, strategy: str) -> None:
    """Print a detailed breakdown for one strategy across all sources.

    Parameters
    ----------
    report:   Completed evaluation report.
    strategy: Strategy name to detail.
    """
    metrics = [m for m in report.metrics if m.strategy == strategy]
    if not metrics:
        print(f"  No metrics found for strategy '{strategy}'.")
        return

    sep  = "─" * 60
    print(sep)
    print(f"  DETAILED VIEW — {strategy.upper()}")
    print(sep)

    for m in metrics:
        d = m.as_dict()
        print(f"  Source        : {d['source']}")
        print(f"  Chunks        : {d['chunks']}")
        print(f"  Avg size      : {d['avg_size']} chars")
        print(f"  Min / Max     : {d['min_size']} / {d['max_size']} chars")
        print(f"  Size variance : {d['size_variance']}")
        print(f"  Sentence rate : {d['sentence_rate']}")
        print(f"  Heading rate  : {d['heading_rate']}")
        print(f"  Code rate     : {d['code_rate']}")
        print(f"  Duplicates    : {d['duplicates']}")
        print(f"  Oversized     : {d['oversized']}")
        print(f"  Undersized    : {d['undersized']}")
        print(f"  Embed time    : {d['embed_time_s']}")
        print(f"  RAG score     : {d['rag_score']}")
        print(f"  Time taken    : {d['time_taken_s']}s")
        print()


def _save_report(
    report:  EvaluationReport,
    path:    Path,
    elapsed: float,
) -> None:
    """Save the evaluation report to a text file.

    Parameters
    ----------
    report:  The completed EvaluationReport.
    path:    Output file path.
    elapsed: Total evaluation time in seconds.
    """
    try:
        content = report.summary
        content += f"\n\nGenerated at : {report.generated_at}"
        content += f"\nTotal time   : {elapsed:.2f}s"
        content += f"\nWinner       : {report.winner}"
        content += f"\nRanking      : {' > '.join(report.ranked)}"
        path.write_text(content, encoding="utf-8")
        print(f"  Report saved to: {path}")
    except Exception as exc:
        log.error("Could not save report to '%s': %s", path, exc)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()