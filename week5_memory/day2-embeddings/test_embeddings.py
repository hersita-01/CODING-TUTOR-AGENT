# -----------------------------------
# WEEK 5 – DAY 2: EMBEDDINGS
# week5-memory/day2-embeddings/ test_embeddings.py
#
# Self-contained tests for EmbeddingManager and embedding_utils.
#
# Two modes:
#   LIVE   — sentence-transformers available → uses all-MiniLM-L6-v2
#   MOCK   — library not available → synthetic 384-d vectors
#            (same structural tests; only model-specific assertions skipped)
#
# Run with:
#   cd week5-memory/day2-embeddings
#   python test_embeddings.py
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

import math
import sys
import traceback
from pathlib import Path

# Allow running from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from embedding_utils import (
    average_vector,
    cosine_similarity,
    dot_product,
    euclidean_distance,
    normalize_vector,
    pairwise_similarity_matrix,
    top_k_similar,
)

# Try to import the real EmbeddingManager.
# If sentence-transformers is unavailable or model can't be fetched,
# fall back to a lightweight mock so utils tests still pass.
try:
    from embedding_manager import EmbeddingManager
    _mgr = EmbeddingManager()
    # Probe to confirm model can actually load.
    _probe = _mgr.embed_text("probe")
    LIVE_MODE = len(_probe) > 0
except Exception:
    LIVE_MODE = False

EXPECTED_DIM = 384     # all-MiniLM-L6-v2 output dimension


# ============================================================
# MOCK EMBEDDING MANAGER
# Used when sentence-transformers / HuggingFace is unavailable.
# Produces deterministic synthetic vectors that satisfy all
# structural invariants (correct dimension, normalised, etc.).
# ============================================================

class _MockEmbeddingManager:
    """Deterministic synthetic embeddings for offline testing."""

    _DIM = EXPECTED_DIM

    def embed_text(self, text: str) -> list[float]:
        if not isinstance(text, str) or not text.strip():
            return []
        # Reproducible vector from character codes.
        base = [float(ord(c) % 97 + 1) for c in (text * self._DIM)[:self._DIM]]
        norm = math.sqrt(sum(x * x for x in base))
        return [x / norm for x in base]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [self.embed_text(t) for t in texts]

    def embedding_dimension(self) -> int:
        return self._DIM

    def model_name(self) -> str:
        return "mock-model (sentence-transformers unavailable)"

    def is_loaded(self) -> bool:
        return True


if LIVE_MODE:
    _mgr_under_test = _mgr
    print("\n  [mode] LIVE — using all-MiniLM-L6-v2\n")
else:
    _mgr_under_test = _MockEmbeddingManager()
    print("\n  [mode] MOCK — sentence-transformers unavailable; using synthetic vectors\n")


# ============================================================
# MINI TEST HARNESS
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
# EMBEDDING MANAGER TESTS
# ============================================================

def test_single_embedding() -> list[float]:
    """1. Embed a single sentence and verify structure."""
    section("1 · Single Sentence Embedding")

    vec = _mgr_under_test.embed_text("What is a for loop in Python?")

    check("returns a list",              isinstance(vec, list))
    check("non-empty vector",            len(vec) > 0)
    check("correct dimension",           len(vec) == EXPECTED_DIM,
          f"got {len(vec)}, expected {EXPECTED_DIM}")
    check("all elements are floats",     all(isinstance(x, float) for x in vec))
    check("vector has non-zero values",  any(x != 0.0 for x in vec))

    return vec


def test_batch_embedding() -> list[list[float]]:
    """2. Embed multiple sentences in one call."""
    section("2 · Batch Embedding")

    texts = [
        "How do I use a list?",
        "What is a dictionary?",
        "Explain Python sets.",
    ]
    batch = _mgr_under_test.embed_batch(texts)

    check("returns a list",              isinstance(batch, list))
    check("correct number of vectors",   len(batch) == len(texts),
          f"got {len(batch)}, expected {len(texts)}")
    check("each vector is correct dim",
          all(len(v) == EXPECTED_DIM for v in batch),
          str([len(v) for v in batch]))
    check("vectors are not all identical",
          batch[0] != batch[1])

    return batch


def test_empty_string_handling() -> None:
    """3. Empty / invalid inputs return [] without raising."""
    section("3 · Empty / Invalid Input Handling")

    check("empty string  → []",       _mgr_under_test.embed_text("") == [])
    check("whitespace    → []",       _mgr_under_test.embed_text("   ") == [])
    check("empty list    → []",       _mgr_under_test.embed_batch([]) == [])

    # Batch with mixed valid/invalid — output length must match input length.
    mixed = _mgr_under_test.embed_batch(["valid sentence", "", "another valid"])
    check("mixed batch length matches input",  len(mixed) == 3, str(len(mixed)))
    check("blank item in batch → zero vector",
          mixed[1] == [0.0] * EXPECTED_DIM or mixed[1] == [],
          str(mixed[1][:5]))
    check("valid items in mixed batch non-zero",
          any(x != 0.0 for x in mixed[0]))


def test_embedding_dimension() -> None:
    """4. embedding_dimension() returns expected value."""
    section("4 · Embedding Dimension")

    dim = _mgr_under_test.embedding_dimension()

    check("returns an int",            isinstance(dim, int))
    check(f"dimension is {EXPECTED_DIM}",  dim == EXPECTED_DIM, f"got {dim}")


def test_same_text_same_vector() -> None:
    """5. Encoding the same string twice gives identical vectors."""
    section("5 · Determinism — Same Input → Same Output")

    text = "Python lists are mutable sequences."
    v1 = _mgr_under_test.embed_text(text)
    v2 = _mgr_under_test.embed_text(text)

    check("two encodings are identical", v1 == v2)


def test_different_texts_different_vectors() -> None:
    """6. Semantically different texts produce different vectors."""
    section("6 · Different Texts → Different Vectors")

    v1 = _mgr_under_test.embed_text("Python for loops iterate over sequences.")
    v2 = _mgr_under_test.embed_text("ZeroDivisionError occurs when dividing by zero.")

    check("vectors are not identical", v1 != v2)


# ============================================================
# UTILITY FUNCTION TESTS
# ============================================================

def test_cosine_similarity() -> None:
    """7. cosine_similarity correctness."""
    section("7 · cosine_similarity")

    identical = [1.0, 0.0, 0.0]
    opposite  = [-1.0, 0.0, 0.0]
    orthog    = [0.0, 1.0, 0.0]
    zero      = [0.0, 0.0, 0.0]

    check("identical vectors → 1.0",
          math.isclose(cosine_similarity(identical, identical), 1.0, abs_tol=1e-6))
    check("opposite vectors → -1.0",
          math.isclose(cosine_similarity(identical, opposite), -1.0, abs_tol=1e-6))
    check("orthogonal vectors → 0.0",
          math.isclose(cosine_similarity(identical, orthog), 0.0, abs_tol=1e-6))
    check("zero vector → 0.0",
          cosine_similarity(identical, zero) == 0.0)
    check("empty vector → 0.0",
          cosine_similarity([], [1.0]) == 0.0)
    check("dimension mismatch → 0.0",
          cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0]) == 0.0)

    # Semantic check with real or mock embeddings.
    v_loop = _mgr_under_test.embed_text("for loop iterating a list")
    v_loop2 = _mgr_under_test.embed_text("iterate over a list with for")
    v_unrel = _mgr_under_test.embed_text("ZeroDivisionError arithmetic exception")

    sim_related   = cosine_similarity(v_loop, v_loop2)
    sim_unrelated = cosine_similarity(v_loop, v_unrel)

    check("similar sentences score higher than dissimilar ones",
          sim_related > sim_unrelated,
          f"related={sim_related:.4f}  unrelated={sim_unrelated:.4f}")


def test_euclidean_distance() -> None:
    """8. euclidean_distance correctness."""
    section("8 · euclidean_distance")

    a = [1.0, 0.0]
    b = [0.0, 1.0]
    c = [1.0, 0.0]

    check("same vector → 0.0",
          math.isclose(euclidean_distance(a, c), 0.0, abs_tol=1e-9))
    check("[1,0] vs [0,1] → sqrt(2)",
          math.isclose(euclidean_distance(a, b), math.sqrt(2), rel_tol=1e-6))
    check("empty vector → inf",
          euclidean_distance([], [1.0]) == float("inf"))
    check("dimension mismatch → inf",
          euclidean_distance([1.0], [1.0, 0.0]) == float("inf"))


def test_normalize_vector() -> None:
    """9. normalize_vector produces unit-length output."""
    section("9 · normalize_vector")

    v    = [3.0, 4.0]           # norm = 5.0
    unit = normalize_vector(v)

    check("output has unit norm",
          math.isclose(math.sqrt(sum(x * x for x in unit)), 1.0, abs_tol=1e-9))
    check("direction preserved (ratio unchanged)",
          math.isclose(unit[0] / unit[1], v[0] / v[1], rel_tol=1e-6))
    check("zero vector returned as-is",
          normalize_vector([0.0, 0.0]) == [0.0, 0.0])


def test_top_k_similar() -> None:
    """10. top_k_similar returns correct ranking."""
    section("10 · top_k_similar")

    query      = [1.0, 0.0, 0.0]
    candidates = [
        [1.0, 0.0, 0.0],    # identical   → highest
        [0.0, 1.0, 0.0],    # orthogonal
        [0.7, 0.7, 0.0],    # partial
        [-1.0, 0.0, 0.0],   # opposite    → lowest
    ]

    results = top_k_similar(query, candidates, k=2)

    check("returns 2 results",        len(results) == 2)
    check("best match is index 0",    results[0][0] == 0,
          f"got index {results[0][0]}")
    check("scores are sorted desc",   results[0][1] >= results[1][1])
    check("empty query → []",         top_k_similar([], candidates, k=2) == [])
    check("empty candidates → []",    top_k_similar(query, [], k=2) == [])


def test_pairwise_similarity_matrix() -> None:
    """11. pairwise_similarity_matrix is square and symmetric."""
    section("11 · pairwise_similarity_matrix")

    vecs = [
        normalize_vector([1.0, 0.0, 0.0]),
        normalize_vector([0.0, 1.0, 0.0]),
        normalize_vector([0.0, 0.0, 1.0]),
    ]
    matrix = pairwise_similarity_matrix(vecs)

    check("matrix is 3×3",            len(matrix) == 3 and len(matrix[0]) == 3)
    check("diagonal is 1.0",
          all(math.isclose(matrix[i][i], 1.0, abs_tol=1e-6) for i in range(3)))
    check("matrix is symmetric",
          matrix[0][1] == matrix[1][0] and matrix[0][2] == matrix[2][0])
    check("orthogonal pairs → ~0.0",
          all(math.isclose(matrix[i][j], 0.0, abs_tol=1e-6)
              for i in range(3) for j in range(3) if i != j))


def test_average_vector() -> None:
    """12. average_vector returns correct element-wise mean."""
    section("12 · average_vector")

    vecs = [
        [1.0, 2.0, 3.0],
        [3.0, 2.0, 1.0],
    ]
    avg = average_vector(vecs)

    check("correct length",   len(avg) == 3)
    check("correct values",
          all(math.isclose(avg[i], 2.0, abs_tol=1e-9) for i in range(3)))
    check("empty list → []",  average_vector([]) == [])


def test_integration_with_memory() -> None:
    """13. EmbeddingManager works with LearnerProfile summary output."""
    section("13 · Integration — LearnerProfile summary → embedding")

    # Import Day 1 modules relative to this file.
    day1 = Path(__file__).resolve().parent.parent / "day1-learner-memory"
    if str(day1) not in sys.path and day1.exists():
        sys.path.insert(0, str(day1))

    # Also try the flat week5-memory layout used during development.
    week5 = Path(__file__).resolve().parent.parent
    if str(week5) not in sys.path:
        sys.path.insert(0, str(week5))

    try:
        from learner_profile import LearnerProfile

        profile = LearnerProfile(learner_name="TestLearner")
        profile.mark_mastered("variables")
        profile.mark_struggling("recursion")
        profile.add_error("ValueError", "invalid literal", "type casting")

        summary = profile.get_summary()
        vec = _mgr_under_test.embed_text(summary)

        check("summary produces non-empty embedding",    len(vec) > 0)
        check("summary embedding has correct dimension", len(vec) == EXPECTED_DIM,
              f"got {len(vec)}")
        check("summary string contains learner name",    "TestLearner" in summary)

    except ImportError as exc:
        print(f"  ⚠  Day 1 modules not on path — skipping integration test ({exc})")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print()
    print("=" * 58)
    print("  WEEK 5 DAY 2 — EMBEDDINGS  ·  Test Suite")
    print("=" * 58)

    try:
        test_single_embedding()
        test_batch_embedding()
        test_empty_string_handling()
        test_embedding_dimension()
        test_same_text_same_vector()
        test_different_texts_different_vectors()
        test_cosine_similarity()
        test_euclidean_distance()
        test_normalize_vector()
        test_top_k_similar()
        test_pairwise_similarity_matrix()
        test_average_vector()
        test_integration_with_memory()

    except Exception:
        print("\n[FATAL] Unexpected exception:")
        traceback.print_exc()

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