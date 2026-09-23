import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")


def log_request(
    user_id: str,
    role: str,
    tenant_id: str,
    query: str,
    returned_chunk_ids: list,
    refused: bool = False,
    reason: str | None = None,
    route: str | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    latency_ms: int | None = None,
):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_log
            (user_id, role, tenant_id, query, route, returned_chunk_ids,
             refused, reason, prompt_tokens, completion_tokens, latency_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            role,
            tenant_id,
            query,
            route,
            returned_chunk_ids,
            refused,
            reason,
            prompt_tokens,
            completion_tokens,
            latency_ms,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    log_request(
        user_id="test_user",
        role="manager",
        tenant_id="acme",
        query="test query",
        returned_chunk_ids=["sample_001_0000"],
        route="hybrid",
        prompt_tokens=120,
        completion_tokens=45,
        latency_ms=890,
    )
    print("Audit log entry written.")

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, route, prompt_tokens, completion_tokens FROM audit_log ORDER BY id DESC LIMIT 1;"
    )
    print("Last row:", cur.fetchone())
    cur.close()
    conn.close()