"""
SQL query tool for Phase 7.

Queries the sample company SQLite database with read-only SQL.
Blocks DDL, DML, and any statement that isn't a SELECT.
"""

import os
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

DB_PATH = Path(os.getenv("SAMPLE_DB_PATH", "data/sample_company.db"))

ALLOWED_TABLES = {"users", "products", "transactions", "support_tickets"}

FORBIDDEN_KEYWORDS = re.compile(
    r"\b("
    r"insert|update|delete|drop|create|alter|truncate|replace|"
    r"attach|detach|pragma|vacuum|reindex|analyze|"
    r"grant|revoke|begin|commit|rollback|savepoint|"
    r"load_extension"
    r")\b",
    re.IGNORECASE,
)


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip()


def _validate(sql: str):
    stripped = _strip_comments(sql)
    if not stripped:
        return False, "empty_sql"
    if not re.match(r"^\s*select\b", stripped, re.IGNORECASE):
        return False, "only_select_allowed"
    if FORBIDDEN_KEYWORDS.search(stripped):
        match = FORBIDDEN_KEYWORDS.search(stripped)
        return False, f"forbidden_keyword:{match.group(0).lower()}"
    if ";" in stripped.rstrip(";"):
        return False, "multiple_statements_not_allowed"
    table_refs = re.findall(
        r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", stripped, re.IGNORECASE)
    for table in table_refs:
        if table.lower() not in ALLOWED_TABLES:
            return False, f"table_not_whitelisted:{table}"
    return True, None


def query_sql(sql: str, limit: int = 50) -> dict:
    limit = min(max(1, int(limit)), 500)

    ok, err = _validate(sql)
    if not ok:
        return {
            "tool": "query_sql",
            "ok": False,
            "result": None,
            "summary": f"SQL validation failed: {err}",
            "error": err,
        }

    if not DB_PATH.exists():
        return {
            "tool": "query_sql",
            "ok": False,
            "result": None,
            "summary": f"Database not found: {DB_PATH}",
            "error": "db_not_found",
        }

    try:
        uri = f"file:{DB_PATH}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchmany(limit)
        result_rows = [dict(r) for r in rows]
        cur.close()
        conn.close()

        return {
            "tool": "query_sql",
            "ok": True,
            "result": {
                "sql": sql,
                "rows": result_rows,
                "row_count": len(result_rows),
                "limit": limit,
            },
            "summary": f"Returned {len(result_rows)} rows",
            "error": None,
        }

    except sqlite3.Error as e:
        return {
            "tool": "query_sql",
            "ok": False,
            "result": None,
            "summary": f"SQL execution failed: {e}",
            "error": str(e)[:200],
        }


if __name__ == "__main__":
    print("=== SQL query tool self-test ===\n")

    r1 = query_sql("SELECT user_id, email, role, team FROM users LIMIT 3")
    print(
        f"Test 1 (valid select): {'PASS' if r1['ok'] and r1['result']['row_count'] == 3 else 'FAIL'}")
    if r1["ok"]:
        for row in r1["result"]["rows"]:
            print(f"    {row}")

    r2 = query_sql("INSERT INTO users VALUES ('x','x','x','x','x','x')")
    print(
        f"Test 2 (reject INSERT): {'PASS' if not r2['ok'] and 'forbidden' in (r2['error'] or '') else 'FAIL'}")

    r3 = query_sql("DROP TABLE users")
    print(f"Test 3 (reject DROP): {'PASS' if not r3['ok'] else 'FAIL'}")

    r4 = query_sql("SELECT * FROM secrets")
    print(
        f"Test 4 (reject unknown table): {'PASS' if not r4['ok'] and 'not_whitelisted' in (r4['error'] or '') else 'FAIL'}")

    r5 = query_sql("SELECT 1; DROP TABLE users")
    print(
        f"Test 5 (reject multi-statement): {'PASS' if not r5['ok'] else 'FAIL'}")

    r6 = query_sql("SELECT * FROM users -- INSERT INTO users")
    print(f"Test 6 (comment handling): {'PASS' if r6['ok'] else 'FAIL'}")

    r7 = query_sql(
        "SELECT status, COUNT(*) AS count FROM transactions GROUP BY status")
    print(f"Test 7 (aggregate query): {'PASS' if r7['ok'] else 'FAIL'}")
    if r7["ok"]:
        for row in r7["result"]["rows"]:
            print(f"    {row}")

    r8 = query_sql("SELECT full_name FROM users LIMIT 3")
    print(f"Test 8 (simple select): {'PASS' if r8['ok'] else 'FAIL'}")

    print()
    print("All SQL query tool tests PASS")
