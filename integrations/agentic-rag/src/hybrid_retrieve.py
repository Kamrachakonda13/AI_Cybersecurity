import os

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from src.bm25_index import get_index

load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")

CLEARANCE_RANK = {
    "PUBLIC": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4,
}

RRF_K = 60

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def vector_search(query: str, user_clearance: str, tenant_id: str, top_k: int = 20):
    """Vector search with clearance and tenant filters enforced in SQL."""
    query_vec = get_model().encode(
        [query], normalize_embeddings=True)[0].tolist()
    max_rank = CLEARANCE_RANK[user_clearance]

    allowed_levels = [lvl for lvl,
                      rank in CLEARANCE_RANK.items() if rank <= max_rank]

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, source_file, content, clearance_level,
               1 - (embedding <=> %s::vector) AS score
        FROM chunks
        WHERE clearance_level = ANY(%s)
          AND tenant_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (query_vec, allowed_levels, tenant_id, query_vec, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "source_file": r[1],
            "content": r[2],
            "clearance_level": r[3],
            "score": float(r[4]),
        }
        for r in rows
    ]


def bm25_search(query: str, user_clearance: str, tenant_id: str, top_k: int = 20):
    """BM25 search with clearance and tenant filters applied to the results."""
    max_rank = CLEARANCE_RANK[user_clearance]
    results = get_index().search(query, top_k=top_k * 3)

    filtered = []
    for r in results:
        chunk = r["chunk"]
        if chunk["tenant_id"] != tenant_id:
            continue
        if CLEARANCE_RANK[chunk["clearance_level"]] > max_rank:
            continue
        filtered.append({
            "id": chunk["id"],
            "source_file": chunk["source_file"],
            "content": chunk["content"],
            "clearance_level": chunk["clearance_level"],
            "score": r["score"],
        })
        if len(filtered) >= top_k:
            break

    return filtered


def reciprocal_rank_fusion(result_lists, k: int = RRF_K):
    """Merge ranked lists via RRF: score(doc) = sum over lists of 1/(k + rank)."""
    scores = {}
    for results in result_lists:
        for rank, item in enumerate(results, start=1):
            doc_id = item["id"]
            if doc_id not in scores:
                scores[doc_id] = {"item": item, "score": 0.0}
            scores[doc_id]["score"] += 1.0 / (k + rank)

    fused = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return [{**entry["item"], "rrf_score": entry["score"]} for entry in fused]


def hybrid_retrieve(query: str, user_clearance: str, tenant_id: str, top_k: int = 20):
    """Vector + BM25 in parallel, fused via RRF."""
    vec_results = vector_search(query, user_clearance, tenant_id, top_k=top_k)
    bm25_results = bm25_search(query, user_clearance, tenant_id, top_k=top_k)
    fused = reciprocal_rank_fusion([vec_results, bm25_results])
    return fused[:top_k]


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "What is the retry policy?"
    results = hybrid_retrieve(
        q, user_clearance="INTERNAL", tenant_id="acme", top_k=5)
    for r in results:
        print(
            f"[{r['rrf_score']:.4f}] {r['id']} ({r['clearance_level']}): {r['content'][:70]}")
