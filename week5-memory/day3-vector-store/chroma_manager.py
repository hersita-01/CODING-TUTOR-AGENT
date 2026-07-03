# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ chroma_manager.py
#
# ChromaManager is the single interface for all ChromaDB operations.
#
# Responsibilities:
#   + Create / open ChromaDB collections
#   + Insert documents with embeddings and metadata
#   + Query by embedding vector
#   + Delete / reset collections
#   + Metadata filtering support
#
# NOT responsible for:
#   - Generating embeddings  -> EmbeddingManager (Day 2)
#   - Chunking text          -> DocumentChunker  (Day 3)
#   - Reading files          -> DocumentIndexer  (Day 3)
# -----------------------------------

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import chromadb

log = logging.getLogger("week5.chroma_manager")

DEFAULT_COLLECTION = "python_tutor"
DEFAULT_PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_store"
DEFAULT_TOP_K = 5

class ChromaManager:
    """Single interface for all ChromaDB collection operations.

    Parameters
    ----------
    persist_dir:
        Directory where ChromaDB persists data to disk.
        Defaults to ``week5-memory/chroma_store/``.
    collection_name:
        Name of the ChromaDB collection. Defaults to ``python_tutor``.
    """

    def __init__(
        self,
        persist_dir:     Optional[Path] = None,
        collection_name: str            = DEFAULT_COLLECTION,
    ) -> None:
        self._persist_dir     = Path(persist_dir or DEFAULT_PERSIST_DIR)
        self._collection_name = collection_name
        self._persist_dir.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(self._persist_dir))
        log.debug("ChromaManager initialised. store=%s  collection=%s",
                  self._persist_dir, collection_name)

        # cosine distance matches EmbeddingManager similarity metric.
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        log.debug("Collection '%s' ready. Documents: %d.",
                  self._collection_name, self._collection.count())

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def collection_name(self) -> str:
        return self._collection_name

    @property
    def persist_dir(self) -> Path:
        return self._persist_dir

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add_documents(
        self,
        ids:        list[str],
        embeddings: list[list[float]],
        documents:  list[str],
        metadatas:  Optional[list[dict[str, Any]]] = None,
    ) -> int:
        """Insert or update documents in the collection.

        Uses upsert semantics — existing documents are updated in place.
        Duplicate IDs within a single call are rejected.

        Parameters
        ----------
        ids:        Unique string IDs, one per document.
        embeddings: Pre-computed vectors from EmbeddingManager.
        documents:  Raw text strings.
        metadatas:  Optional list of metadata dicts.

        Returns
        -------
        int  Number of documents upserted, 0 on failure.
        """
        if not ids:
            log.warning("add_documents called with empty ids list.")
            return 0

        if len(ids) != len(embeddings) or len(ids) != len(documents):
            raise ValueError(
                f"ids ({len(ids)}), embeddings ({len(embeddings)}), "
                f"documents ({len(documents)}) must have equal length."
            )

        if metadatas is None:
            metadatas = [{} for _ in ids]

        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate document IDs detected.")

        # Validate embeddings: no empty vectors, all same dimension.
        for emb in embeddings:
            if not emb:
                raise ValueError("add_documents: embeddings must not be empty vectors.")
        dims = {len(e) for e in embeddings}
        if len(dims) > 1:
            raise ValueError(
                f"add_documents: inconsistent embedding dimensions {dims}. "
                "All embeddings must have the same dimension."
            )

        clean_meta = [_sanitise_metadata(m) for m in metadatas]

        try:
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=clean_meta,
            )
            log.info("Upserted %d documents into '%s'.", len(ids), self._collection_name)
            return len(ids)
        except Exception as exc:
            log.error("add_documents failed: %s", exc)
            return 0

    def is_empty(self) -> bool:
        """Return True if the collection has no documents."""
        return self.document_count() == 0
    
    def collection_info(self) -> dict[str, Any]:
        """Return basic information about the collection."""
        return {
            "collection": self.collection_name,
            "persist_dir": str(self.persist_dir),
            "documents": self.document_count(),
        }
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a single document by ID. Returns True on success."""
        try:
            self._collection.delete(ids=[doc_id])
            log.debug("Deleted document '%s'.", doc_id)
            return True
        except Exception as exc:
            log.error("delete_document('%s') failed: %s", doc_id, exc)
            return False

    def reset_collection(self) -> None:
        """Remove all documents from the collection (keeps collection itself)."""
        try:
            self._client.delete_collection(self._collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            log.info("Collection '%s' reset.", self._collection_name)
        except Exception as exc:
            log.error("reset_collection failed: %s", exc)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def query(
        self,
        query_embedding: list[float],
        top_k:           int = DEFAULT_TOP_K,
        where:           Optional[dict[str, Any]]  = None,
    ) -> dict[str, Any]:
        """Return the top-k most similar documents to a query vector.

        Parameters
        ----------
        query_embedding: Vector from EmbeddingManager.embed_text().
        top_k:           Number of results to return.
        where:           Optional ChromaDB metadata filter.

        Returns
        -------
        dict with keys: ids, documents, metadatas, distances
        """
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if not query_embedding:
            log.warning("query called with empty embedding.")
            return _empty_result()

        count = self._collection.count()
        if count == 0:
            log.warning("Collection '%s' is empty.", self._collection_name)
            return _empty_result()

        effective_k = max(1, min(top_k, count))
        try:
            kwargs: dict[str, Any] = {
                "query_embeddings": [query_embedding],
                "n_results":        effective_k,
                "include":          ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where

            raw = self._collection.query(**kwargs)
            return {
                "ids":       raw["ids"][0]       if raw["ids"]       else [],
                "documents": raw["documents"][0] if raw["documents"] else [],
                "metadatas": raw["metadatas"][0] if raw["metadatas"] else [],
                "distances": raw["distances"][0] if raw["distances"] else [],
            }
        except Exception as exc:
            log.exception("query failed")
            return _empty_result()

    def document_count(self) -> int:
        """Return total number of documents in the collection."""
        try:
            return int(self._collection.count())
        except Exception as exc:
            log.error("document_count failed: %s", exc)
            return 0

    def get_document(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Fetch a single document by ID. Returns None if not found."""
        try:
            result = self._collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"],
            )
            if result["ids"]:
                return {
                    "id":       result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
            return None
        except Exception as exc:
            log.error("get_document('%s') failed: %s", doc_id, exc)
            return None

    def list_sources(self) -> list[str]:
        """Return alphabetically sorted unique source filenames in the collection.

        Safely handles None or missing metadata entries.
        """
        try:
            result = self._collection.get(include=["metadatas"])
            sources: set[str] = set()
            for m in (result.get("metadatas") or []):
                if m is None:
                    continue
                src = str(m.get("source", "")).strip()
                if src:
                    sources.add(src)
            return sorted(sources)
        except Exception as exc:
            log.error("list_sources failed: %s", exc)
            return []


# ============================================================
# PRIVATE HELPERS
# ============================================================

def _sanitise_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """Cast metadata values to types ChromaDB accepts (str/int/float/bool).

    Conversion rules (in priority order):
      - Primitives (str/int/float/bool) → kept as-is
      - None                            → empty string ""
      - list / tuple                    → comma-separated string
      - pathlib.Path                    → str(path)
      - everything else                 → str(value)
    """
    allowed = (str, int, float, bool)
    result: dict[str, Any] = {}
    for k, v in meta.items():
        if isinstance(v, allowed):
            result[k] = v
        elif v is None:
            result[k] = ""
        elif isinstance(v, (list, tuple)):
            result[k] = ", ".join(str(item) for item in v)
        elif isinstance(v, Path):
            result[k] = str(v)
        else:
            result[k] = str(v)
    return result


def _empty_result() -> dict[str, Any]:
    """Return an empty result dict matching the query() schema."""
    return {"ids": [], "documents": [], "metadatas": [], "distances": []}