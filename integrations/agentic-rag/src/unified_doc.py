"""
Unified document model for Phase 6.

Every connector — local FS, S3, Google Drive, SharePoint, Microsoft Graph,
Power BI, Tableau, Confluence, Jira, Slack, Notion — produces UnifiedDocument
instances. Every downstream stage (fingerprinting, dedup, chunking, embedding,
federated search) consumes them.

The model captures five concerns:

1. Identity: which source produced this, and what is its ID in that source?
2. Content: the text and its type.
3. Ownership: which team owns this, and who is accountable?
4. Access: who is allowed to see it? (clearance + share_scope + acl)
5. Provenance: when was it created/modified, and what is its fingerprint?
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations (as constants for simplicity — Python enums add friction here)
# ---------------------------------------------------------------------------

# Clearance levels — same hierarchy as Phase 2/3/5
CLEARANCE_PUBLIC = "PUBLIC"
CLEARANCE_INTERNAL = "INTERNAL"
CLEARANCE_CONFIDENTIAL = "CONFIDENTIAL"
CLEARANCE_RESTRICTED = "RESTRICTED"

VALID_CLEARANCES = {
    CLEARANCE_PUBLIC,
    CLEARANCE_INTERNAL,
    CLEARANCE_CONFIDENTIAL,
    CLEARANCE_RESTRICTED,
}

# Share scope — governs cross-team visibility within a tenant
SHARE_TEAM = "team"    # only the owning team sees it
SHARE_ORG = "org"      # everyone in the tenant with sufficient clearance sees it
# Any other value must be a list of team names, e.g. ["platform", "security"]

# Source systems — enumerated so we can validate and query on them
SOURCE_LOCAL_FS = "local_fs"
SOURCE_S3 = "s3"
SOURCE_MS_GRAPH = "ms_graph"
SOURCE_GOOGLE_DRIVE = "google_drive"
SOURCE_SHAREPOINT = "sharepoint"
SOURCE_M365 = "m365"
SOURCE_POWERBI = "powerbi"
SOURCE_TABLEAU = "tableau"
SOURCE_CONFLUENCE = "confluence"
SOURCE_JIRA = "jira"
SOURCE_SLACK = "slack"
SOURCE_NOTION = "notion"

VALID_SOURCES = {
    SOURCE_LOCAL_FS,
    SOURCE_S3,
    SOURCE_MS_GRAPH,
    SOURCE_GOOGLE_DRIVE,
    SOURCE_SHAREPOINT,
    SOURCE_M365,
    SOURCE_POWERBI,
    SOURCE_TABLEAU,
    SOURCE_CONFLUENCE,
    SOURCE_JIRA,
    SOURCE_SLACK,
    SOURCE_NOTION,
}


# ---------------------------------------------------------------------------
# ACL principal — a single access grant
# ---------------------------------------------------------------------------

@dataclass
class ACLPrincipal:
    """
    A single access grant on a document.

    principal_type is one of: "user", "group", "team", "role"
    principal_id is the identifier in the source system's terms.
        e.g. "user:alice@acme.com" or "group:platform-engineers"
    access is one of: "read", "write", "admin" — only "read" is used by RAG
    """
    principal_type: str
    principal_id: str
    access: str = "read"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ACLPrincipal":
        return cls(
            principal_type=d["principal_type"],
            principal_id=d["principal_id"],
            access=d.get("access", "read"),
        )

    def canonical(self) -> str:
        """Return a canonical string form for SQL containment checks."""
        return f"{self.principal_type}:{self.principal_id}"


# ---------------------------------------------------------------------------
# Unified document
# ---------------------------------------------------------------------------

@dataclass
class UnifiedDocument:
    """
    The single document shape every connector produces.

    Required fields are validated by .validate(). Optional fields default to
    sensible values.
    """

    # --- Identity ---------------------------------------------------------
    source_system: str                         # one of VALID_SOURCES
    source_id: str                             # the ID in that source system
    source_url: Optional[str] = None           # deep link back to the source
    source_path: Optional[str] = None          # path or hierarchy within source

    # --- Content ----------------------------------------------------------
    content: str = ""                          # plain text (connectors must extract)
    mime_type: str = "text/plain"              # original mime type
    title: Optional[str] = None                # human-readable title
    language: str = "en"

    # --- Ownership --------------------------------------------------------
    owner_team: str = "unknown"                # team that owns the document
    owner_user: Optional[str] = None           # specific accountable person
    tenant_id: str = "acme"                    # multi-tenant isolation

    # --- Access -----------------------------------------------------------
    clearance_level: str = CLEARANCE_INTERNAL  # PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED
    share_scope: object = SHARE_TEAM           # "team", "org", or ["team_a", "team_b"]
    acl: list = field(default_factory=list)    # list of ACLPrincipal

    # --- Provenance -------------------------------------------------------
    fingerprint: Optional[str] = None          # SHA-256 of normalized content
    created_at: Optional[str] = None           # ISO 8601 UTC
    last_modified: Optional[str] = None        # ISO 8601 UTC
    ingested_at: Optional[str] = None          # ISO 8601 UTC, set by pipeline
    source_version: Optional[str] = None       # e.g. git SHA, Drive revision, S3 ETag

    # --- Extensibility ----------------------------------------------------
    metadata: dict = field(default_factory=dict)  # source-specific extras

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------

    def validate(self) -> tuple[bool, Optional[str]]:
        """Return (is_valid, reason). Fail closed: missing clearance = invalid."""
        if self.source_system not in VALID_SOURCES:
            return False, f"Unknown source_system: {self.source_system}"

        if not self.source_id:
            return False, "source_id is required"

        if self.clearance_level not in VALID_CLEARANCES:
            return False, f"Unknown clearance_level: {self.clearance_level}"

        if not self.tenant_id:
            return False, "tenant_id is required"

        if not self.owner_team:
            return False, "owner_team is required"

        # share_scope must be "team", "org", or a list of team names
        if not isinstance(self.share_scope, (str, list)):
            return False, f"Invalid share_scope type: {type(self.share_scope).__name__}"

        if isinstance(self.share_scope, str) and self.share_scope not in (SHARE_TEAM, SHARE_ORG):
            return False, f"Invalid share_scope string: {self.share_scope}"

        if isinstance(self.share_scope, list):
            if not all(isinstance(t, str) for t in self.share_scope):
                return False, "share_scope list must contain only team names"

        # Validate ACL principals
        for principal in self.acl:
            if isinstance(principal, dict):
                if "principal_type" not in principal or "principal_id" not in principal:
                    return False, "ACL principal missing required fields"
            elif isinstance(principal, ACLPrincipal):
                if not principal.principal_type or not principal.principal_id:
                    return False, "ACL principal missing required fields"
            else:
                return False, f"ACL principal must be dict or ACLPrincipal, got {type(principal).__name__}"

        return True, None

    # ---------------------------------------------------------------------
    # Conversion helpers
    # ---------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize to a plain dict, with ACL principals converted to dicts."""
        d = asdict(self)
        d["acl"] = [
            p.to_dict() if isinstance(p, ACLPrincipal) else p
            for p in self.acl
        ]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "UnifiedDocument":
        """Reconstruct from a dict (e.g., from fixture files)."""
        acl_raw = d.get("acl") or []
        acl = [
            ACLPrincipal.from_dict(p) if isinstance(p, dict) else p
            for p in acl_raw
        ]
        known = {
            "source_system", "source_id", "source_url", "source_path",
            "content", "mime_type", "title", "language",
            "owner_team", "owner_user", "tenant_id",
            "clearance_level", "share_scope", "acl",
            "fingerprint", "created_at", "last_modified", "ingested_at", "source_version",
            "metadata",
        }
        kwargs = {k: v for k, v in d.items() if k in known}
        kwargs["acl"] = acl
        return cls(**kwargs)

    # ---------------------------------------------------------------------
    # Convenience
    # ---------------------------------------------------------------------

    def document_id(self) -> str:
        """
        Return a globally unique document ID.
        Format: <source_system>:<source_id>
        e.g. "ms_graph:01BYE5RZ6QN3ZWBTUFOFD3GSPGOHDJD36"
        """
        return f"{self.source_system}:{self.source_id}"

    def stamped_ingested_at(self) -> str:
        """Set and return ingested_at."""
        self.ingested_at = datetime.now(timezone.utc).isoformat()
        return self.ingested_at


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # Test 1: valid internal document
    doc = UnifiedDocument(
        source_system=SOURCE_MS_GRAPH,
        source_id="01BYE5RZ6QN3ZWBTUFOFD3GSPGOHDJD36",
        title="Platform Deployment Runbook",
        content="This is the runbook for deploying the platform to production.",
        owner_team="platform",
        owner_user="alice@acme.com",
        clearance_level=CLEARANCE_INTERNAL,
        share_scope=SHARE_ORG,
        acl=[
            ACLPrincipal("group", "platform-engineers", "read"),
            ACLPrincipal("user", "bob@acme.com", "read"),
        ],
        source_url="https://contoso.sharepoint.com/sites/platform/docs/runbook.docx",
        source_version="3",
        last_modified="2026-09-15T10:00:00Z",
    )
    ok, reason = doc.validate()
    print("Test 1 (valid internal doc):", "PASS" if ok else f"FAIL — {reason}")
    print("  document_id:", doc.document_id())

    # Test 2: invalid clearance
    doc2 = UnifiedDocument(
        source_system=SOURCE_LOCAL_FS,
        source_id="bad",
        clearance_level="SUPER_SECRET",
    )
    ok, reason = doc2.validate()
    print("Test 2 (invalid clearance):", "PASS" if not ok else "FAIL — should have rejected")
    print("  reason:", reason)

    # Test 3: fail-closed default clearance
    doc3 = UnifiedDocument(
        source_system=SOURCE_LOCAL_FS,
        source_id="test",
    )
    ok, reason = doc3.validate()
    print("Test 3 (default clearance):", "PASS" if ok else f"FAIL — {reason}")
    print("  default clearance:", doc3.clearance_level, "(should be INTERNAL)")

    # Test 4: round-trip through dict
    d = doc.to_dict()
    doc_rt = UnifiedDocument.from_dict(d)
    ok, reason = doc_rt.validate()
    print("Test 4 (round-trip):", "PASS" if ok and doc_rt.document_id() == doc.document_id() else "FAIL")

    # Test 5: share_scope as list
    doc5 = UnifiedDocument(
        source_system=SOURCE_LOCAL_FS,
        source_id="shared-doc",
        owner_team="platform",
        share_scope=["platform", "security", "sre"],
    )
    ok, reason = doc5.validate()
    print("Test 5 (share_scope list):", "PASS" if ok else f"FAIL — {reason}")

    # Test 6: share_scope invalid string
    doc6 = UnifiedDocument(
        source_system=SOURCE_LOCAL_FS,
        source_id="bad-share",
        owner_team="platform",
        share_scope="everyone",
    )
    ok, reason = doc6.validate()
    print("Test 6 (invalid share_scope):", "PASS" if not ok else "FAIL — should have rejected")

    print()
    print("Full serialized example:")
    print(json.dumps(doc.to_dict(), indent=2, default=str)[:800])