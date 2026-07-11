# Week 5 – Day 3: ChromaDB Vector Store

Local semantic search over Python tutorial documents.  
Sits between Day 2 Embeddings and Day 5 RAG in the memory stack.

---

## Architecture

```
python_docs/*.txt
      ↓
DocumentChunker       split into sections
      ↓
EmbeddingManager      Day 2 — 384-d vectors
      ↓
ChromaManager         persist in ChromaDB
      ↓
rag_search()          semantic retrieval
      ↓
RAG Pipeline          Day 5
```

---

## Files

| File | Responsibility |
|---|---|
| `chroma_manager.py` | All ChromaDB read/write operations |
| `document_chunker.py` | Split text into chunks with metadata |
| `document_indexer.py` | Orchestrate chunk → embed → store pipeline |
| `rag_search_tool.py` | Public `rag_search()` API |
| `ingest_documents.py` | CLI to index python_docs/ |
| `test_chroma.py` | Full test suite |
| `python_docs/` | Tutorial corpus |

---

## Install

```bash
pip install chromadb sentence-transformers
```

---

## Usage

### 1. Index documents

```bash
cd week5-memory/day3-vector-store
python ingest_documents.py
```

Add `--reset` to clear and re-index from scratch:

```bash
python ingest_documents.py --reset
```

### 2. Search

```python
from rag_search_tool import rag_search

result = rag_search("how do for loops work?", top_k=3)
for chunk in result["chunks"]:
    print(chunk["source"], chunk["similarity"])
    print(chunk["text"][:200])
```

### 3. Run tests

```bash
python test_chroma.py
```

---

## Chunking Strategies

| Strategy | How it splits | Best for |
|---|---|---|
| `section` (default) | On `##` headings | Tutorial documents with sections |
| `sentence` | On `.!?` boundaries, grouped 5 per chunk | Prose text |
| `fixed` | Fixed character count with overlap | Arbitrary text |

---

## Data Storage

ChromaDB data is persisted at:
```
week5-memory/chroma_store/
```

Shared across Day 3, 4, and 5 — do not delete between days.

---

## Connection to Other Days

| Day | Connection |
|---|---|
| Day 1 | `LearnerProfile.get_summary()` can be embedded and stored |
| Day 2 | `EmbeddingManager` is imported directly — no duplication |
| Day 4 | Chunking strategies extended for larger documents |
| Day 5 | `rag_search()` plugged into `tool_dispatcher` |