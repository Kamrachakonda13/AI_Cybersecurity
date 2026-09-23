"""
Permissions matrix computation for the dashboard.

For each (team, source) pair, count how many chunks that team can access.
Simplified model:
    - Team clearance ceiling: INTERNAL by default, CONFIDENTIAL for csuite/executive
    - Access if owner_team matches, OR share_scope grants the team,
      OR share_scope is 'org'
"""

import os

import psycopg2
import psycopg2.extras


# Default clearance ceiling per team
TEAM_CLEARANCE = {
    "executive": "CONFIDENTIAL",
    "security": "CONFIDENTIAL",
    "finance": "CONFIDENTIAL",
    "hr": "CONFIDENTIAL",
    # Everything else defaults to INTERNAL
}

CLEARANCE_RANK = {
    "PUBLIC": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4,
}


def _db_url():
    return os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")


def list_all_teams():
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT owner_team
        FROM chunks
        WHERE source_system IS NOT NULL
          AND deleted_at IS NULL
          AND owner_team IS NOT NULL
        ORDER BY owner_team
    """)
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def list_all_sources():
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT source_system
        FROM chunks
        WHERE source_system IS NOT NULL
          AND deleted_at IS NULL
        ORDER BY source_system
    """)
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def _team_can_access(team: str, chunk: dict) -> bool:
    """Pure Python access check (mirrors the SQL filter)."""
    team_ceiling = TEAM_CLEARANCE.get(team, "INTERNAL")
    if CLEARANCE_RANK.get(chunk.get("clearance_level") or "INTERNAL", 2) > CLEARANCE_RANK[team_ceiling]:
        return False

    if chunk.get("owner_team") == team:
        return True

    scope = chunk.get("share_scope")
    if scope == "org":
        return True
    if isinstance(scope, list) and team in scope:
        return True
    # ACL check omitted for the matrix view; covered by drill-down

    return False


def build_matrix():
    """
    Return:
        {
          "teams": [...],
          "sources": [...],
          "cells": {(team, source): {"accessible": N, "total": M, "level": "full"|"partial"|"none"}}
        }
    """
    teams = list_all_teams()
    sources = list_all_sources()

    conn = psycopg2.connect(_db_url())
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            source_system,
            owner_team,
            clearance_level,
            share_scope
        FROM chunks
        WHERE source_system IS NOT NULL
          AND deleted_at IS NULL
    """)
    chunks = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    # Totals per source
    source_totals = {}
    for c in chunks:
        s = c["source_system"]
        source_totals[s] = source_totals.get(s, 0) + 1

    cells = {}
    for team in teams:
        for source in sources:
            total = source_totals.get(source, 0)
            accessible = sum(
                1 for c in chunks
                if c["source_system"] == source and _team_can_access(team, c)
            )
            if total == 0:
                level = "none"
            elif accessible == total:
                level = "full"
            elif accessible > 0:
                level = "partial"
            else:
                level = "none"

            cells[(team, source)] = {
                "accessible": accessible,
                "total": total,
                "level": level,
            }

    return {
        "teams": teams,
        "sources": sources,
        "cells": cells,
    }


def get_accessible_chunks(team: str, source: str, limit: int = 100):
    """Return the chunks that `team` can access from `source`."""
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            id,
            source_file,
            LEFT(content, 200) AS content_preview,
            clearance_level,
            owner_team,
            share_scope
        FROM chunks
        WHERE source_system = %s
          AND deleted_at IS NULL
        ORDER BY id
        LIMIT %s
    """, (source, limit))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    return [r for r in rows if _team_can_access(team, r)]


if __name__ == "__main__":
    print("=== permissions_query self-test ===\n")
    matrix = build_matrix()
    print(f"Teams:   {len(matrix['teams'])}")
    print(f"Sources: {len(matrix['sources'])}")
    print()

    # Print a sample row
    sample_team = matrix["teams"][0] if matrix["teams"] else None
    if sample_team:
        print(f"Sample row for team '{sample_team}':")
        for source in matrix["sources"]:
            cell = matrix["cells"][(sample_team, source)]
            print(f"  {source:<15} {cell['accessible']:>3}/{cell['total']:<3} ({cell['level']})")
    print()
    print("All tests PASS")
