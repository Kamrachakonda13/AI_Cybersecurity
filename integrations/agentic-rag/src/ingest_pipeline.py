"""
Ingestion pipeline orchestrator for Phase 6.

End-to-end flow:
    1. Load registry (all configured connectors)
    2. Fetch every document, compute fingerprints
    3. Find duplicate groups, select canonicals
    4. For each canonical document:
         a. Check sync_state: unchanged? skip.
         b. Mark old chunks (same source_system+source_id) as deleted.
         c. Chunk content, embed, insert into pgvector.
    5. Detect removed documents (in sync_state but not in current fetch)
    6. Soft-delete their chunks
    7. Update sync_state
    8. Write report

Idempotent: running twice with no source changes produces no new rows.
"""

from src.sync_state import SyncState
from src.fingerprint import content_fingerprint
from src.dedup import find_duplicates, select_canonical
from src.connectors.registry import ConnectorRegistry
from sentence_transformers import SentenceTransformer
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import psycopg2
import json
import os
import sys
import time
from pathlib import Path
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")
SYNC_STATE_DB = os.getenv("SYNC_STATE_DB", "data/sync_state.db")

# Chunking parameters (same as Phase 1)
CHUNK_SIZE = 400
OVERLAP = 50


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            last_period = text.rfind(".", start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
    return [c for c in chunks if len(c) >= 50]


# ---------------------------------------------------------------------------
# Database writes
# ---------------------------------------------------------------------------

def mark_deleted(cur, source_system: str, source_id: str):
    """
    Soft-delete all existing chunks for a (source_system, source_id) pair.
    Used when re-ingesting a changed document or removing a deleted one.
    """
    cur.execute("""
        UPDATE chunks
        SET deleted_at = NOW()
        WHERE source_system = %s
          AND id LIKE %s
          AND deleted_at IS NULL
    """, (source_system, f"%{source_id}%"))


def insert_chunks(cur, rows: list):
    execute_batch(cur, """
        INSERT INTO chunks
            (id, source_file, chunk_index, content, embedding,
             clearance_level, tenant_id, source_system, alternate_sources, fingerprint,
             owner_team, share_scope, acl)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            content = excluded.content,
            embedding = excluded.embedding,
            clearance_level = excluded.clearance_level,
            alternate_sources = excluded.alternate_sources,
            owner_team = excluded.owner_team,
            share_scope = excluded.share_scope,
            acl = excluded.acl,
            deleted_at = NULL
    """, rows)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(dry_run: bool = False) -> dict:
    started = time.time()
    report = {
        "connectors_loaded": 0,
        "documents_fetched": 0,
        "duplicate_groups": 0,
        "canonical_documents": 0,
        "skipped_unchanged": 0,
        "reindexed": 0,
        "removed": 0,
        "chunks_written": 0,
        "errors": [],
    }

    # 1. Registry
    print("[1/7] Loading registry...")
    registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
    report["connectors_loaded"] = len(registry.loaded_names())
    print(f"      Loaded {report['connectors_loaded']} connectors")

    # 2. Fetch + dedup
    print("[2/7] Fetching documents and finding duplicates...")
    dedup_result = find_duplicates(registry)
    report["documents_fetched"] = dedup_result["total_documents"]
    report["duplicate_groups"] = dedup_result["duplicate_groups"]
    report["errors"].extend(dedup_result.get("errors", []))
    print(f"      Fetched {report['documents_fetched']} documents, "
          f"{report['duplicate_groups']} duplicate group(s)")

    # 3. Prepare canonical list
    print("[3/7] Selecting canonicals...")
    canonical_records = []  # list of (canonical, alternates)
    # All fingerprints (unique + duplicate groups)
    all_fingerprints = {}

    # Iterate over all fetched documents to get canonical per fingerprint
    # (dedup_result only exposes duplicate groups; we need all documents)
    # Re-fetch to get all documents
    from src.dedup import fetch_all_documents
    all_records, _ = fetch_all_documents(registry)

    by_fp = {}
    for r in all_records:
        if r.fingerprint is None:
            continue
        by_fp.setdefault(r.fingerprint, []).append(r)

    for fp, members in by_fp.items():
        if len(members) > 1:
            canonical, alternates = select_canonical(members)
        else:
            canonical = members[0]
            alternates = []
        canonical_records.append((canonical, alternates))

    report["canonical_documents"] = len(canonical_records)
    print(f"      {report['canonical_documents']} canonical documents "
          f"(after dedup)")

    # 4. Sync state
    print("[4/7] Checking sync state...")
    sync_state = SyncState(SYNC_STATE_DB)
    currently_indexed = sync_state.all_indexed_keys()
    print(f"      Sync state has {len(currently_indexed)} indexed documents")

    # 5. Chunk and embed
    print("[5/7] Chunking and embedding changed documents...")

    to_index = []
    current_keys = set()

    for canonical, alternates in canonical_records:
        key = (canonical.source_system, canonical.source_id)
        current_keys.add(key)

        if sync_state.is_unchanged(canonical.source_system, canonical.source_id, canonical.fingerprint):
            report["skipped_unchanged"] += 1
            continue

        to_index.append((canonical, alternates))

    print(f"      {report['skipped_unchanged']} unchanged, "
          f"{len(to_index)} to index")

    model = None
    if to_index:
        print("      Loading embedding model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

    chunks_to_insert = []

    for canonical, alternates in to_index:
        # Chunk the canonical content
        chunks = chunk_text(canonical.content)
        if not chunks:
            continue

        # Embed
        embeddings = model.encode(
            chunks, normalize_embeddings=True, show_progress_bar=False)

        # Alternate sources payload
        alternate_payload = [
            {
                "source_system": alt.source_system,
                "source_id": alt.source_id,
                "source_url": alt.source_url,
                "owner_team": alt.owner_team,
            }
            for alt in alternates
        ]

        # Canonical chunk ID prefix: source_system:source_id
        source_file = f"{canonical.source_system}:{canonical.source_id}"

        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            def _short_hash(s: str) -> str:
                return hashlib.sha256(s.encode()).hexdigest()[:8]
            chunk_id = f"{canonical.source_system}_{_short_hash(canonical.source_id)}_{i:04d}"
            chunks_to_insert.append((
                chunk_id,
                source_file,
                i,
                chunk,
                emb.tolist(),
                canonical.clearance_level,
                "acme",
                canonical.source_system,
                json.dumps(alternate_payload),
                canonical.fingerprint,
                canonical.owner_team,
                json.dumps(canonical.share_scope),
                json.dumps(canonical.acl),
            ))

        report["reindexed"] += 1

    report["chunks_written"] = len(chunks_to_insert)

    # 6. Detect removed documents
    print("[6/7] Detecting removed documents...")
    removed_keys = currently_indexed - current_keys
    report["removed"] = len(removed_keys)
    print(f"      {report['removed']} document(s) removed from sources")

    # 7. Write to database
    if dry_run:
        print("[7/7] DRY RUN — no writes")
    else:
        print("[7/7] Writing to database...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Mark old chunks of changed documents as deleted
        for canonical, alternates in to_index:
            mark_deleted(cur, canonical.source_system, canonical.source_id)

        # Mark removed documents' chunks as deleted
        for source_system, source_id in removed_keys:
            mark_deleted(cur, source_system, source_id)

        # Insert new chunks
        if chunks_to_insert:
            insert_chunks(cur, chunks_to_insert)

        conn.commit()
        cur.close()
        conn.close()

        # Update sync state
        for canonical, alternates in to_index:
            alternate_payload = [
                {"source_system": alt.source_system, "source_id": alt.source_id}
                for alt in alternates
            ]
            chunk_count = len(chunk_text(canonical.content))
            sync_state.upsert(
                canonical.source_system,
                canonical.source_id,
                canonical.fingerprint,
                chunk_count,
                alternate_payload,
            )

        for source_system, source_id in removed_keys:
            sync_state.remove(source_system, source_id)

    report["duration_seconds"] = round(time.time() - started, 2)
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 65)
    print("Phase 6.13 — Enterprise ingestion pipeline")
    print("=" * 65)
    print()

    report = run_pipeline(dry_run=dry_run)

    print()
    print("=" * 65)
    print("Report")
    print("=" * 65)
    for k, v in report.items():
        if k == "errors":
            print(f"  errors: {len(v)}")
        else:
            print(f"  {k}: {v}")
    print("=" * 65)


if __name__ == "__main__":
    main()
