# -----------------------------------
# WEEK 5 – DAY 3: VECTOR STORE
# week5-memory/day3-vector-store/ document_indexer.py
#
# DocumentIndexer orchestrates the full ingestion pipeline:
#
#   Read .txt files
#       -> DocumentChunker  (split into chunks)
#       -> EmbeddingManager (Day 2, embed each chunk)
#       -> ChromaManager    (store in ChromaDB)
#
# This module does NOT perform retrieval.
# -----------------------------------

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

log = logging.getLogger("week5.document_indexer")

# ── Path setup ────────────────────────────────────────────────────────
_here  = Path(__file__).resolve().parent          # day3-vector-store/
_day2  = _here.parent / "day2-embeddings"
_week5 = _here.parent

for _p in [str(_here), str(_day2), str(_week5)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chroma_manager    import ChromaManager
from document_chunker  import DocumentChunker, Chunk
from embedding_manager import EmbeddingManager


# ============================================================
# RESULT DATACLASS
# ============================================================

@dataclass
class IndexResult:
    """Summary of a completed indexing run.

    Attributes
    ----------
    files_indexed:      Number of .txt files processed.
    chunks_created:     Total chunks produced by the chunker.
    embeddings_generated: Chunks successfully embedded.
    documents_stored:   Chunks successfully stored in ChromaDB.
    skipped:            Chunks skipped due to empty embedding.
    errors:             List of error messages encountered.
    """
    files_indexed:         int
    chunks_created:        int
    embeddings_generated:  int
    documents_stored:      int
    skipped:               int
    errors:                list[str]

    def summary(self) -> str:
        lines = [
            f"Files indexed:          {self.files_indexed}",
            f"Chunks created:         {self.chunks_created}",
            f"Embeddings generated:   {self.embeddings_generated}",
            f"Documents stored:       {self.documents_stored}",
            f"Skipped (empty embed):  {self.skipped}",
        ]
        if self.errors:
            lines.append(f"Errors:                 {len(self.errors)}")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)


# ============================================================
# DOCUMENT INDEXER
# ============================================================

class DocumentIndexer:
    """Reads tutorial files, chunks, embeds, and stores them in ChromaDB.

    Parameters
    ----------
    chroma_manager:
        ChromaManager instance to write into.
    embedding_manager:
        EmbeddingManager instance (Day 2) for producing vectors.
    chunker:
        DocumentChunker instance. Defaults to section-based chunking.
        Supports strategies: "section", "sentence", "fixed", "auto".
    batch_size:
        Number of chunks to embed and store per ChromaDB upsert call.

    Example
    -------
    >>> indexer = DocumentIndexer()
    >>> result  = indexer.index_directory(Path("python_docs/"))
    >>> print(result.summary())
    """

    def __init__(
        self,
        chroma_manager:    Optional[ChromaManager]    = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        chunker:           Optional[DocumentChunker]  = None,
        batch_size:        int                        = 32,
    ) -> None:
        self._chroma    = chroma_manager    if chroma_manager    is not None else ChromaManager()
        self._embedder  = embedding_manager if embedding_manager is not None else EmbeddingManager()
        self._chunker   = chunker           if chunker           is not None else DocumentChunker()
        self._batch_size = batch_size

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def index_directory(
        self,
        docs_dir:    Path,
        reset_first: bool = False,
    ) -> IndexResult:
        """Index all .txt files in a directory.

        Parameters
        ----------
        docs_dir:
            Directory containing .txt tutorial files.
        reset_first:
            If True, clears the ChromaDB collection before indexing.
            Useful for a clean re-index.

        Returns
        -------
        IndexResult  Summary of the operation.
        """
        docs_dir = Path(docs_dir)
        if not docs_dir.is_dir():
            log.error("index_directory: '%s' is not a directory.", docs_dir)
            return IndexResult(0, 0, 0, 0, 0, [f"Not a directory: {docs_dir}"])

        # Exclude hidden files (names starting with '.') such as .notes.txt.
        txt_files = sorted(
            p for p in docs_dir.glob("*.txt") if not p.name.startswith(".")
        )
        if not txt_files:
            log.warning("index_directory: no .txt files found in '%s'.", docs_dir)
            return IndexResult(0, 0, 0, 0, 0, [f"No .txt files in {docs_dir}"])

        if reset_first:
            log.info("Resetting collection before indexing.")
            self._chroma.reset_collection()

        return self.index_files(txt_files)

    def index_files(self, paths: list[Path]) -> IndexResult:
        """Index a specific list of .txt files.

        Parameters
        ----------
        paths:
            List of file paths to index.

        Returns
        -------
        IndexResult  Summary of the operation.
        """
        all_chunks: list[Chunk] = []
        errors: list[str]       = []

        # ── Step 1: chunk all files ───────────────────────────────────
        for path in paths:
            try:
                chunks = self._chunker.chunk_file(path)
                if chunks:
                    all_chunks.extend(chunks)
                    log.info("'%s' → %d chunks.", path.name, len(chunks))
                else:
                    log.warning("'%s' produced no chunks.", path.name)
            except Exception as exc:
                msg = f"Chunking failed for '{path.name}': {exc}"
                log.error(msg)
                errors.append(msg)

        chunks_created = len(all_chunks)

        if not all_chunks:
            return IndexResult(
                files_indexed        = len(paths),
                chunks_created       = 0,
                embeddings_generated = 0,
                documents_stored     = 0,
                skipped              = 0,
                errors               = errors,
            )

        # ── Step 2 & 3: embed + store in batches ─────────────────────
        total_stored  = 0
        total_skipped = 0
        total_embedded = 0

        for batch_start in range(0, len(all_chunks), self._batch_size):
            batch = all_chunks[batch_start:batch_start + self._batch_size]

            texts = [c.text for c in batch]

            try:
                vectors = self._embedder.embed_batch(texts)
            except Exception as exc:
                msg = f"Embedding batch {batch_start}–{batch_start+len(batch)} failed: {exc}"
                log.error(msg)
                errors.append(msg)
                continue

            # Filter out chunks whose embedding came back empty.
            ids        : list[str]             = []
            embeds     : list[list[float]]     = []
            docs       : list[str]             = []
            metas      : list[dict[str, str]]  = []

            for chunk, vec in zip(batch, vectors):
                if not vec or all(v == 0.0 for v in vec):
                    log.warning("Empty embedding for chunk '%s' — skipping.", chunk.chunk_id)
                    total_skipped += 1
                    continue
                ids.append(chunk.chunk_id)
                embeds.append(vec)
                docs.append(chunk.text)
                metas.append(chunk.to_metadata())
                total_embedded += 1

            if ids:
                stored = self._chroma.add_documents(
                    ids=ids, embeddings=embeds, documents=docs, metadatas=metas
                )
                total_stored += stored

        return IndexResult(
            files_indexed        = len(paths),
            chunks_created       = chunks_created,
            embeddings_generated = total_embedded,
            documents_stored     = total_stored,
            skipped              = total_skipped,
            errors               = errors,
        )

    def index_text(
        self,
        text:   str,
        source: str = "inline",
    ) -> IndexResult:
        """Index a raw text string directly (no file required).

        Useful for testing or indexing dynamically generated content.

        Parameters
        ----------
        text:   The document text to chunk, embed, and store.
        source: Label used in metadata as the source.
        """
        chunks = self._chunker.chunk_text(text, source=source)
        if not chunks:
            return IndexResult(1, 0, 0, 0, 0, ["No chunks produced from text."])

        # Mirror the embed-and-store logic from index_files().
        total_stored   = 0
        total_skipped  = 0
        total_embedded = 0
        errors: list[str] = []

        for batch_start in range(0, len(chunks), self._batch_size):
            batch   = chunks[batch_start:batch_start + self._batch_size]
            texts   = [c.text for c in batch]

            try:
                vectors = self._embedder.embed_batch(texts)
            except Exception as exc:
                msg = f"Embedding batch failed: {exc}"
                log.error(msg)
                errors.append(msg)
                continue

            ids:    list[str]            = []
            embeds: list[list[float]]    = []
            docs:   list[str]            = []
            metas:  list[dict[str, str]] = []

            for chunk, vec in zip(batch, vectors):
                if not vec or all(v == 0.0 for v in vec):
                    log.warning("Empty embedding for chunk '%s' — skipping.", chunk.chunk_id)
                    total_skipped += 1
                    continue
                ids.append(chunk.chunk_id)
                embeds.append(vec)
                docs.append(chunk.text)
                metas.append(chunk.to_metadata())
                total_embedded += 1

            if ids:
                stored = self._chroma.add_documents(
                    ids=ids, embeddings=embeds, documents=docs, metadatas=metas
                )
                total_stored += stored

        return IndexResult(
            files_indexed        = 1,
            chunks_created       = len(chunks),
            embeddings_generated = total_embedded,
            documents_stored     = total_stored,
            skipped              = total_skipped,
            errors               = errors,
        )

    def is_indexed(self, source_filename: str) -> bool:
        """Check whether a source file has already been indexed.

        Parameters
        ----------
        source_filename:
            The basename of the file (e.g. ``loops.txt``).

        Returns
        -------
        bool  True if at least one chunk from this source exists.
        """
        sources = self._chroma.list_sources()
        return source_filename in sources