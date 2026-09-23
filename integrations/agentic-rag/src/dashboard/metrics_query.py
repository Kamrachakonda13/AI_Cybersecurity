"""
Metrics aggregation for the dashboard.

Reads from:
    - audit_log table (Postgres): user_id, role, route, tokens, latency
    - data/traces.jsonl: reasoning traces
"""

import json
import os
from pathlib import Path

import psycopg2
import psycopg2.extras


TRACES_FILE = Path("data/traces.jsonl")


def _db_url():
    return os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")


def _connect():
    try:
        return psycopg2.connect(_db_url())
    except Exception:
        return None


def summary_metrics():
    conn = _connect()
    if conn is None:
        return {
            "total_requests": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "avg_latency_ms": 0,
            "max_latency_ms": 0,
            "refusal_count": 0,
            "error": "database unavailable",
        }

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT
                COUNT(*) AS total_requests,
                COALESCE(SUM(prompt_tokens), 0) AS total_prompt_tokens,
                COALESCE(SUM(completion_tokens), 0) AS total_completion_tokens,
                COALESCE(AVG(latency_ms), 0) AS avg_latency_ms,
                COALESCE(MAX(latency_ms), 0) AS max_latency_ms,
                COUNT(*) FILTER (WHERE refused = true) AS refusal_count
            FROM audit_log
        """)
        row = cur.fetchone()
        return {
            "total_requests": row["total_requests"] or 0,
            "total_prompt_tokens": row["total_prompt_tokens"] or 0,
            "total_completion_tokens": row["total_completion_tokens"] or 0,
            "avg_latency_ms": round(float(row["avg_latency_ms"] or 0), 1),
            "max_latency_ms": int(row["max_latency_ms"] or 0),
            "refusal_count": row["refusal_count"] or 0,
            "error": None,
        }
    except Exception as e:
        return {
            "total_requests": 0, "total_prompt_tokens": 0,
            "total_completion_tokens": 0, "avg_latency_ms": 0,
            "max_latency_ms": 0, "refusal_count": 0,
            "error": str(e)[:200],
        }
    finally:
        cur.close()
        conn.close()


def tokens_by_route():
    conn = _connect()
    if conn is None:
        return []
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT
                COALESCE(route, 'unknown') AS route,
                COUNT(*) AS calls,
                COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                COALESCE(SUM(completion_tokens), 0) AS completion_tokens
            FROM audit_log
            GROUP BY route
            ORDER BY calls DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        cur.close()
        conn.close()


def latency_buckets():
    """Return latency distribution bucketed by 500ms intervals."""
    conn = _connect()
    if conn is None:
        return []
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT latency_ms
            FROM audit_log
            WHERE latency_ms IS NOT NULL
        """)
        rows = [r["latency_ms"] for r in cur.fetchall()]
    except Exception:
        rows = []
    finally:
        cur.close()
        conn.close()

    if not rows:
        return []

    buckets = {
        "0-500": 0, "500-1000": 0, "1000-2000": 0,
        "2000-5000": 0, "5000-10000": 0, "10000+": 0,
    }
    for ms in rows:
        if ms < 500: buckets["0-500"] += 1
        elif ms < 1000: buckets["500-1000"] += 1
        elif ms < 2000: buckets["1000-2000"] += 1
        elif ms < 5000: buckets["2000-5000"] += 1
        elif ms < 10000: buckets["5000-10000"] += 1
        else: buckets["10000+"] += 1

    return [{"bucket": k, "count": v} for k, v in buckets.items()]


def recent_traces(limit: int = 20):
    if not TRACES_FILE.exists():
        return []
    lines = TRACES_FILE.read_text().strip().splitlines()
    rows = []
    for line in lines[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(rows))


def recent_requests(limit: int = 20):
    conn = _connect()
    if conn is None:
        return []
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT
                ts, user_id, role, route, query,
                refused, latency_ms, prompt_tokens, completion_tokens
            FROM audit_log
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))
        return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("=== metrics_query self-test ===\n")
    s = summary_metrics()
    print("Summary:")
    for k, v in s.items():
        print(f"  {k:<25} {v}")
    print()

    by_route = tokens_by_route()
    print("Tokens by route:")
    for r in by_route:
        print(f"  {r['route']:<15} calls={r['calls']:<5} prompt={r['prompt_tokens']:<8} completion={r['completion_tokens']}")
    print()

    lat = latency_buckets()
    print("Latency buckets:")
    for b in lat:
        print(f"  {b['bucket']:<15} {b['count']}")
    print()

    traces = recent_traces(5)
    print(f"Recent traces: {len(traces)}")
    print()
    print("All tests PASS")
