import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

CHUNKS_FILE = Path("data/chunks.json")
ENTITIES_FILE = Path("data/graph/entities.json")
RELATIONSHIPS_FILE = Path("data/graph/relationships.json")

ENTITIES_FILE.parent.mkdir(parents=True, exist_ok=True)

EXTRACTION_PROMPT = """You are a knowledge graph extraction engine.

From the text below, extract:
1. Entities: named services, systems, policies, databases, stores, roles, or components.
2. Relationships between those entities.

Output STRICT JSON with this exact schema and nothing else:

{
  "entities": [
    {"id": "auth-service", "type": "Service", "name": "auth-service"}
  ],
  "relationships": [
    {"source": "auth-service", "target": "identity-database", "type": "DEPENDS_ON"}
  ]
}

Rules:
- Entity ids must be lowercase-hyphenated.
- Allowed entity types: Service, Database, Policy, Role, Store, Component.
- Allowed relationship types: DEPENDS_ON, USES_POLICY, STORES, CLASSIFIED_AS, COMMUNICATES_WITH.
- Only include entities and relationships that are EXPLICITLY stated in the text.
- If nothing is extractable, return an empty entities and relationships array.
- Do not include any commentary, markdown fences, or text outside the JSON.

Text:
__CHUNK__"""


def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_from_chunk(chunk_text: str) -> dict:
    prompt = EXTRACTION_PROMPT.replace("__CHUNK__", chunk_text)
    response = get_client().chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  JSON parse failed: {e}")
        print(f"  Raw output: {raw[:300]}")
        return {"entities": [], "relationships": []}


def main():
    chunks = json.loads(CHUNKS_FILE.read_text())

    target_chunks = [c for c in chunks if c["source_file"] == "sample_006.md"]

    if not target_chunks:
        print("No sample_006.md chunks found. Did you add the file and re-run chunk.py?")
        return

    print(f"Extracting from {len(target_chunks)} chunks...")

    all_entities = {}
    all_relationships = []

    for i, chunk in enumerate(target_chunks):
        print(f"  [{i+1}/{len(target_chunks)}] {chunk['id']}")
        result = extract_from_chunk(chunk["content"])

        for ent in result.get("entities", []):
            all_entities[ent["id"]] = ent

        for rel in result.get("relationships", []):
            all_relationships.append({
                **rel,
                "source_chunk": chunk["id"],
                "clearance_level": chunk["clearance_level"],
                "tenant_id": chunk["tenant_id"],
            })

    entities_list = list(all_entities.values())

    ENTITIES_FILE.write_text(json.dumps(entities_list, indent=2))
    RELATIONSHIPS_FILE.write_text(json.dumps(all_relationships, indent=2))

    print()
    print(f"Extracted {len(entities_list)} entities, {len(all_relationships)} relationships")
    print(f"Saved to {ENTITIES_FILE} and {RELATIONSHIPS_FILE}")


if __name__ == "__main__":
    main()