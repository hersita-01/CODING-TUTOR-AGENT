# Week 5 – Day 2: Embeddings

Converts text into vector embeddings using `sentence-transformers`.  
This is the second layer of the Week 5 memory stack — sitting between the learner profile (Day 1) and ChromaDB (Day 3).

---

## What Are Embeddings?

An embedding is a fixed-length list of numbers (a vector) that represents the *meaning* of a piece of text.

Two sentences that mean similar things will have vectors that point in similar directions — measured by **cosine similarity** (1.0 = identical meaning, 0.0 = unrelated, -1.0 = opposite).

```
"How do I use a for loop?"       → [0.12, -0.34, 0.87, ...]  ← 384 numbers
"Iterate over a list with for."  → [0.11, -0.31, 0.85, ...]  ← very similar
"ZeroDivisionError occurred."    → [0.55,  0.02, -0.21, ...] ← different
```

This is what allows the tutor to find *conceptually related* past errors, topics, and explanations — not just keyword matches.

---

## Why Embeddings Are Required

| Without embeddings | With embeddings |
|---|---|
| Can only match exact keywords | Understands meaning — "loop" matches "iterate", "for", "while" |
| No way to rank relevance | Can score and sort by semantic closeness |
| ChromaDB (Day 3) cannot ingest text directly | ChromaDB stores and searches vectors |
| RAG (Day 5) cannot retrieve relevant past context | RAG finds the most relevant past errors for the current question |

---

## Model

| Property | Value |
|---|---|
| Library | `sentence-transformers` |
| Model | `all-MiniLM-L6-v2` |
| Dimension | 384 |
| Runs on | CPU (no GPU required) |
| Speed | ~2 000 sentences/sec on CPU |
| Size | ~80 MB download, cached locally |

The model is loaded **once** at `EmbeddingManager` construction and reused for all subsequent calls.

---

## Installation

```bash
pip install sentence-transformers
```

The model downloads automatically on first use (~80 MB, cached in `~/.cache/huggingface/`).

---

## File Structure

```
week5-memory/
└── day2-embeddings/
    ├── embedding_manager.py    ← EmbeddingManager class (model + embed calls)
    ├── embedding_utils.py      ← Pure vector math utilities (no model loading)
    ├── test_embeddings.py      ← Test suite (live or mock mode)
    └── README.md               ← this file
```

---

## Quick Start

```python
from embedding_manager import EmbeddingManager

mgr = EmbeddingManager()

# Single text
vec = mgr.embed_text("What is a for loop?")
print(len(vec))   # 384

# Batch (faster than calling embed_text in a loop)
vecs = mgr.embed_batch(["lists", "dictionaries", "sets"])
print(len(vecs))  # 3

# Dimension
print(mgr.embedding_dimension())  # 384
```

```python
from embedding_utils import cosine_similarity, top_k_similar

sim = cosine_similarity(vec_a, vec_b)  # 0.0 – 1.0

# Find the 3 most similar past errors to a new one
results = top_k_similar(query_vec, past_error_vecs, k=3)
# [(index, score), ...]
```

---

## Integration Map

### Day 1 → Day 2 (current)

```python
from memory_manager   import MemoryManager
from embedding_manager import EmbeddingManager

mgr     = MemoryManager()
emb     = EmbeddingManager()

profile = mgr.get_or_create("alice")
summary = profile.get_summary()
vector  = emb.embed_text(summary)   # summary → 384-d vector
```

### Day 2 → Day 3 (ChromaDB)

```python
# Day 3 will store vectors in ChromaDB.
collection.add(
    ids        = ["alice_summary"],
    embeddings = [vector],
    documents  = [summary],
)
```

`EmbeddingManager` produces the vectors; ChromaDB stores and indexes them.  
`EmbeddingManager` does **not** change between Day 2 and Day 3.

### Day 2 → Day 5 (RAG)

```python
# Day 5 will query ChromaDB with an embedding to retrieve context.
query_vec = emb.embed_text(student_question)
results   = collection.query(query_embeddings=[query_vec], n_results=3)
# → inject retrieved context into system prompt
```

`EmbeddingManager.embed_text()` is the same call in Day 5 as it is today.

---

## API Reference

### `EmbeddingManager`

| Method | Returns | Description |
|---|---|---|
| `embed_text(text)` | `list[float]` | Embed one string; `[]` on empty input |
| `embed_batch(texts)` | `list[list[float]]` | Embed many strings in one pass |
| `embedding_dimension()` | `int` | Vector length (384) |
| `model_name()` | `str` | Model identifier string |
| `is_loaded()` | `bool` | True after first embed call |

### `embedding_utils`

| Function | Description |
|---|---|
| `cosine_similarity(v1, v2)` | Cosine similarity [-1, 1] |
| `euclidean_distance(v1, v2)` | L2 distance |
| `dot_product(v1, v2)` | Raw dot product |
| `normalize_vector(v)` | Return unit-length copy |
| `top_k_similar(query, candidates, k)` | Top-k (index, score) pairs |
| `pairwise_similarity_matrix(vectors)` | N×N similarity matrix |
| `average_vector(vectors)` | Element-wise mean |

---

## Running the Tests

```bash
cd week5-memory/day2-embeddings
python test_embeddings.py
```

The test suite runs in **LIVE mode** when `sentence-transformers` is installed and the model is reachable, and falls back to **MOCK mode** (synthetic deterministic vectors) otherwise.  All 13 structural tests pass in both modes.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ImportError: sentence-transformers` | `pip install sentence-transformers` |
| Slow first run | Model downloading (~80 MB) — subsequent runs use the cache |
| `OSError: can't load model` | Check internet connection; model caches after first download |
| Tests run in MOCK mode | Expected offline — all structural tests still pass |