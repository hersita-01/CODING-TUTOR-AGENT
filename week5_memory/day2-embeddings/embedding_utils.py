# -----------------------------------
# WEEK 5 – DAY 2: EMBEDDINGS
# week5-memory/day2-embeddings/ embedding_utils.py
#
# Pure vector utility functions.
# No model loading, no I/O, no external state.
#
# These helpers are consumed by:
#   Day 2 → test_embeddings.py (similarity checks)
#   Day 3 → ChromaDB result re-ranking
#   Day 5 → RAG retrieval scoring
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import logging
import math
from typing import Union

log = logging.getLogger("week5.embedding_utils")

# Type alias used throughout this module.
Vector = list[float]


# ============================================================
# SINGLE-PAIR SIMILARITY
# ============================================================

def cosine_similarity(vec1: Vector, vec2: Vector) -> float:
    """Compute the cosine similarity between two embedding vectors.

    Cosine similarity measures the angle between two vectors,
    returning 1.0 for identical direction, 0.0 for orthogonal,
    and -1.0 for opposite.  It is length-invariant, which makes
    it ideal for comparing text embeddings.

    Parameters
    ----------
    vec1, vec2:
        Flat lists of floats of equal length.

    Returns
    -------
    float
        Similarity in the range [-1.0, 1.0].
        Returns 0.0 for zero vectors or mismatched dimensions.

    Example
    -------
    >>> a = [1.0, 0.0, 0.0]
    >>> b = [1.0, 0.0, 0.0]
    >>> cosine_similarity(a, b)
    1.0
    >>> cosine_similarity(a, [0.0, 1.0, 0.0])
    0.0
    """
    if not vec1 or not vec2:
        log.warning("cosine_similarity received an empty vector — returning 0.0.")
        return 0.0

    if len(vec1) != len(vec2):
        log.warning(
            "cosine_similarity: dimension mismatch (%d vs %d) — returning 0.0.",
            len(vec1), len(vec2),
        )
        return 0.0

    dot    = sum(a * b for a, b in zip(vec1, vec2))
    norm1  = math.sqrt(sum(a * a for a in vec1))
    norm2  = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0.0 or norm2 == 0.0:
        log.warning("cosine_similarity: zero-magnitude vector — returning 0.0.")
        return 0.0

    # Clamp to [-1, 1] to guard against floating-point drift.
    return max(-1.0, min(1.0, dot / (norm1 * norm2)))


def euclidean_distance(vec1: Vector, vec2: Vector) -> float:
    """Compute the Euclidean (L2) distance between two vectors.

    Smaller values indicate more similar vectors.

    Parameters
    ----------
    vec1, vec2:
        Flat lists of floats of equal length.

    Returns
    -------
    float
        Non-negative distance.  Returns float('inf') on dimension
        mismatch or empty input.
    """
    if not vec1 or not vec2:
        log.warning("euclidean_distance received an empty vector — returning inf.")
        return float("inf")

    if len(vec1) != len(vec2):
        log.warning(
            "euclidean_distance: dimension mismatch (%d vs %d) — returning inf.",
            len(vec1), len(vec2),
        )
        return float("inf")

    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


def dot_product(vec1: Vector, vec2: Vector) -> float:
    """Compute the dot product of two equal-length vectors.

    Parameters
    ----------
    vec1, vec2:
        Flat lists of floats of equal length.

    Returns
    -------
    float
        Dot product, or 0.0 on dimension mismatch / empty input.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    return sum(a * b for a, b in zip(vec1, vec2))


# ============================================================
# NORMALISATION
# ============================================================

def normalize_vector(vec: Vector) -> Vector:
    """Return a unit-length copy of ``vec`` (L2 normalisation).

    Normalising before dot-product search is equivalent to cosine
    similarity and is the standard prep step for ChromaDB ingestion.

    Parameters
    ----------
    vec:
        Flat list of floats.

    Returns
    -------
    list[float]
        Unit vector, or the original vector if its norm is zero.
    """
    if not vec:
        return vec

    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec  # zero vector — return as-is to avoid division by zero

    return [x / norm for x in vec]


# ============================================================
# BATCH SIMILARITY
# ============================================================

def top_k_similar(
    query:      Vector,
    candidates: list[Vector],
    k:          int = 5,
) -> list[tuple[int, float]]:
    """Find the top-k most similar vectors to a query.

    Parameters
    ----------
    query:
        The reference embedding vector.
    candidates:
        List of embedding vectors to compare against.
    k:
        Number of results to return.

    Returns
    -------
    list[tuple[int, float]]
        Up to k (index, similarity) pairs sorted by similarity descending.
        Indices refer to positions in ``candidates``.

    Example
    -------
    >>> q  = [1.0, 0.0]
    >>> cs = [[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]]
    >>> top_k_similar(q, cs, k=2)
    [(0, 1.0), (2, 0.7071...)]
    """
    if not query or not candidates:
        return []

    scored = [
        (i, cosine_similarity(query, c))
        for i, c in enumerate(candidates)
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


def pairwise_similarity_matrix(vectors: list[Vector]) -> list[list[float]]:
    """Compute an N×N cosine similarity matrix for a list of vectors.

    Useful for visualising how a set of concepts relate to each other —
    for example, comparing all of a student's recent topics at once.

    Parameters
    ----------
    vectors:
        List of embedding vectors.  All must have the same dimension.

    Returns
    -------
    list[list[float]]
        Square matrix where ``matrix[i][j]`` is the cosine similarity
        between ``vectors[i]`` and ``vectors[j]``.
    """
    n = len(vectors)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i, n):
            sim = cosine_similarity(vectors[i], vectors[j])
            matrix[i][j] = sim
            matrix[j][i] = sim     # symmetric

    return matrix


def average_vector(vectors: list[Vector]) -> Vector:
    """Compute the element-wise mean of a list of vectors.

    Useful for creating a single "concept centroid" from multiple
    embeddings — e.g. averaging all error embeddings for a topic
    to produce a representative query vector for RAG retrieval.

    Parameters
    ----------
    vectors:
        Non-empty list of equal-length float lists.

    Returns
    -------
    list[float]
        Mean vector, or ``[]`` if ``vectors`` is empty.
    """
    if not vectors:
        log.warning("average_vector received an empty list — returning [].")
        return []

    dim = len(vectors[0])
    total = [0.0] * dim

    for vec in vectors:
        if len(vec) != dim:
            log.warning(
                "average_vector: skipping vector with wrong dimension (%d vs %d).",
                len(vec), dim,
            )
            continue
        for i, v in enumerate(vec):
            total[i] += v

    n = len(vectors)
    return [x / n for x in total]