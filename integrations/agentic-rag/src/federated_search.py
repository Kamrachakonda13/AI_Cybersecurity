"""
Federated search for Phase 6.

Queries the unified chunks table with:
  - Vector retrieval
  - Full ACL enforcement (clearance + tenant + owner_team + share_scope + acl)
  - Soft-delete filtering (deleted_at IS NULL)
  - Source-system attribution
  - Alternate source references from dedup
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder, SentenceTransformer

from src.acl import allowed_clearance_levels, build_acl_filter

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")

_model = None
_reranker = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def vector_search(query: str, user: dict, top_k: int = 20) -> list:
    query_vec = _get_model().encode([query], normalize_embeddings=True)[0].tolist()
    acl = build_acl_filter(user)

    sql = """
        SELECT
            id, content, source_file, clearance_level, tenant_id,
            source_system, alternate_sources, owner_team, share_scope,
            1 - (embedding <=> %s::vector) AS score
        FROM chunks
        WHERE deleted_at IS NULL
          AND clearance_level = ANY(%s)
          AND tenant_id = %s
          AND (
              owner_team = ANY(%s)
              OR share_scope = '"org"'::jsonb
              OR share_scope ?| %s::text[]
              OR acl @> %s::jsonb
          )
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    params = (
        query_vec,
        acl["allowed_levels"],
        acl["tenant_id"],
        acl["user_teams"],
        acl["user_teams"],
        json.dumps([acl["user_principal"]]),
        query_vec,
        top_k,
    )

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "content": r[1],
            "source_file": r[2],
            "clearance_level": r[3],
            "tenant_id": r[4],
            "source_system": r[5],
            "alternate_sources": r[6] or [],
            "owner_team": r[7],
            "share_scope": r[8],
            "score": float(r[9]),
        }
        for r in rows
    ]


def rerank(query: str, candidates: list, top_k: int = 5) -> list:
    if not candidates:
        return []
    model = _get_reranker()
    pairs = [(query, c["content"]) for c in candidates]
    scores = model.predict(pairs)
    scored = sorted(zip(candidates, scores), key=lambda x: float(x[1]), reverse=True)
    return [{**c, "rerank_score": float(s)} for c, s in scored[:top_k]]


def federated_search(query: str, user: dict, top_k: int = 20, final_k: int = 5) -> dict:
    candidates = vector_search(query, user, top_k=top_k)
    reranked = rerank(query, candidates, top_k=final_k)

    return {
        "query": query,
        "user": {
            "user_id": user["user_id"],
            "role": user["role"],
            "team": user.get("teams", []),
            "clearance": user["clearance"],
        },
        "allowed_levels": allowed_clearance_levels(user["clearance"]),
        "results": reranked,
        "count": len(reranked),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Phase 6.14 federated search self-test ===\n")

    users = [
        {
            "user_id": "alice@acme.com",
            "role": "csuite",
            "tenant_id": "acme",
            "clearance": "CONFIDENTIAL",
            "teams": ["executive"],
        },
        {
            "user_id": "bob@acme.com",
            "role": "manager",
            "tenant_id": "acme",
            "clearance": "INTERNAL",
            "teams": ["platform"],
        },
        {
            "user_id": "carol@acme.com",
            "role": "junior",
            "tenant_id": "acme",
            "clearance": "PUBLIC",
            "teams": ["product"],
        },
    ]

    queries = [
        "deployment runbook",
        "security policy",
        "observability vendor",
    ]

    for query in queries:
        print(f"Query: {query!r}")
        print()
        for user in users:
            result = federated_search(query, user, top_k=20, final_k=3)
            print(f"  User: {user['user_id']:<20} "
                  f"role={user['role']:<8} "
                  f"teams={user['teams']}")
            print(f"    Allowed levels: {result['allowed_levels']}")
            print(f"    Results: {result['count']}")
            for r in result["results"]:
                print(f"      [{r['rerank_score']:.2f}] {r['source_system']:<12} "
                      f"clearance={r['clearance_level']:<12} "
                      f"team={r['owner_team']}")
                if r["alternate_sources"]:
                    print(f"          also in: "
                          f"{[a['source_system'] for a in r['alternate_sources']]}")
            print()
        print("-" * 65)
