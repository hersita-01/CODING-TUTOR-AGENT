# -----------------------------------
# WEEK 5 – DAY 2: EMBEDDINGS
# week5-memory/day2-embeddings/ embedding_manager.py
#
# EmbeddingManager is the single interface for converting text
# into vector embeddings throughout the tutoring system.
#
# Architecture position:
#
#   Memory Manager (Day 1)
#       ↓
#   EmbeddingManager          ← this file
#       ↓
#   ChromaDB (Day 3)
#       ↓
#   RAG Retriever (Day 5)
#
# Design principles:
#   • Model is loaded ONCE at construction and reused — no repeated
#     disk/network I/O on every embed call.
#   • Returns plain Python lists (not numpy arrays) so callers have
#     no numpy dependency and ChromaDB can ingest them directly.
#   • Fails gracefully on empty / invalid input — never raises on
#     bad text; returns an empty list and logs a warning instead.
#   • No retrieval, no storage, no ChromaDB — embedding only.
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

log = logging.getLogger("week5.embedding_manager")


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_MODEL       = "all-MiniLM-L6-v2"
DEFAULT_BATCH_SIZE  = 64
# 384-dimensional embeddings; fast, accurate for semantic similarity.
# Chosen because it is small enough to run on CPU without a GPU.


# ============================================================
# EMBEDDING MANAGER
# ============================================================

class EmbeddingManager:
    """Loads a sentence-transformer model and produces text embeddings.

    The model is loaded once on first use (lazy initialisation) and
    then reused for all subsequent calls, so there is no per-call
    overhead from model loading.

    Parameters
    ----------
    model_name:
        HuggingFace model identifier.  Defaults to ``all-MiniLM-L6-v2``.
    batch_size:
        Number of texts to encode per model forward pass.
        Defaults to ``DEFAULT_BATCH_SIZE`` (64).

    Example
    -------
    >>> mgr = EmbeddingManager()
    >>> vec = mgr.embed_text("What is a for loop?")
    >>> len(vec)
    384
    >>> batch = mgr.embed_batch(["lists", "dictionaries", "sets"])
    >>> len(batch)
    3
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self._model_name: str = model_name
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0.")
        self._batch_size: int = batch_size
        self._model = None          # lazy-loaded on first embed call
        self._dim:   Optional[int] = None
        log.debug("EmbeddingManager created (model=%s, batch_size=%d, not yet loaded).",
                  model_name, batch_size)

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        """Load the sentence-transformer model (called once on first use)."""
        if self._model is not None:
            return  # already loaded

        try:
            from sentence_transformers import SentenceTransformer
            log.info("Loading embedding model '%s' …", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            # Cache the dimension from a probe embedding.
            probe = self._model.encode("probe", convert_to_numpy=True, normalize_embeddings=True)
            self._dim = int(probe.shape[0])
            log.info(
                "Embedding model loaded. Dimension: %d.", self._dim
            )
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model '{self._model_name}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string and return it as a flat list of floats.

        Parameters
        ----------
        text:
            The string to embed.  Whitespace-only strings are treated
            as invalid and return an empty list.

        Returns
        -------
        list[float]
            A vector of length ``embedding_dimension()``, or ``[]`` on
            invalid input.
        """
        if not isinstance(text, str) or not text.strip():
            log.warning("embed_text received empty or non-string input — returning [].")
            return []

        self._load_model()

        try:
            vector: np.ndarray = self._model.encode(
                text.strip(),
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return vector.tolist()
        except Exception as exc:
            log.error("embed_text failed for input %r: %s", text[:60], exc)
            return []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of strings in a single model pass.

        Empty or whitespace-only strings within the batch are replaced
        with zero vectors so the output length always equals the input
        length — callers can safely zip inputs and outputs.

        Parameters
        ----------
        texts:
            List of strings to embed.

        Returns
        -------
        list[list[float]]
            A list of vectors, one per input string.  Empty / invalid
            strings produce a zero vector of the correct dimension.
        """
        if not texts:
            log.warning("embed_batch received an empty list — returning [].")
            return []

        self._load_model()

        # Separate valid texts from blanks; track original positions.
        valid_indices: list[int] = []
        valid_texts:   list[str] = []
        for i, t in enumerate(texts):
            if isinstance(t, str) and t.strip():
                valid_indices.append(i)
                valid_texts.append(t.strip())
            else:
                log.warning(
                    "embed_batch: item %d is empty or invalid — using zero vector.", i
                )

        # Initialise output with zero vectors for blanks.
        dim = self.embedding_dimension()
        results: list[list[float]] = [[0.0] * dim for _ in texts]

        if not valid_texts:
            return results

        try:
            vectors: np.ndarray = self._model.encode(
                valid_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=self._batch_size,
            )
            for out_idx, vec in zip(valid_indices, vectors):
                results[out_idx] = vec.tolist()
        except Exception as exc:
            log.error("embed_batch failed: %s", exc)

        return results

    def embedding_dimension(self) -> int:
        """Return the number of dimensions in each embedding vector.

        Triggers model loading on first call if the model has not
        been loaded yet.

        Returns
        -------
        int
            Vector length (384 for ``all-MiniLM-L6-v2``).
        """
        if self._dim is None:
            self._load_model()
        return self._dim  # type: ignore[return-value]

    def model_name(self) -> str:
        """Return the model identifier string."""
        return self._model_name

    def is_loaded(self) -> bool:
        """Return True if the model has been loaded into memory."""
        return self._model is not None

    def batch_size(self) -> int:
        """Return the configured embedding batch size."""
        return self._batch_size