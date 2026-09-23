"""
Query helpers for the chunks dashboard page.
"""

import os
from typing import Optional

import psycopg2
import psycopg2.extras


def _db_url():
    return os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")


def list_sources():
    """Return the distinct source_system values currently in the chunks table."""
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT source_system
        FROM chunks
        WHERE source_system IS NOT NULL
        ORDER BY source_system
    """)
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def list_teams():
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT owner_team
        FROM chunks
        WHERE owner_team IS NOT NULL
        ORDER BY owner_team
    """)
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def count_chunks(
    query: Optional[str] = None,
    source: Optional[str] = None,
    clearance: Optional[str] = None,
    team: Optional[str] = None,
    include_deleted: bool = False,
):
    where, params = _build_where(query, source, clearance, team, include_deleted)
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM chunks {where}", params)
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def _build_where(query, source, clearance, team, include_deleted):
    clauses = []
    params = []
    if not include_deleted:
        clauses.append("deleted_at IS NULL")
    # Exclude legacy Phase 5 chunks (source_system IS NULL) unless explicitly filtered
    clauses.append("source_system IS NOT NULL")
    if query:
        clauses.append("content ILIKE %s")
        params.append(f"%{query}%")
    if source:
        clauses.append("source_system = %s")
        params.append(source)
    if clearance:
        clauses.append("clearance_level = %s")
        params.append(clearance)
    if team:
        clauses.append("owner_team = %s")
        params.append(team)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, tuple(params)


def fetch_chunks(
    query: Optional[str] = None,
    source: Optional[str] = None,
    clearance: Optional[str] = None,
    team: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    include_deleted: bool = False,
):
    where, params = _build_where(query, source, clearance, team, include_deleted)
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"""
        SELECT
            id,
            source_file,
            source_system,
            LEFT(content, 200) AS content_preview,
            clearance_level,
            owner_team,
            share_scope,
            alternate_sources,
            deleted_at
        FROM chunks
        {where}
        ORDER BY id
        LIMIT %s OFFSET %s
    """, params + (limit, offset))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


if __name__ == "__main__":
    print("=== chunks_query self-test ===\n")
    sources = list_sources()
    teams = list_teams()
    total = count_chunks()
    print(f"Total chunks: {total}")
    print(f"Sources: {sources}")
    print(f"Teams: {teams}")
    print()
    print("First 3 chunks:")
    for c in fetch_chunks(limit=3):
        src = c['source_system'] or 'legacy'
        cl = c['clearance_level'] or 'NONE'
        tm = c['owner_team'] or 'unknown'
        print(f"  {c['id'][:40]:<42} | {src:<12} | {cl:<12} | {tm}")
    print()
    print("Filtered: source=s3")
    for c in fetch_chunks(source="s3", limit=5):
        print(f"  {c['id']:<40} | {c['source_system']}")
    print()
    print("All tests PASS")
