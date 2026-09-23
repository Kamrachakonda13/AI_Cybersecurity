import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.graph_retrieve import graph_retrieve  # noqa: E402


def graph_query(query: str, user_clearance: str = "CONFIDENTIAL") -> dict:
    """
    Graph RAG retrieval wrapped as an agent tool.
    Enforces clearance on returned edges.
    """
    CLEARANCE_RANK = {
        "PUBLIC": 1,
        "INTERNAL": 2,
        "CONFIDENTIAL": 3,
        "RESTRICTED": 4,
    }

    try:
        result = graph_retrieve(query)
        matched = result["matched_entities"]
        rows = result["rows"]

        if not matched:
            return {
                "tool": "graph_query",
                "ok": True,
                "result": {"matched_entities": [], "edges": [], "count": 0},
                "summary": "No graph entities matched the query.",
                "error": None,
            }

        max_rank = CLEARANCE_RANK.get(user_clearance, 1)
        allowed = []
        for r in rows:
            edge_clearance = r.get("clearance") or "INTERNAL"
            if CLEARANCE_RANK.get(edge_clearance, 99) <= max_rank:
                allowed.append(r)

        edges = [
            {
                "source": r["source"],
                "rel": r["rel"],
                "target": r["target"],
                "clearance": r.get("clearance"),
            }
            for r in allowed
        ]

        return {
            "tool": "graph_query",
            "ok": True,
            "result": {
                "matched_entities": matched,
                "edges": edges,
                "count": len(edges),
                "context": result["context"],
            },
            "summary": (
                f"Matched {len(matched)} entities; traversed {len(edges)} edges "
                f"at {user_clearance} clearance."
            ),
            "error": None,
        }
    except Exception as e:
        return {
            "tool": "graph_query",
            "ok": False,
            "result": None,
            "summary": "Graph traversal failed.",
            "error": str(e),
        }


if __name__ == "__main__":
    import json

    r = graph_query("What does billing-service depend on?", "INTERNAL")
    print(json.dumps(r, indent=2)[:800])