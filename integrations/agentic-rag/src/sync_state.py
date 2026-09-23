"""
SQLite-backed sync state for the Phase 6 ingestion pipeline.

Tracks every (source_system, source_id) pair that has been indexed, along with
the fingerprint of the indexed content. On each run, the pipeline can compare
the current fingerprint against the stored one to decide whether to re-embed.

Schema:
    documents
        source_system     TEXT
        source_id         TEXT
        fingerprint       TEXT
        last_indexed_at   TIMESTAMPTZ (ISO string)
        chunk_count       INTEGER
        alternate_sources JSONB (JSON string)
        PRIMARY KEY (source_system, source_id)
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_DB_PATH = "data/sync_state.db"


class SyncState:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        conn = self._connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    source_system     TEXT NOT NULL,
                    source_id         TEXT NOT NULL,
                    fingerprint       TEXT,
                    last_indexed_at   TEXT NOT NULL,
                    chunk_count       INTEGER NOT NULL DEFAULT 0,
                    alternate_sources TEXT NOT NULL DEFAULT '[]',
                    PRIMARY KEY (source_system, source_id)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # -------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------

    def get(self, source_system: str, source_id: str) -> Optional[dict]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM documents WHERE source_system = ? AND source_id = ?",
                (source_system, source_id),
            ).fetchone()
            if row is None:
                return None
            d = dict(row)
            d["alternate_sources"] = json.loads(d["alternate_sources"])
            return d
        finally:
            conn.close()

    def is_unchanged(self, source_system: str, source_id: str, fingerprint: str) -> bool:
        row = self.get(source_system, source_id)
        if row is None:
            return False
        return row.get("fingerprint") == fingerprint

    def all_indexed_keys(self) -> set:
        """Return the set of (source_system, source_id) pairs currently indexed."""
        conn = self._connect()
        try:
            rows = conn.execute("SELECT source_system, source_id FROM documents").fetchall()
            return {(r["source_system"], r["source_id"]) for r in rows}
        finally:
            conn.close()

    # -------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------

    def upsert(
        self,
        source_system: str,
        source_id: str,
        fingerprint: str,
        chunk_count: int,
        alternate_sources: list,
    ):
        now = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO documents
                    (source_system, source_id, fingerprint, last_indexed_at,
                     chunk_count, alternate_sources)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (source_system, source_id) DO UPDATE SET
                    fingerprint = excluded.fingerprint,
                    last_indexed_at = excluded.last_indexed_at,
                    chunk_count = excluded.chunk_count,
                    alternate_sources = excluded.alternate_sources
            """, (
                source_system,
                source_id,
                fingerprint,
                now,
                chunk_count,
                json.dumps(alternate_sources),
            ))
            conn.commit()
        finally:
            conn.close()

    def remove(self, source_system: str, source_id: str):
        conn = self._connect()
        try:
            conn.execute(
                "DELETE FROM documents WHERE source_system = ? AND source_id = ?",
                (source_system, source_id),
            )
            conn.commit()
        finally:
            conn.close()

    def stats(self) -> dict:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS c, COALESCE(SUM(chunk_count), 0) AS t FROM documents"
            ).fetchone()
            return {"documents": row["c"], "chunks": row["t"]}
        finally:
            conn.close()


if __name__ == "__main__":
    print("=== sync_state self-test ===\n")
    import os

    test_db = "/tmp/test_sync_state.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    s = SyncState(test_db)
    print("Test 1 (init): PASS")

    s.upsert("local_fs", "/path/a.md", "fp:v1:abc", 3, [])
    s.upsert("s3", "bucket/b.md", "fp:v1:def", 5, [{"source_system": "gdrive", "source_id": "x"}])
    print("Test 2 (upsert): PASS")

    row = s.get("local_fs", "/path/a.md")
    assert row["chunk_count"] == 3
    assert row["fingerprint"] == "fp:v1:abc"
    print("Test 3 (get): PASS")

    assert s.is_unchanged("local_fs", "/path/a.md", "fp:v1:abc") is True
    assert s.is_unchanged("local_fs", "/path/a.md", "fp:v1:xyz") is False
    print("Test 4 (is_unchanged): PASS")

    keys = s.all_indexed_keys()
    assert ("local_fs", "/path/a.md") in keys
    assert ("s3", "bucket/b.md") in keys
    print("Test 5 (all_indexed_keys): PASS")

    s.upsert("local_fs", "/path/a.md", "fp:v1:new", 4, [])
    row = s.get("local_fs", "/path/a.md")
    assert row["fingerprint"] == "fp:v1:new"
    assert row["chunk_count"] == 4
    print("Test 6 (upsert update): PASS")

    s.remove("s3", "bucket/b.md")
    assert s.get("s3", "bucket/b.md") is None
    print("Test 7 (remove): PASS")

    stats = s.stats()
    assert stats["documents"] == 1
    print("Test 8 (stats): PASS")

    os.remove(test_db)
    print()
    print("All sync_state tests PASS")
