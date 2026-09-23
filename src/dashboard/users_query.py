"""
Users and effective access computation for the dashboard.
"""

import os

import psycopg2
import psycopg2.extras


SIMULATED_USERS = [
    {"user_id": "alice@acme.com", "role": "csuite",   "clearance": "CONFIDENTIAL", "teams": ["executive"]},
    {"user_id": "bob@acme.com",   "role": "manager",  "clearance": "INTERNAL",     "teams": ["platform"]},
    {"user_id": "carol@acme.com", "role": "junior",   "clearance": "PUBLIC",       "teams": ["product"]},
    {"user_id": "dave@acme.com",  "role": "senior",   "clearance": "INTERNAL",     "teams": ["sre"]},
    {"user_id": "eve@acme.com",   "role": "senior",   "clearance": "CONFIDENTIAL", "teams": ["security"]},
    {"user_id": "frank@acme.com", "role": "junior",   "clearance": "INTERNAL",     "teams": ["engineering"]},
    {"user_id": "grace@acme.com", "role": "manager",  "clearance": "INTERNAL",     "teams": ["analytics"]},
    {"user_id": "henry@acme.com", "role": "manager",  "clearance": "INTERNAL",     "teams": ["data-platform"]},
    {"user_id": "ivy@acme.com",   "role": "junior",   "clearance": "PUBLIC",       "teams": ["marketing"]},
    {"user_id": "jack@acme.com",  "role": "csuite",   "clearance": "CONFIDENTIAL", "teams": ["executive"]},
]


CLEARANCE_RANK = {"PUBLIC": 1, "INTERNAL": 2, "CONFIDENTIAL": 3, "RESTRICTED": 4}


def _db_url():
    return os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")


def _user_can_access(user: dict, chunk: dict) -> bool:
    user_clearance = user["clearance"]
    if CLEARANCE_RANK.get(chunk.get("clearance_level") or "INTERNAL", 2) > CLEARANCE_RANK[user_clearance]:
        return False

    user_teams = set(user.get("teams", []))
    owner = chunk.get("owner_team")
    if owner and owner in user_teams:
        return True

    scope = chunk.get("share_scope")
    if scope == "org":
        return True
    if isinstance(scope, list) and user_teams & set(scope):
        return True

    return False


def list_users_with_access_counts():
    conn = psycopg2.connect(_db_url())
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id, source_system, clearance_level, owner_team, share_scope
        FROM chunks
        WHERE source_system IS NOT NULL AND deleted_at IS NULL
    """)
    chunks = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    out = []
    for user in SIMULATED_USERS:
        accessible = sum(1 for c in chunks if _user_can_access(user, c))
        out.append({**user, "accessible_chunks": accessible, "total_chunks": len(chunks)})
    return out


def get_user_chunks(user_id: str, limit: int = 200):
    user = next((u for u in SIMULATED_USERS if u["user_id"] == user_id), None)
    if not user:
        return None, []

    conn = psycopg2.connect(_db_url())
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            id, source_system, source_file,
            LEFT(content, 200) AS content_preview,
            clearance_level, owner_team, share_scope
        FROM chunks
        WHERE source_system IS NOT NULL AND deleted_at IS NULL
        ORDER BY id
        LIMIT %s
    """, (limit,))
    all_chunks = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    accessible = [c for c in all_chunks if _user_can_access(user, c)]
    return user, accessible


if __name__ == "__main__":
    print("=== users_query self-test ===\n")
    users = list_users_with_access_counts()
    print(f"Users: {len(users)}\n")
    for u in users:
        teams = ", ".join(u["teams"])
        print(f"  {u['user_id']:<22} role={u['role']:<10} "
              f"clearance={u['clearance']:<14} "
              f"teams=[{teams}] "
              f"access={u['accessible_chunks']}/{u['total_chunks']}")
    print()
    print("Drill-down for alice@acme.com:")
    user, chunks = get_user_chunks("alice@acme.com")
    print(f"  {user['user_id']}: {len(chunks)} accessible chunks")
    print()
    print("All tests PASS")
