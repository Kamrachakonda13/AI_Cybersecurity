import re
import sys
from pathlib import Path

# Add project root so `from src.x import y` resolves when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.graph_retrieve import graph_retrieve, list_all_entity_ids  # noqa: E402

# Words that suggest a relationship query
RELATIONSHIP_KEYWORDS = [
    r"\bdepend(s|ency|encies)?\b",
    r"\btransitiv(e|ely)\b",
    r"\bconnect(ed|ion|s)?\b",
    r"\brelat(ed|ionship|ionships)?\b",
    r"\bsource(s)?\b",
    r"\btarget(s)?\b",
    r"\bcollaborat(e|ed|ion)\b",
    r"\bupstream\b",
    r"\bdownstream\b",
    r"\bwhich service",
    r"\bwhat service",
    r"\bhow many services",
    r"\bpath\b",
]

COMPILED_KEYWORDS = [re.compile(p, re.IGNORECASE) for p in RELATIONSHIP_KEYWORDS]


def query_mentions_entity(query: str) -> bool:
    """Check if the query mentions any entity that exists in the graph."""
    all_ids = list_all_entity_ids()
    q = query.lower()
    for entity_id in all_ids:
        pattern = re.escape(entity_id).replace(r"\-", r"[\s\-]?")
        if re.search(pattern, q):
            return True
    return False


def query_has_relationship_keywords(query: str) -> bool:
    """Check if the query contains relationship-oriented phrasing."""
    for pattern in COMPILED_KEYWORDS:
        if pattern.search(query):
            return True
    return False


def route(query: str) -> dict:
    """
    Decide which retrieval path(s) to use.

    Returns a dict with:
      - mode: "graph", "hybrid", or "both"
      - reason: short explanation for logging
    """
    has_entity = query_mentions_entity(query)
    has_relationship_word = query_has_relationship_keywords(query)

    if has_entity and has_relationship_word:
        return {
            "mode": "graph",
            "reason": "Query mentions a known entity AND uses relationship phrasing",
        }

    if has_entity and not has_relationship_word:
        return {
            "mode": "hybrid",
            "reason": "Query mentions an entity but no relationship phrasing",
        }

    return {
        "mode": "hybrid",
        "reason": "No graph entity matched — defaulting to hybrid RAG",
    }


def run_graph_only(query: str) -> dict:
    """Execute graph retrieval and return the subgraph context."""
    return graph_retrieve(query)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What does billing-service depend on?"
    decision = route(q)
    print(f"Query: {q}")
    print(f"Mode:  {decision['mode']}")
    print(f"Why:   {decision['reason']}")