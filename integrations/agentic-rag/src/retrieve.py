import os

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def retrieve(query: str, top_k: int = 5):
    query_vec = get_model().encode(
        [query], normalize_embeddings=True)[0].tolist()

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, source_file, content, 1 - (embedding <=> %s::vector) AS score
        FROM chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (query_vec, query_vec, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"id": r[0], "source_file": r[1],
            "content": r[2], "score": float(r[3])}
        for r in rows
    ]


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "What is the retry policy?"
    for r in retrieve(q):
        print(f"[{r['score']:.3f}] {r['id']}: {r['content'][:80]}")
