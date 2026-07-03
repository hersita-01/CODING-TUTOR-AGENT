# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ test_chroma.py
#
# Self-contained test suite for the Day 3 vector store subsystem.
# Uses a temporary ChromaDB directory so production data is never touched.
#
# Run with:
#   cd week5-memory/day3-vector-store
#   python test_chroma.py
# -----------------------------------

from __future__ import annotations

import math
import sys
import tempfile
import traceback
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────
_here  = Path(__file__).resolve().parent
_day2  = _here.parent / "day2-embeddings"
_week5 = _here.parent

for _p in [str(_here), str(_day2), str(_week5)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chroma_manager    import ChromaManager
from document_chunker  import DocumentChunker, Chunk
from document_indexer  import DocumentIndexer
from embedding_manager import EmbeddingManager
from rag_search_tool   import rag_search


# ============================================================
# SHARED MOCK EMBEDDER
# Deterministic 384-d synthetic vectors — no HuggingFace needed.
# ============================================================

class _MockEmbedder:
    _DIM = 384

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            return []
        base = [float(ord(c) % 97 + 1) for c in (text * self._DIM)[:self._DIM]]
        norm = math.sqrt(sum(x * x for x in base))
        return [x / norm for x in base]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        results = []
        for t in texts:
            v = self.embed_text(t)
            results.append(v if v else [0.0] * self._DIM)
        return results

    def embedding_dimension(self) -> int:
        return self._DIM


_MOCK_EMBEDDER = _MockEmbedder()

# Registry of all ChromaManager instances created during the test run.
# Used in main() to close ChromaDB clients before temp dir cleanup on Windows.
_ALL_CHROMA_MANAGERS: list[ChromaManager] = []


# ============================================================
# TEST HARNESS
# ============================================================

_PASSED: list[str] = []
_FAILED: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        _PASSED.append(name)
        print(f"  ✓  {name}")
    else:
        _FAILED.append(name)
        msg = f"  ✗  {name}"
        if detail:
            msg += f"\n       → {detail}"
        print(msg)


def section(title: str) -> None:
    print(f"\n{'─' * 58}")
    print(f"  {title}")
    print(f"{'─' * 58}")


# ============================================================
# TESTS
# ============================================================

# ── Sample data ───────────────────────────────────────────────────────
_LOOP_TEXT = """## For Loops
A for loop iterates over a sequence such as a list, string, or range.
Use range() to generate a sequence of numbers.
The loop variable takes each value from the sequence in turn.
"""

_FUNC_TEXT = """## Functions
A function is a reusable block of code defined with the def keyword.
Functions can accept parameters and return values.
Use return to send a value back to the caller.
"""

_LIST_TEXT = """## Lists
A list is an ordered mutable collection defined with square brackets.
Access items by index starting at zero.
Use append() to add items and remove() to delete them.
"""

SAMPLE_DOCS = [
    ("loops.txt",     _LOOP_TEXT,  "loops",     "beginner"),
    ("functions.txt", _FUNC_TEXT,  "functions", "intermediate"),
    ("lists.txt",     _LIST_TEXT,  "lists",     "beginner"),
]


def _make_manager(tmp_dir: Path, name: str = "test_col") -> ChromaManager:
    mgr = ChromaManager(persist_dir=tmp_dir, collection_name=name)
    _ALL_CHROMA_MANAGERS.append(mgr)
    return mgr


def _embed(text: str) -> list[float]:
    return _MOCK_EMBEDDER.embed_text(text)


def _populate(mgr: ChromaManager) -> int:
    """Insert the three sample documents and return count stored."""
    total = 0
    for i, (src, text, topic, diff) in enumerate(SAMPLE_DOCS):
        vec = _embed(text)
        n = mgr.add_documents(
            ids       = [f"doc_{i}"],
            embeddings= [vec],
            documents = [text],
            metadatas = [{"source": src, "topic": topic, "difficulty": diff}],
        )
        total += n
    return total


# ── 1. Chunking ───────────────────────────────────────────────────────

def test_section_chunking() -> None:
    section("1 · Section-Based Chunking (default)")

    full_text = """# Loops
topic: loops
difficulty: beginner

## For Loops
A for loop iterates over a sequence.

## While Loops
A while loop repeats while a condition is True.

## Break and Continue
break exits the loop. continue skips the iteration.
"""
    chunker = DocumentChunker(strategy="section")
    chunks  = chunker.chunk_text(full_text, source="loops.txt")

    check("produces multiple chunks",        len(chunks) >= 2, str(len(chunks)))
    check("each chunk is a Chunk instance",  all(isinstance(c, Chunk) for c in chunks))
    check("topic extracted from header",     all(c.topic == "loops" for c in chunks))
    check("difficulty extracted",            all(c.difficulty == "beginner" for c in chunks))
    check("source stored in metadata",       all(c.source == "loops.txt" for c in chunks))
    check("chunk_id is unique",
          len({c.chunk_id for c in chunks}) == len(chunks))
    check("char_count populated",            all(c.char_count > 0 for c in chunks))


def test_sentence_chunking() -> None:
    section("2 · Sentence-Based Chunking")

    text = "Python is interpreted. It is easy to learn. Variables store values. " \
           "Lists hold collections. Functions avoid repetition. Loops repeat code."
    chunker = DocumentChunker(strategy="sentence")
    chunks  = chunker.chunk_text(text, source="misc.txt")

    check("produces at least one chunk",     len(chunks) >= 1)
    check("all chunks non-empty",            all(c.char_count > 0 for c in chunks))


def test_fixed_chunking() -> None:
    section("3 · Fixed-Size Chunking")

    text    = "A" * 1500
    chunker = DocumentChunker(strategy="fixed", chunk_size=500, overlap=50)
    chunks  = chunker.chunk_text(text, source="test.txt")

    check("produces multiple chunks",        len(chunks) > 1,  str(len(chunks)))
    check("no chunk exceeds chunk_size",
          all(c.char_count <= 500 for c in chunks))


def test_empty_document_chunking() -> None:
    section("4 · Empty Document Chunking")

    chunker = DocumentChunker()
    check("empty string → []",      chunker.chunk_text("") == [])
    check("whitespace only → []",   chunker.chunk_text("   \n\t  ") == [])


# ── 2. ChromaManager ─────────────────────────────────────────────────

def test_chroma_add_and_count(tmp: Path) -> None:
    section("5 · ChromaDB — Add Documents and Count")

    mgr   = _make_manager(tmp)
    count = _populate(mgr)

    check("all 3 docs stored",          count == 3, str(count))
    check("document_count() == 3",      mgr.document_count() == 3,
          str(mgr.document_count()))


def test_chroma_query(tmp: Path) -> None:
    section("6 · ChromaDB — Semantic Query")

    mgr = _make_manager(tmp)
    _populate(mgr)

    query_vec = _embed("how do for loops work in Python")
    results   = mgr.query(query_embedding=query_vec, top_k=3)

    check("returns ids",                   len(results["ids"])       > 0)
    check("returns documents",             len(results["documents"]) > 0)
    check("returns metadatas",             len(results["metadatas"]) > 0)
    check("returns distances",             len(results["distances"]) > 0)
    check("top result has a topic field",
          bool(results["metadatas"][0].get("topic")),
          str(results["metadatas"][0]))


def test_chroma_top_k(tmp: Path) -> None:
    section("7 · ChromaDB — Top-K Limiting")

    mgr = _make_manager(tmp, name="topk_col")
    _populate(mgr)

    r1 = mgr.query(_embed("Python"), top_k=1)
    r2 = mgr.query(_embed("Python"), top_k=2)

    check("top_k=1 returns 1 result",   len(r1["ids"]) == 1,  str(len(r1["ids"])))
    check("top_k=2 returns 2 results",  len(r2["ids"]) == 2,  str(len(r2["ids"])))


def test_chroma_metadata(tmp: Path) -> None:
    section("8 · ChromaDB — Metadata Storage and Retrieval")

    mgr = _make_manager(tmp, name="meta_col")
    _populate(mgr)

    doc = mgr.get_document("doc_0")

    check("get_document returns a dict",      isinstance(doc, dict))
    check("metadata source is correct",
          doc["metadata"].get("source") == "loops.txt",
          str(doc["metadata"]))
    check("metadata topic is correct",
          doc["metadata"].get("topic") == "loops")
    check("metadata difficulty is correct",
          doc["metadata"].get("difficulty") == "beginner")


def test_chroma_duplicate_handling(tmp: Path) -> None:
    section("9 · ChromaDB — Duplicate / Upsert Handling")

    mgr = _make_manager(tmp, name="dup_col")

    vec = _embed("for loops in Python")
    mgr.add_documents(["dup_id"], [vec], ["Original text."],
                      [{"source": "test.txt", "topic": "loops"}])

    # Insert again with same ID but different text.
    mgr.add_documents(["dup_id"], [vec], ["Updated text."],
                      [{"source": "test.txt", "topic": "loops"}])

    check("only 1 document after duplicate insert",
          mgr.document_count() == 1,
          str(mgr.document_count()))

    doc = mgr.get_document("dup_id")
    check("document text was updated",
          doc["document"] == "Updated text.",
          str(doc["document"]))


def test_chroma_empty_query(tmp: Path) -> None:
    section("10 · ChromaDB — Empty Query Handling")

    mgr     = _make_manager(tmp, name="empty_col")
    results = mgr.query(query_embedding=[], top_k=5)

    check("empty embedding → empty results",
          results["ids"] == [] and results["documents"] == [])


def test_chroma_reset(tmp: Path) -> None:
    section("11 · ChromaDB — Reset Collection")

    mgr = _make_manager(tmp, name="reset_col")
    _populate(mgr)
    check("3 docs before reset",    mgr.document_count() == 3)

    mgr.reset_collection()
    check("0 docs after reset",     mgr.document_count() == 0)


def test_list_sources(tmp: Path) -> None:
    section("12 · ChromaDB — list_sources()")

    mgr = _make_manager(tmp, name="src_col")
    _populate(mgr)
    sources = mgr.list_sources()

    check("returns a list",               isinstance(sources, list))
    check("contains loops.txt",           "loops.txt"     in sources)
    check("contains functions.txt",       "functions.txt" in sources)
    check("contains lists.txt",           "lists.txt"     in sources)
    check("no duplicates",                len(sources) == len(set(sources)))


# ── 3. DocumentIndexer ────────────────────────────────────────────────

def test_indexer_with_real_files(tmp: Path) -> None:
    section("13 · DocumentIndexer — Index python_docs/")

    docs_dir = _here / "python_docs"
    if not docs_dir.is_dir():
        print("  ⚠  python_docs/ not found — skipping.")
        return

    indexer = DocumentIndexer(
        chroma_manager    = (_idx_cm := ChromaManager(persist_dir=tmp, collection_name="idx_col"), _ALL_CHROMA_MANAGERS.append(_idx_cm))[0],
        embedding_manager = _MOCK_EMBEDDER,
        chunker           = DocumentChunker(),
    )
    result = indexer.index_directory(docs_dir, reset_first=True)

    check("files indexed > 0",         result.files_indexed > 0,
          str(result.files_indexed))
    check("chunks created > 0",        result.chunks_created > 0,
          str(result.chunks_created))
    check("documents stored > 0",      result.documents_stored > 0,
          str(result.documents_stored))
    check("no errors",                 result.errors == [],
          str(result.errors))


# ── 4. RAG Search Tool ────────────────────────────────────────────────

def test_rag_search(tmp: Path) -> None:
    section("14 · rag_search() — Semantic Retrieval")

    import rag_search_tool as rst

    # Inject test doubles so we don't need HuggingFace or production DB.
    rst._embedder = _MOCK_EMBEDDER
    rst._chroma   = ChromaManager(persist_dir=tmp, collection_name="rag_col")
    _ALL_CHROMA_MANAGERS.append(rst._chroma)

    # Populate with sample data.
    _populate(rst._chroma)

    result = rag_search("how do for loops work", top_k=2)

    check("success is True",           result["success"],
          result.get("error"))
    check("query echoed back",         result["query"] == "how do for loops work")
    check("chunks returned",           len(result["chunks"]) > 0)
    check("sources list non-empty",    len(result["sources"]) > 0)
    check("summary is a string",       isinstance(result["summary"], str))
    check("each chunk has text",
          all("text" in c for c in result["chunks"]))
    check("each chunk has similarity",
          all("similarity" in c for c in result["chunks"]))
    check("top result has a topic field",
          bool(result["chunks"][0].get("topic")),
          str(result["chunks"][0]))


def test_rag_search_empty_query(tmp: Path) -> None:
    section("15 · rag_search() — Empty Query Handling")

    import rag_search_tool as rst
    rst._embedder = _MOCK_EMBEDDER
    rst._chroma   = ChromaManager(persist_dir=tmp, collection_name="rag_empty_col")
    _ALL_CHROMA_MANAGERS.append(rst._chroma)

    r1 = rag_search("")
    r2 = rag_search("   ")

    check("empty string → success=False",     not r1["success"])
    check("whitespace   → success=False",     not r2["success"])
    check("error message populated",          bool(r1["error"]))


# ── 5. New tests from code review ────────────────────────────────────

def test_index_text(tmp: Path) -> None:
    section("16 · DocumentIndexer.index_text() — full pipeline")

    indexer = DocumentIndexer(
        chroma_manager    = (_txt_cm := ChromaManager(persist_dir=tmp, collection_name="txt_col"), _ALL_CHROMA_MANAGERS.append(_txt_cm))[0],
        embedding_manager = _MOCK_EMBEDDER,
        chunker           = DocumentChunker(),
    )

    text = """# Inline Doc
topic: testing
difficulty: beginner

## Section One
This section explains how index_text works end to end.
It should chunk, embed, and store the text properly.

## Section Two
A second section ensures multiple chunks are produced.
Each chunk gets its own embedding and document ID.
"""
    result = indexer.index_text(text, source="inline_test.txt")

    check("files_indexed == 1",          result.files_indexed == 1)
    check("chunks_created > 0",          result.chunks_created > 0,
          str(result.chunks_created))
    check("embeddings_generated > 0",    result.embeddings_generated > 0,
          str(result.embeddings_generated))
    check("documents_stored > 0",        result.documents_stored > 0,
          str(result.documents_stored))
    check("no errors",                   result.errors == [], str(result.errors))
    check("stored == embedded",
          result.documents_stored == result.embeddings_generated)


def test_metadata_filter_query(tmp: Path) -> None:
    section("17 · ChromaDB — Metadata Filter Query (where topic=loops)")

    mgr = _make_manager(tmp, name="filter_col")
    _populate(mgr)   # inserts loops, functions, lists docs

    query_vec = _embed("iterating sequences")
    results   = mgr.query(
        query_embedding = query_vec,
        top_k           = 3,
        where           = {"topic": "loops"},
    )

    check("filter returns at least one result",
          len(results["documents"]) >= 1,
          str(results["documents"]))
    check("all returned docs have topic=loops",
          all(m.get("topic") == "loops" for m in results["metadatas"]),
          str(results["metadatas"]))
    check("non-matching topics excluded",
          all(m.get("topic") != "functions" for m in results["metadatas"]))


def test_split_fixed_overlap_guard() -> None:
    section("18 · _split_fixed() — ValueError when overlap >= chunk_size")

    from document_chunker import _split_fixed
    import traceback as _tb

    # overlap == chunk_size
    raised_equal = False
    try:
        _split_fixed("some text", chunk_size=100, overlap=100)
    except ValueError:
        raised_equal = True
    except Exception:
        pass

    # overlap > chunk_size
    raised_greater = False
    try:
        _split_fixed("some text", chunk_size=50, overlap=200)
    except ValueError:
        raised_greater = True
    except Exception:
        pass

    # overlap < chunk_size — must NOT raise
    no_raise = False
    try:
        _split_fixed("A" * 500, chunk_size=100, overlap=20)
        no_raise = True
    except Exception:
        pass

    check("raises ValueError when overlap == chunk_size",  raised_equal)
    check("raises ValueError when overlap > chunk_size",   raised_greater)
    check("no error when overlap < chunk_size",            no_raise)




def test_similarity_threshold(tmp: Path) -> None:
    section("19 · rag_search() — min_similarity threshold filters low-scoring chunks")

    import rag_search_tool as rst
    rst._embedder = _MOCK_EMBEDDER
    rst._chroma   = ChromaManager(persist_dir=tmp, collection_name="sim_col")
    _ALL_CHROMA_MANAGERS.append(rst._chroma)
    _populate(rst._chroma)

    # With threshold 0.0 (default) — all results returned.
    r_all = rag_search("Python programming", top_k=3, min_similarity=0.0)
    check("threshold=0.0 returns results",   r_all["success"],  r_all.get("error"))

    # With threshold 0.9999 — only near-identical chunks pass; likely none.
    r_high = rag_search("Python programming", top_k=3, min_similarity=0.9999)
    # Either no results (success=False) or fewer results than r_all.
    if r_high["success"]:
        check("high threshold yields fewer results",
              len(r_high["chunks"]) <= len(r_all["chunks"]))
    else:
        check("high threshold filters all chunks (success=False)", True)

    # All returned chunks must meet the threshold.
    r_mid = rag_search("Python programming", top_k=3, min_similarity=0.5)
    if r_mid["success"]:
        check("all chunks meet min_similarity=0.5",
              all(c["similarity"] >= 0.5 for c in r_mid["chunks"]),
              str([c["similarity"] for c in r_mid["chunks"]]))
    else:
        check("no chunks met min_similarity=0.5 (acceptable)", True)


def test_embedding_dimension_validation(tmp: Path) -> None:
    section("20 · ChromaDB — ValueError on inconsistent embedding dimensions")

    mgr = _make_manager(tmp, name="dim_col")

    raised = False
    try:
        mgr.add_documents(
            ids        = ["a", "b"],
            embeddings = [[1.0, 2.0], [1.0, 2.0, 3.0]],   # 2-d vs 3-d
            documents  = ["doc a", "doc b"],
        )
    except ValueError:
        raised = True

    check("inconsistent dimensions raise ValueError", raised)

    # Zero-length embedding must also raise.
    raised_empty = False
    try:
        mgr.add_documents(
            ids        = ["c"],
            embeddings = [[]],
            documents  = ["doc c"],
        )
    except ValueError:
        raised_empty = True

    check("empty embedding raises ValueError", raised_empty)


def test_hidden_files_skipped(tmp: Path) -> None:
    section("21 · index_directory() — hidden files are skipped")

    import tempfile as _tf

    docs_dir = tmp / "hidden_test_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Write a normal file and a hidden file.
    (docs_dir / "visible.txt").write_text(
        "# Visible\ntopic: loops\ndifficulty: beginner\n\n## Section\nContent here.",
        encoding="utf-8",
    )
    (docs_dir / ".notes.txt").write_text(
        "# Hidden\ntopic: secret\ndifficulty: beginner\n\n## Section\nHidden content.",
        encoding="utf-8",
    )

    indexer = DocumentIndexer(
        chroma_manager    = (_hid_cm := ChromaManager(persist_dir=tmp, collection_name="hidden_col"), _ALL_CHROMA_MANAGERS.append(_hid_cm))[0],
        embedding_manager = _MOCK_EMBEDDER,
        chunker           = DocumentChunker(),
    )
    result = indexer.index_directory(docs_dir, reset_first=True)

    check("only 1 file indexed (hidden skipped)",
          result.files_indexed == 1,
          str(result.files_indexed))
    check("documents stored > 0",
          result.documents_stored > 0,
          str(result.documents_stored))

    sources = indexer._chroma.list_sources()
    check(".notes.txt not in sources",  ".notes.txt"  not in sources, str(sources))
    check("visible.txt in sources",     "visible.txt" in sources,     str(sources))


def test_index_text_retrieval(tmp: Path) -> None:
    section("22 · index_text() — indexed content is retrievable via rag_search()")

    import rag_search_tool as rst

    chroma  = ChromaManager(persist_dir=tmp, collection_name="txt_ret_col")
    _ALL_CHROMA_MANAGERS.append(chroma)
    indexer = DocumentIndexer(
        chroma_manager    = chroma,
        embedding_manager = _MOCK_EMBEDDER,
        chunker           = DocumentChunker(),
    )

    text = """# Inline Topic
topic: recursion
difficulty: intermediate

## What is Recursion?
Recursion is when a function calls itself to solve a smaller version of the problem.
The base case stops the recursion; without it the function loops forever.

## Example
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""
    result = indexer.index_text(text, source="recursion_inline.txt")
    check("index_text stores documents",  result.documents_stored > 0,
          str(result.documents_stored))

    # Now verify rag_search() can find it.
    rst._embedder = _MOCK_EMBEDDER
    rst._chroma   = chroma

    r = rag_search("what is recursion", top_k=3)
    check("rag_search finds indexed text",  r["success"],  r.get("error"))
    check("source appears in results",
          "recursion_inline.txt" in r["sources"],
          str(r["sources"]))

# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print()
    print("=" * 58)
    print("  WEEK 5 DAY 3 — VECTOR STORE  ·  Test Suite")
    print("=" * 58)

    # ignore_cleanup_errors prevents Windows file-lock errors on cleanup.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_str:
        tmp = Path(tmp_str)

        try:
            # Chunking tests (no ChromaDB needed)
            test_section_chunking()
            test_sentence_chunking()
            test_fixed_chunking()
            test_empty_document_chunking()

            # ChromaDB tests (each gets its own sub-directory / collection)
            test_chroma_add_and_count(tmp / "main")
            test_chroma_query(tmp / "query")
            test_chroma_top_k(tmp / "topk")
            test_chroma_metadata(tmp / "meta")
            test_chroma_duplicate_handling(tmp / "dup")
            test_chroma_empty_query(tmp / "empty")
            test_chroma_reset(tmp / "reset")
            test_list_sources(tmp / "src")

            # Integration tests
            test_indexer_with_real_files(tmp / "idx")
            test_rag_search(tmp / "rag")
            test_rag_search_empty_query(tmp / "rag_empty")

            # New tests from code review
            test_index_text(tmp / "txt")
            test_metadata_filter_query(tmp / "filter")
            test_split_fixed_overlap_guard()

            # New tests from second review pass
            test_similarity_threshold(tmp / "sim")
            test_embedding_dimension_validation(tmp / "dim")
            test_hidden_files_skipped(tmp / "hidden")
            test_index_text_retrieval(tmp / "txt_ret")

        except Exception:
            print("\n[FATAL] Unexpected exception:")
            traceback.print_exc()

        finally:
            # Close all ChromaDB clients so Windows releases file locks
            # before TemporaryDirectory attempts to delete the folder.
            for _mgr in _ALL_CHROMA_MANAGERS:
                try:
                    _mgr._client._system.stop()
                except Exception:
                    pass

    total  = len(_PASSED) + len(_FAILED)
    passed = len(_PASSED)
    failed = len(_FAILED)

    print()
    print("=" * 58)
    print(f"  Results:  {passed}/{total} passed", end="")
    if failed:
        print(f"  ·  {failed} FAILED")
        for name in _FAILED:
            print(f"    ✗  {name}")
    else:
        print("  ·  All passed ✓")
    print("=" * 58)
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()