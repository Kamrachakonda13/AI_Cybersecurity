import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import psycopg2  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")


def query_audit_log(limit: int = 10, route: str | None = None) -> dict:
    """
    Read-only query of the audit log. Returns the most recent N rows,
    optionally filtered by route.
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        if route:
            cur.execute(
                """
                SELECT id, ts, user_id, role, route, query, refused, latency_ms
                FROM audit_log
                WHERE route = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (route, limit),
            )
        else:
            cur.execute(
                """
                SELECT id, ts, user_id, role, route, query, refused, latency_ms
                FROM audit_log
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,),
            )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        entries = [
            {
                "id": r[0],
                "ts": r[1].isoformat(),
                "user_id": r[2],
                "role": r[3],
                "route": r[4],
                "query": r[5],
                "refused": r[6],
                "latency_ms": r[7],
            }
            for r in rows
        ]

        return {
            "tool": "query_audit_log",
            "ok": True,
            "result": {"entries": entries, "count": len(entries)},
            "summary": f"Retrieved {len(entries)} audit entries"
            + (f" (route={route})" if route else ""),
            "error": None,
        }
    except Exception as e:
        return {
            "tool": "query_audit_log",
            "ok": False,
            "result": None,
            "summary": "Audit query failed.",
            "error": str(e),
        }


if __name__ == "__main__":
    import json

    r = query_audit_log(limit=5)
    print(json.dumps(r, indent=2)[:800])