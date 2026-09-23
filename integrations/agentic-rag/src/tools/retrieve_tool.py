import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.hybrid_retrieve import hybrid_retrieve  # noqa: E402
from src.rerank import rerank  # noqa: E402


def retrieve(query: str, user_clearance: str, tenant_id: str, top_k: int = 5) -> dict:
    """
    Hybrid retrieval with reranking, wrapped as an agent tool.
    Returns a uniform tool-result dict.
    """
    try:
        candidates = hybrid_retrieve(
            query,
            user_clearance=user_clearance,
            tenant_id=tenant_id,
            top_k=20,
        )
        if not candidates:
            return {
                "tool": "retrieve",
                "ok": True,
                "result": {"chunks": [], "count": 0},
                "summary": "No accessible chunks matched the query.",
                "error": None,
            }

        reranked = rerank(query, candidates, top_k=top_k)
        chunks = [
            {
                "id": c["id"],
                "source": c["source_file"],
                "clearance_level": c["clearance_level"],
                "content": c["content"],
                "rerank_score": float(c["rerank_score"]),
            }
            for c in reranked
        ]

        ids = [c["id"] for c in chunks]
        return {
            "tool": "retrieve",
            "ok": True,
            "result": {"chunks": chunks, "count": len(chunks)},
            "summary": f"Retrieved {len(chunks)} chunks: {', '.join(ids)}",
            "error": None,
        }
    except Exception as e:
        return {
            "tool": "retrieve",
            "ok": False,
            "result": None,
            "summary": "Retrieval failed.",
            "error": str(e),
        }


if __name__ == "__main__":
    import json

    r = retrieve("What is the retry policy?", "INTERNAL", "acme")
    print(json.dumps(r, indent=2)[:800])