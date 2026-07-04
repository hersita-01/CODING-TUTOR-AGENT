# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ ingest_documents.py
#
# CLI utility that reads every .txt file in python_docs/,
# chunks, embeds, and stores them in ChromaDB.
#
# Usage:
#   cd week5-memory/day3-vector-store
#   python ingest_documents.py
#   python ingest_documents.py --reset     # clear collection first
#   python ingest_documents.py --docs-dir path/to/docs
# -----------------------------------

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────
_here  = Path(__file__).resolve().parent
_day2  = _here.parent / "day2-embeddings"
_week5 = _here.parent

for _p in [str(_here), str(_day2), str(_week5)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chroma_manager   import ChromaManager
from document_chunker import DocumentChunker
from document_indexer import DocumentIndexer
from embedding_manager import EmbeddingManager

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("ingest_documents")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index Python tutorial .txt files into ChromaDB."
    )
    parser.add_argument(
        "--docs-dir",
        type    = Path,
        default = _here / "python_docs",
        help    = "Directory containing .txt tutorial files (default: python_docs/)",
    )
    parser.add_argument(
        "--reset",
        action  = "store_true",
        help    = "Clear the ChromaDB collection before indexing.",
    )
    parser.add_argument(
        "--strategy",
        type    = str,
        default = "section",
        choices = ["section", "sentence", "fixed", "auto"],
        help    = "Chunking strategy (default: section).",
    )
    args = parser.parse_args()

    docs_dir: Path = args.docs_dir
    reset:    bool = args.reset
    strategy: str  = args.strategy

    print()
    print("=" * 52)
    print("  WEEK 5 DAY 3 — Document Ingestion")
    print("=" * 52)
    print(f"  Docs directory : {docs_dir}")
    print(f"  Reset first    : {reset}")
    print(f"  Strategy       : {strategy}")
    print()

    if not docs_dir.is_dir():
        print(f"  ERROR: '{docs_dir}' is not a directory.")
        sys.exit(1)

    txt_files = sorted(
        p for p in docs_dir.glob("*.txt") if not p.name.startswith(".")
    )
    if not txt_files:
        print(f"  ERROR: No .txt files found in '{docs_dir}'.")
        sys.exit(1)

    print(f"  Found {len(txt_files)} file(s):")
    for f in txt_files:
        print(f"    - {f.name}")
    print()

    # Initialise components.
    print("  Loading embedding model …")
    t0       = time.time()
    indexer  = DocumentIndexer(
        chroma_manager    = ChromaManager(),
        embedding_manager = EmbeddingManager(),
        chunker           = DocumentChunker(strategy=strategy),
    )
    print(f"  Model ready ({time.time() - t0:.1f}s)")
    print()

    # Run ingestion.
    print("  Indexing …")
    t1     = time.time()
    result = indexer.index_directory(docs_dir, reset_first=reset)
    elapsed = time.time() - t1

    # Print summary.
    print()
    print("─" * 52)
    print(result.summary())
    print("─" * 52)
    print(f"  Completed in {elapsed:.1f}s")
    print()

    if result.errors:
        print("  Errors encountered:")
        for e in result.errors:
            print(f"    - {e}")
        print()

    if result.documents_stored == 0:
        print("  WARNING: No documents were stored.")
        sys.exit(1)

    print("  Ingestion complete. ChromaDB is ready for rag_search().")
    print()


if __name__ == "__main__":
    main()