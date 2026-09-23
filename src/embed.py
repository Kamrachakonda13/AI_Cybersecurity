import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_batch
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")
CHUNKS_FILE = Path("data/chunks.json")


def main():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNKS_FILE} not found. Run 'python src/chunk.py' first."
        )

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    chunks = json.loads(CHUNKS_FILE.read_text())
    texts = [c["content"] for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    print("Connecting to Postgres...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    rows = [
        (
            c["id"],
            c["source_file"],
            c["chunk_index"],
            c["content"],
            embeddings[i].tolist(),
            c["clearance_level"],
            c["tenant_id"],
        )
        for i, c in enumerate(chunks)
    ]

    execute_batch(cur, """
        INSERT INTO chunks
            (id, source_file, chunk_index, content, embedding, clearance_level, tenant_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, rows)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(rows)} chunks")


if __name__ == "__main__":
    main()
