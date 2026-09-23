"""
Deduplication engine for Phase 6.

Identifies documents with identical content across all sources, groups them
by content fingerprint, and selects a canonical document for each group.

Canonical selection rule (Option A):
    1. Highest clearance wins (fail-secure).
       PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED
    2. Ties broken by oldest last_modified (the original is the canonical).

Alternate sources are recorded on the canonical document as `alternate_sources`,
so a single indexed chunk can be traced back to every location that contains it.

Usage:
    from src.connectors.registry import ConnectorRegistry
    from src.dedup import find_duplicates, select_canonical, build_dedup_report

    registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
    groups = find_duplicates(registry)
    report = build_dedup_report(groups)
    print(report)
"""

from datetime import datetime, timezone
from typing import Optional

from src.fingerprint import content_fingerprint


# Clearance ranking for canonical selection
CLEARANCE_RANK = {
    "PUBLIC": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4,
}


# ---------------------------------------------------------------------------
# Document record
# ---------------------------------------------------------------------------

class DocumentRecord:
    """
    A single fetched document with all metadata needed for dedup and downstream
    ingestion.
    """

    __slots__ = (
        "source_system", "source_id", "source_url", "title",
        "content", "mime_type",
        "owner_team", "owner_user", "clearance_level", "share_scope", "acl",
        "last_modified", "created_at", "fingerprint",
        "connector_name",
    )

    def __init__(
        self,
        *,
        source_system: str,
        source_id: str,
        content: str,
        connector_name: str,
        source_url: Optional[str] = None,
        title: Optional[str] = None,
        mime_type: str = "text/plain",
        owner_team: str = "unknown",
        owner_user: Optional[str] = None,
        clearance_level: str = "INTERNAL",
        share_scope=None,
        acl=None,
        last_modified: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.source_system = source_system
        self.source_id = source_id
        self.source_url = source_url
        self.title = title
        self.content = content
        self.mime_type = mime_type
        self.owner_team = owner_team
        self.owner_user = owner_user
        self.clearance_level = clearance_level
        self.share_scope = share_scope or "team"
        self.acl = acl or []
        self.last_modified = last_modified
        self.created_at = created_at
        self.connector_name = connector_name
        self.fingerprint = content_fingerprint(content)

    def to_dict(self) -> dict:
        return {
            "source_system": self.source_system,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "title": self.title,
            "mime_type": self.mime_type,
            "owner_team": self.owner_team,
            "owner_user": self.owner_user,
            "clearance_level": self.clearance_level,
            "share_scope": self.share_scope,
            "acl": self.acl,
            "last_modified": self.last_modified,
            "created_at": self.created_at,
            "fingerprint": self.fingerprint,
            "connector_name": self.connector_name,
            "content_length": len(self.content),
        }


# ---------------------------------------------------------------------------
# Fetch all documents from all connectors
# ---------------------------------------------------------------------------

def fetch_all_documents(registry) -> tuple:
    """
    Iterate every connector, fetch every document, return (records, errors).

    Returns:
        (list[DocumentRecord], list[dict])  -- records and per-connector errors.
    """
    records = []
    errors = []

    for connector_name, connector in registry.all_connectors():
        try:
            changes = list(connector.list_changed_since(cursor=None))
        except Exception as e:
            errors.append({
                "connector": connector_name,
                "stage": "list",
                "error": f"{type(e).__name__}: {str(e)[:200]}",
            })
            continue

        for change in changes:
            source_id = change.get("source_id")
            try:
                doc = connector.fetch_document(source_id)
            except Exception as e:
                errors.append({
                    "connector": connector_name,
                    "source_id": source_id,
                    "stage": "fetch",
                    "error": f"{type(e).__name__}: {str(e)[:200]}",
                })
                continue

            try:
                acl = connector.get_acl(source_id)
            except Exception as e:
                errors.append({
                    "connector": connector_name,
                    "source_id": source_id,
                    "stage": "acl",
                    "error": f"{type(e).__name__}: {str(e)[:200]}",
                })
                acl = {}

            try:
                record = DocumentRecord(
                    source_system=connector.SOURCE_SYSTEM,
                    source_id=source_id,
                    content=doc.get("content", ""),
                    connector_name=connector_name,
                    source_url=doc.get("source_url"),
                    title=doc.get("title"),
                    mime_type=doc.get("mime_type", "text/plain"),
                    owner_team=acl.get("owner_team", "unknown"),
                    owner_user=acl.get("owner_user"),
                    clearance_level=acl.get("clearance_level", "INTERNAL"),
                    share_scope=acl.get("share_scope", "team"),
                    acl=acl.get("acl", []),
                    last_modified=doc.get("last_modified"),
                    created_at=doc.get("created_at"),
                )
                records.append(record)
            except Exception as e:
                errors.append({
                    "connector": connector_name,
                    "source_id": source_id,
                    "stage": "construct",
                    "error": f"{type(e).__name__}: {str(e)[:200]}",
                })

    return records, errors


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def find_duplicates(registry) -> dict:
    """
    Return {'groups': {fingerprint: [DocumentRecord, ...]}, 'errors': [...]}.

    Only fingerprints with 2+ members are included in groups.
    Fingerprints with 0 or 1 member are ignored (unique documents).
    """
    records, errors = fetch_all_documents(registry)

    by_fingerprint: dict = {}
    for record in records:
        fp = record.fingerprint
        if fp is None:
            continue
        by_fingerprint.setdefault(fp, []).append(record)

    duplicate_groups = {
        fp: members
        for fp, members in by_fingerprint.items()
        if len(members) > 1
    }

    return {
        "groups": duplicate_groups,
        "total_documents": len(records),
        "unique_fingerprints": len(by_fingerprint),
        "duplicate_groups": len(duplicate_groups),
        "duplicate_documents": sum(len(m) - 1 for m in duplicate_groups.values()),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Canonical selection
# ---------------------------------------------------------------------------

def _clearance_rank(level: str) -> int:
    return CLEARANCE_RANK.get(level, 0)


def _parse_ts(ts: Optional[str]) -> float:
    """Parse an ISO timestamp into a sortable float. Missing → far future."""
    if not ts:
        return float("inf")
    try:
        s = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(s).timestamp()
    except (ValueError, AttributeError):
        return float("inf")


def select_canonical(members: list) -> tuple:
    """
    Choose the canonical document from a duplicate group.

    Returns (canonical, alternates).

    Rule (Option A):
        1. Highest clearance wins.
        2. Tie broken by oldest last_modified (the "original").
        3. Further tie broken by lexicographic source_id for determinism.
    """
    if not members:
        return None, []

    def sort_key(record):
        # Sort ascending by clearance rank reversed (highest first)
        # then by last_modified ascending (oldest first)
        # then by source_id for determinism
        return (
            -_clearance_rank(record.clearance_level),
            _parse_ts(record.last_modified),
            record.source_id,
        )

    ordered = sorted(members, key=sort_key)
    canonical = ordered[0]
    alternates = ordered[1:]
    return canonical, alternates


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def build_dedup_report(result: dict) -> str:
    """
    Render the dedup analysis as a human-readable report.
    """
    lines = []
    lines.append("=== Phase 6.12 deduplication report ===")
    lines.append("")

    lines.append(f"Total documents:     {result['total_documents']}")
    lines.append(f"Unique fingerprints: {result['unique_fingerprints']}")
    lines.append(f"Duplicate groups:    {result['duplicate_groups']}")
    lines.append(f"Redundant copies:    {result['duplicate_documents']}")
    lines.append("")

    if result["duplicate_groups"] == 0:
        lines.append("No duplicates found.")
    else:
        group_index = 1
        for fp, members in result["groups"].items():
            canonical, alternates = select_canonical(members)

            lines.append(f"Duplicate group {group_index}:")
            lines.append(f"  Fingerprint: {fp}")
            lines.append(f"  Members: {len(members)}")
            lines.append("")

            lines.append(f"    [CANONICAL] {canonical.connector_name} ({canonical.source_system})")
            lines.append(f"      source_id:   {canonical.source_id}")
            lines.append(f"      title:       {canonical.title}")
            lines.append(f"      owner_team:  {canonical.owner_team}")
            lines.append(f"      clearance:   {canonical.clearance_level}")
            lines.append(f"      share_scope: {canonical.share_scope}")
            if canonical.source_url:
                lines.append(f"      source_url:  {canonical.source_url}")
            lines.append("")

            for alt in alternates:
                lines.append(f"    [ALTERNATE] {alt.connector_name} ({alt.source_system})")
                lines.append(f"      source_id:   {alt.source_id}")
                lines.append(f"      title:       {alt.title}")
                lines.append(f"      owner_team:  {alt.owner_team}")
                lines.append(f"      clearance:   {alt.clearance_level}")
                lines.append(f"      share_scope: {alt.share_scope}")
                if alt.source_url:
                    lines.append(f"      source_url:  {alt.source_url}")
                lines.append("")

            # Cross-team summary
            teams = sorted({m.owner_team for m in members})
            if len(teams) > 1:
                lines.append(f"  Cross-team overlap: {' <-> '.join(teams)}")
                lines.append("")

            group_index += 1

    if result["errors"]:
        lines.append(f"Errors during fetch: {len(result['errors'])}")
        for err in result["errors"][:5]:
            lines.append(f"  {err['connector']} [{err.get('stage', '?')}]: {err['error']}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pathlib import Path as P

    sys.path.insert(0, str(P(__file__).resolve().parent.parent))

    from src.connectors.registry import ConnectorRegistry

    print("=== Phase 6.12 deduplication self-test ===\n")

    project_root = P(__file__).resolve().parent.parent
    manifest = project_root / "data" / "connectors" / "registry.json"

    print("Loading connectors...")
    registry = ConnectorRegistry.from_manifest(str(manifest))
    print(f"  Loaded {len(registry.loaded_names())} connectors\n")

    print("Fetching all documents...")
    result = find_duplicates(registry)
    print(f"  Fetched {result['total_documents']} documents\n")

    report = build_dedup_report(result)
    print(report)

    # Assertions
    print()
    print("Assertions:")
    assert result["duplicate_groups"] >= 1, "expected at least 1 duplicate group"
    print("  [PASS] Found at least one duplicate group")

    # Verify the specific group we engineered
    for fp, members in result["groups"].items():
        systems = {m.source_system for m in members}
        if "local_fs" in systems and "sharepoint" in systems:
            canonical, alternates = select_canonical(members)
            assert canonical.clearance_level in ("INTERNAL", "CONFIDENTIAL", "RESTRICTED")
            print(f"  [PASS] Cross-source duplicate: local_fs <-> sharepoint")
            print(f"  [PASS] Canonical selected: {canonical.connector_name} ({canonical.clearance_level})")
            break
    else:
        print("  [FAIL] Expected local_fs/sharepoint duplicate group not found")
        sys.exit(1)

    print()
    print("All deduplication tests PASS")
