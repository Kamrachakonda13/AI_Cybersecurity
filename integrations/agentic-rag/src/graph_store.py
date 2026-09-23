import json
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "ragpassword")

ENTITIES_FILE = Path("data/graph/entities.json")
RELATIONSHIPS_FILE = Path("data/graph/relationships.json")

# Entities we consider noise — drop them during load
IGNORE_ENTITY_IDS = {"internal", "public", "confidential", "restricted"}


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def clear_graph(session):
    session.run("MATCH (n) DETACH DELETE n")


def load_entities(session, entities):
    """Create one node per entity, tagged with its type label."""
    for ent in entities:
        if ent["id"] in IGNORE_ENTITY_IDS:
            continue
        session.run(
            f"MERGE (n:{ent['type']} {{id: $id}}) "
            f"SET n.name = $name",
            id=ent["id"],
            name=ent["name"],
        )


def load_relationships(session, relationships, entities):
    """
    Create relationships. Auto-create missing nodes as Component type
    (covers cases like docs-service that appear only in relationships).
    """
    known_ids = {e["id"] for e in entities if e["id"] not in IGNORE_ENTITY_IDS}

    for rel in relationships:
        if rel["source"] in IGNORE_ENTITY_IDS or rel["target"] in IGNORE_ENTITY_IDS:
            continue

        # Auto-create nodes that weren't in the entities list
        for node_id in (rel["source"], rel["target"]):
            if node_id not in known_ids:
                session.run(
                    "MERGE (n:Component {id: $id}) SET n.name = $id",
                    id=node_id,
                )
                known_ids.add(node_id)

        # Relationship with clearance and source metadata on the edge
        session.run(
            f"MATCH (s {{id: $source}}) "
            f"MATCH (t {{id: $target}}) "
            f"MERGE (s)-[r:{rel['type']}]->(t) "
            f"SET r.clearance_level = $clearance, "
            f"    r.source_chunk = $source_chunk, "
            f"    r.tenant_id = $tenant_id",
            source=rel["source"],
            target=rel["target"],
            clearance=rel["clearance_level"],
            source_chunk=rel["source_chunk"],
            tenant_id=rel["tenant_id"],
        )


def main():
    entities = json.loads(ENTITIES_FILE.read_text())
    relationships = json.loads(RELATIONSHIPS_FILE.read_text())

    print(f"Connecting to {NEO4J_URI}...")
    driver = get_driver()

    with driver.session() as session:
        print("Clearing existing graph...")
        clear_graph(session)

        print(f"Loading {len(entities)} entities...")
        load_entities(session, entities)

        print(f"Loading {len(relationships)} relationships...")
        load_relationships(session, relationships, entities)

        node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

    driver.close()

    print()
    print(f"Graph loaded: {node_count} nodes, {rel_count} relationships")


if __name__ == "__main__":
    main()