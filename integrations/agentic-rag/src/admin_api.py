"""
Admin API for Phase 6.

Exposes the ingestion fabric for inspection and control:
    GET  /admin/connectors              - list all connectors
    GET  /admin/connectors/{name}       - one connector's detail
    POST /admin/ingest                  - trigger the pipeline
    GET  /admin/sync-state              - what's indexed
    GET  /admin/duplicates              - current duplicate groups
    GET  /admin/sources/{name}          - documents from a source

Mounted on the main FastAPI app via include_router().
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import APIRouter, HTTPException  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from src.connectors.registry import ConnectorRegistry  # noqa: E402
from src.dedup import find_duplicates, select_canonical  # noqa: E402
from src.ingest_pipeline import run_pipeline  # noqa: E402
from src.sync_state import SyncState  # noqa: E402

router = APIRouter(prefix="/admin", tags=["admin"])

MANIFEST = "data/connectors/registry.json"
SYNC_DB = "data/sync_state.db"


def _registry():
    return ConnectorRegistry.from_manifest(MANIFEST)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    dry_run: bool = False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/connectors")
def list_connectors():
    registry = _registry()
    out = []
    for entry in registry.list_sources():
        name = entry["name"]
        item = {
            "name": name,
            "status": entry["status"],
            "source_system": entry.get("source_system"),
            "display_name": entry.get("display_name"),
        }
        if entry["status"] == "loaded":
            try:
                connector = registry.get(name)
                docs = list(connector.list_changed_since(cursor=None))
                item["document_count"] = len(docs)
            except Exception as e:
                item["document_count"] = None
                item["error"] = str(e)[:200]
        else:
            item["error"] = entry.get("error")
        out.append(item)
    return {"connectors": out, "count": len(out)}


@router.get("/connectors/{name}")
def connector_detail(name: str):
    registry = _registry()
    try:
        connector = registry.get(name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Connector not found: {e}")

    docs = list(connector.list_changed_since(cursor=None))

    # Sample first 3 docs with their ACLs
    sample = []
    for change in docs[:3]:
        try:
            acl = connector.get_acl(change["source_id"])
        except Exception:
            acl = {}
        sample.append({
            "source_id": change["source_id"],
            "title": change.get("title"),
            "mime_type": change.get("mime_type"),
            "clearance_level": acl.get("clearance_level"),
            "owner_team": acl.get("owner_team"),
            "share_scope": acl.get("share_scope"),
        })

    return {
        "name": name,
        "source_system": getattr(connector, "SOURCE_SYSTEM", "unknown"),
        "document_count": len(docs),
        "sample_documents": sample,
        "observability": connector.observability() if hasattr(connector, "observability") else {},
    }


@router.post("/ingest")
def trigger_ingest(req: IngestRequest):
    try:
        report = run_pipeline(dry_run=req.dry_run)
        return {"status": "ok", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@router.get("/sync-state")
def get_sync_state():
    s = SyncState(SYNC_DB)
    stats = s.stats()
    keys = sorted(s.all_indexed_keys())
    return {
        "documents_indexed": stats["documents"],
        "total_chunks": stats["chunks"],
        "indexed_keys": [f"{ss}:{sid}" for ss, sid in keys],
    }


@router.get("/duplicates")
def get_duplicates():
    registry = _registry()
    result = find_duplicates(registry)

    groups = []
    for fp, members in result["groups"].items():
        canonical, alternates = select_canonical(members)
        groups.append({
            "fingerprint": fp,
            "member_count": len(members),
            "canonical": {
                "source_system": canonical.source_system,
                "source_id": canonical.source_id,
                "owner_team": canonical.owner_team,
                "clearance_level": canonical.clearance_level,
            },
            "alternates": [
                {
                    "source_system": alt.source_system,
                    "source_id": alt.source_id,
                    "owner_team": alt.owner_team,
                    "clearance_level": alt.clearance_level,
                }
                for alt in alternates
            ],
            "cross_team_overlap": sorted({m.owner_team for m in members}),
        })

    return {
        "total_documents": result["total_documents"],
        "unique_fingerprints": result["unique_fingerprints"],
        "duplicate_groups": result["duplicate_groups"],
        "redundant_copies": result["duplicate_documents"],
        "groups": groups,
    }


@router.get("/sources/{name}")
def source_documents(name: str, limit: int = 50):
    registry = _registry()
    try:
        connector = registry.get(name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Connector not found: {e}")

    docs = list(connector.list_changed_since(cursor=None))

    out = []
    for change in docs[:limit]:
        try:
            acl = connector.get_acl(change["source_id"])
        except Exception:
            acl = {}
        out.append({
            "source_id": change["source_id"],
            "title": change.get("title"),
            "last_modified": change.get("last_modified"),
            "clearance_level": acl.get("clearance_level"),
            "owner_team": acl.get("owner_team"),
            "share_scope": acl.get("share_scope"),
            "acl": acl.get("acl", []),
        })

    return {"connector": name, "count": len(out), "documents": out}


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Phase 6.15 admin API self-test ===\n")

    # Direct call to each endpoint function
    r1 = list_connectors()
    print(f"Test 1 (list_connectors): {r1['count']} connectors")
    assert r1["count"] == 12

    r2 = connector_detail("local_fs")
    print(f"Test 2 (connector_detail): local_fs has {r2['document_count']} docs")
    assert r2["document_count"] >= 6

    r3 = get_sync_state()
    print(f"Test 3 (sync_state): {r3['documents_indexed']} docs, {r3['total_chunks']} chunks")
    assert r3["documents_indexed"] >= 40

    r4 = get_duplicates()
    print(f"Test 4 (duplicates): {r4['duplicate_groups']} groups")
    assert r4["duplicate_groups"] >= 1

    r5 = source_documents("s3")
    print(f"Test 5 (source_documents): s3 has {r5['count']} docs")
    assert r5["count"] >= 3

    print()
    print("All admin API tests PASS")
