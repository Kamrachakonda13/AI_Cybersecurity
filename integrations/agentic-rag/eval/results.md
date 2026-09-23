# Phase 1 Evaluation Results

**Date:** 2026-09-15
**Corpus:** 5 documents, 16 chunks
**Embedding model:** all-MiniLM-L6-v2 (384 dims)
**Vector store:** pgvector with HNSW (m=16, ef_construction=64)
**Chunking:** 400-char paragraph-level, 50-char overlap
**top_k:** 5

## Metrics

| Metric | Value |
|--------|-------|
| Questions | 12 |
| Hit Rate @ 1 | 83.33% |
| Hit Rate @ 3 | 91.67% |
| Hit Rate @ 5 | 100.00% |
| MRR | 0.892 |

## Observations

- Retrieval is reliable for direct questions whose wording closely matches source text.
- All questions hit within top-3, indicating the embedding space separates these documents cleanly.
- One question missed Hit@1 despite hitting Hit@3 — the correct chunk was ranked second or third.
- Entity-heavy queries (acronyms, proper nouns) may underperform without keyword search.
- No reranking is applied — top-5 ordering comes from cosine similarity alone.

## Design Decisions

- **Chunking:** 400-char paragraph-level with 50-char overlap. Alternatives considered: sentence-level (too small, loses context) and document-level (too large, dilutes embedding signal).
- **Embedding:** all-MiniLM-L6-v2 (384-dim, local, zero cost). Alternatives considered: OpenAI text-embedding-3-small (higher quality, but adds API dependency and cost for a baseline).
- **Vector store:** pgvector with HNSW index. Alternatives considered: FAISS (faster but no persistence or SQL filtering).

## Limitations (Requirements for Phase 2)

1. No keyword search — entity-heavy queries may underperform.
2. No reranking — cosine similarity ordering only.
3. No access control — any caller sees all chunks.
4. No confidence thresholding — the LLM will attempt an answer even when retrieval is weak.

These become the explicit requirements for Phase 2 (Hybrid RAG with RBAC).