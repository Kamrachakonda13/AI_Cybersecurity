import os
import re

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "ragpassword")

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver


def list_all_entity_ids() -> list:
    with get_driver().session() as s:
        result = s.run("MATCH (n) RETURN n.id AS id ORDER BY id")
        return [r["id"] for r in result if r["id"]]


def extract_entity_ids(query: str, all_entity_ids: list) -> list:
    """
    Naive entity recognition: find any known entity id mentioned in the query.
    Matches either the hyphenated id or the multi-word form.
    """
    q = query.lower()
    found = []
    for entity_id in all_entity_ids:
        pattern = re.escape(entity_id).replace(r"\-", r"[\s\-]?")
        if re.search(pattern, q):
            found.append(entity_id)
    return found


def traverse_from_entities(entity_ids: list, depth: int = 2, limit: int = 30) -> list:
    """
    Return all relationships reachable within `depth` hops from any of the given
    starting entities.
    """
    if not entity_ids:
        return []

    # Cypher does not allow parameters in path bounds; depth is interpolated as int.
    # This is safe because depth comes from our own code, not user input.
    depth = int(depth)
    query = f"""
        MATCH (start)
        WHERE start.id IN $ids
        MATCH path = (start)-[*1..{depth}]-(end)
        UNWIND relationships(path) AS r
        WITH DISTINCT r
        MATCH (a)-[r]->(b)
        RETURN a.id   AS source,
               a.name AS source_name,
               type(r) AS rel,
               b.id   AS target,
               b.name AS target_name,
               r.clearance_level AS clearance
        LIMIT $limit
    """

    with get_driver().session() as s:
        result = s.run(query, ids=entity_ids, limit=limit)
        return [dict(r) for r in result]


def format_subgraph_as_text(rows: list) -> str:
    """Convert rows into readable prose for the LLM."""
    if not rows:
        return "No graph relationships found."

    lines = []
    for r in rows:
        lines.append(
            f"{r['source_name']} ({r['source']}) --[{r['rel']}]--> "
            f"{r['target_name']} ({r['target']})"
        )
    return "\n".join(lines)


def graph_retrieve(query: str, top_k: int = 30) -> dict:
    """
    Full graph retrieval pipeline:
      1. Identify entities in the query.
      2. Traverse the graph up to 2 hops.
      3. Return the subgraph as structured rows + prose.
    """
    all_ids = list_all_entity_ids()
    matched = extract_entity_ids(query, all_ids)

    if not matched:
        return {
            "matched_entities": [],
            "rows": [],
            "context": "No entities from the query matched the graph.",
        }

    rows = traverse_from_entities(matched, depth=2, limit=top_k)

    return {
        "matched_entities": matched,
        "rows": rows,
        "context": format_subgraph_as_text(rows),
    }


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "What does billing-service depend on?"
    result = graph_retrieve(q)
    print("Matched entities:", result["matched_entities"])
    print()
    print("Subgraph context:")
    print(result["context"])