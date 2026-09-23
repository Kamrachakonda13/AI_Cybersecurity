"""
Shared base class for fixture-based source connectors.

Every stub connector (Google Drive, SharePoint, Power BI, Tableau, Confluence,
Jira, Slack, Notion, M365) inherits from FixtureSourceConnector. Each subclass
only needs to set SOURCE_SYSTEM and optionally override a transform hook.

The fixture format is designed to mirror the real API shape so that replacing
fixture data with live API calls is a client-swap, not a rewrite.

Fixture layout:
    data/connectors/{source_system}_fixtures/
        documents.json      # list of document descriptors
        permissions.json    # optional: {source_id: [permission dicts]}
        content/            # optional: local files matching content_fixture_path
            file1.md
            file2.md
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from .base import BaseConnector
from .exceptions import (
    InvalidConfigurationError,
    NotFoundError,
)


class FixtureSourceConnector(BaseConnector):
    """
    Fixture-based connector base.

    Subclasses must set SOURCE_SYSTEM and may override transform_document().
    """

    SOURCE_SYSTEM = "fixture"

    def __init__(
        self,
        *,
        config_path: str,
        **kwargs,
    ):
        super().__init__(tenant_id="acme", owner_team="unknown", **kwargs)

        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise InvalidConfigurationError(
                f"Config not found: {self.config_path}",
                source_system=self.SOURCE_SYSTEM,
            )

        config = json.loads(self.config_path.read_text())
        self.tenant_id = config.get("tenant_id", self.tenant_id)
        self.display_name = config.get("display_name", self.SOURCE_SYSTEM)

        # Fixture directory (defaults to {source_system}_fixtures/)
        fc = config.get("fixture_client", {})
        self.fixtures_dir = Path(
            fc.get("fixtures_dir", f"data/connectors/{self.SOURCE_SYSTEM}_fixtures")
        )
        self.content_root = Path(fc.get("content_root", "."))

        if not self.fixtures_dir.exists():
            raise InvalidConfigurationError(
                f"Fixtures directory not found: {self.fixtures_dir}",
                source_system=self.SOURCE_SYSTEM,
            )

        # Load documents and permissions
        self._documents = self._load_json("documents.json")
        if isinstance(self._documents, dict):
            self._documents = self._documents.get("value", [])

        permissions_path = self.fixtures_dir / "permissions.json"
        self._permissions = {}
        if permissions_path.exists():
            self._permissions = json.loads(permissions_path.read_text())

        # Team mapping (owner -> team/clearance/scope)
        tm = config.get("team_mapping", {})
        self.default_team = tm.get("default_team", "unknown")
        self.default_clearance = tm.get("default_clearance", "INTERNAL")
        self.default_share_scope = tm.get("default_share_scope", "team")
        self.owner_team_map = tm.get("owners", {})

        # Per-collection overrides (e.g., per-folder, per-channel, per-project)
        self.collection_governance = config.get("collection_governance", {})

        self._cursor: dict = {}

    # ---------------------------------------------------------------------
    # Fixture loading
    # ---------------------------------------------------------------------

    def _load_json(self, name: str):
        path = self.fixtures_dir / name
        if not path.exists():
            raise InvalidConfigurationError(
                f"Fixture not found: {path}",
                source_system=self.SOURCE_SYSTEM,
            )
        return json.loads(path.read_text())

    # ---------------------------------------------------------------------
    # Required interface
    # ---------------------------------------------------------------------

    def test_connection(self) -> bool:
        if not self._documents:
            raise InvalidConfigurationError(
                f"No documents in fixture for {self.SOURCE_SYSTEM}",
                source_system=self.SOURCE_SYSTEM,
            )
        return True

    def list_changed_since(
        self,
        cursor: Optional[str],
        *,
        limit: int = 500,
    ) -> Iterator[dict]:
        previous = {}
        if cursor:
            try:
                previous = json.loads(cursor)
            except json.JSONDecodeError:
                previous = {}

        yielded = 0
        for doc in self._documents:
            if yielded >= limit:
                return

            source_id = doc.get("id")
            if not source_id:
                continue

            version = doc.get("version") or (
                f"{doc.get('last_modified', '')}-{doc.get('size', 0)}"
            )

            prev = previous.get(source_id)
            if prev and prev.get("version") == version:
                self._cursor[source_id] = prev
                continue

            self._cursor[source_id] = {"version": version}

            yield self.transform_document(doc)
            yielded += 1

    def fetch_document(self, source_id: str) -> dict:
        doc = self._doc_by_id(source_id)
        if doc is None:
            raise NotFoundError(
                f"Document not found in fixture: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        content = self._read_content(doc)

        return {
            "source_id": source_id,
            "content": content,
            "mime_type": doc.get("mime_type", doc.get("mimeType", "text/plain")),
            "title": doc.get("title", doc.get("name", "")),
            "source_url": doc.get("source_url", doc.get("webUrl")),
            "source_path": doc.get("source_path", doc.get("path", "")),
            "created_at": doc.get("created_at", doc.get("createdDateTime")),
            "last_modified": doc.get("last_modified", doc.get("lastModifiedDateTime")),
            "source_version": self._version_of(doc),
            "metadata": doc.get("metadata", {}),
        }

    def get_acl(self, source_id: str) -> dict:
        doc = self._doc_by_id(source_id)
        if doc is None:
            raise NotFoundError(
                f"Document not found in fixture: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        owner = doc.get("owner", doc.get("owner_user", ""))
        collection = doc.get("collection", doc.get("folder", ""))

        # Priority: owner mapping > collection governance > default
        owner_cfg = self.owner_team_map.get(owner, {})
        coll_cfg = self.collection_governance.get(collection, {})

        owner_team = (
            owner_cfg.get("team")
            or coll_cfg.get("team")
            or self.default_team
        )
        clearance = (
            owner_cfg.get("clearance")
            or coll_cfg.get("clearance")
            or self.default_clearance
        )
        share_scope = (
            owner_cfg.get("share_scope")
            or coll_cfg.get("share_scope")
            or self.default_share_scope
        )

        acl = []
        if source_id in self._permissions:
            for perm in self._permissions[source_id]:
                principal_type = perm.get("principal_type", "user")
                principal_id = perm.get("principal_id")
                access = perm.get("access", "read")
                if principal_id:
                    acl.append({
                        "principal_type": principal_type,
                        "principal_id": principal_id,
                        "access": access,
                    })

        return {
            "clearance_level": clearance,
            "share_scope": share_scope,
            "acl": acl,
            "owner_team": owner_team,
            "owner_user": owner or None,
        }

    def get_cursor(self) -> Optional[str]:
        if not self._cursor:
            return None
        return json.dumps(self._cursor)

    # ---------------------------------------------------------------------
    # Overridable hooks
    # ---------------------------------------------------------------------

    def transform_document(self, doc: dict) -> dict:
        """
        Convert a fixture document descriptor into the shape list_changed_since yields.
        Subclasses may override to extract source-specific metadata.

        Default implementation produces the minimum required shape.
        """
        return {
            "source_id": doc.get("id"),
            "source_version": self._version_of(doc),
            "last_modified": doc.get("last_modified", doc.get("lastModifiedDateTime", "")),
            "title": doc.get("title", doc.get("name", "")),
            "mime_type": doc.get("mime_type", doc.get("mimeType", "text/plain")),
        }

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _doc_by_id(self, source_id: str) -> Optional[dict]:
        for doc in self._documents:
            if doc.get("id") == source_id:
                return doc
        return None

    def _version_of(self, doc: dict) -> str:
        if doc.get("version"):
            return doc["version"]
        lm = doc.get("last_modified", doc.get("lastModifiedDateTime", ""))
        size = doc.get("size", 0)
        return f"{lm}-{size}"

    def _read_content(self, doc: dict) -> str:
        rel = doc.get("content_fixture_path")
        if rel:
            path = self.content_root / rel
            if path.exists():
                return path.read_text(encoding="utf-8")
            raise NotFoundError(
                f"Content file not found: {path}",
                source_system=self.SOURCE_SYSTEM,
            )
        # Fall back to inline content if present
        return doc.get("content", "")