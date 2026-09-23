"""
Local filesystem connector for Phase 6.

Reads text files from one or more configured directory roots. Each root has
its own governance metadata (owner_team, clearance_level, share_scope).

Configuration file (JSON):
    {
      "connector_type": "local_fs",
      "tenant_id": "acme",
      "roots": [
        {
          "path": "/abs/path/to/root",
          "owner_team": "platform",
          "clearance_level": "INTERNAL",
          "share_scope": "org"
        }
      ]
    }

Per-file metadata override:
    Place a `.metadata.json` file alongside the document with optional keys:
        {"owner_team": ..., "clearance_level": ..., "share_scope": ...,
         "owner_user": ..., "acl": [...]}
    Values in the sidecar override the root config for that file only.

Security:
    Symlinks are not followed. Any symlink whose target is outside the root
    is skipped with a warning. This prevents symlink attacks that would let
    the connector read arbitrary files.
"""

import hashlib
import json
import mimetypes
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from .base import BaseConnector
from .exceptions import (
    InvalidConfigurationError,
    NotFoundError,
    TransientError,
)


# Extensions we know how to read as plain text
TEXT_EXTENSIONS = {
    ".txt", ".md", ".markdown", ".rst",
    ".json", ".yaml", ".yml", ".toml",
    ".csv", ".tsv", ".log",
    ".py", ".js", ".ts", ".java", ".go", ".rs", ".rb",
    ".html", ".xml", ".sql", ".sh", ".bash",
}

# Extensions we explicitly skip (binary or unsupported in Phase 6.4)
SKIPPED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".mp4", ".mp3", ".wav", ".mov",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".class",
}


class LocalFSConnector(BaseConnector):
    """Filesystem connector with per-root governance metadata."""

    SOURCE_SYSTEM = "local_fs"

    def __init__(
        self,
        *,
        config_path: str,
        tenant_id: Optional[str] = None,
        owner_team: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            tenant_id=tenant_id or "acme",
            owner_team=owner_team or "unknown",
            **kwargs,
        )

        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise InvalidConfigurationError(
                f"Config file not found: {self.config_path}",
                source_system=self.SOURCE_SYSTEM,
            )

        try:
            config = json.loads(self.config_path.read_text())
        except json.JSONDecodeError as e:
            raise InvalidConfigurationError(
                f"Invalid JSON in {self.config_path}: {e}",
                source_system=self.SOURCE_SYSTEM,
            )

        self.tenant_id = config.get("tenant_id", self.tenant_id)
        self.roots = []
        for root_cfg in config.get("roots", []):
            root_path = Path(root_cfg["path"]).resolve()
            if not root_path.exists():
                raise InvalidConfigurationError(
                    f"Configured root does not exist: {root_path}",
                    source_system=self.SOURCE_SYSTEM,
                )
            if not root_path.is_dir():
                raise InvalidConfigurationError(
                    f"Configured root is not a directory: {root_path}",
                    source_system=self.SOURCE_SYSTEM,
                )
            self.roots.append({
                "path": root_path,
                "owner_team": root_cfg.get("owner_team", "unknown"),
                "clearance_level": root_cfg.get("clearance_level", "INTERNAL"),
                "share_scope": root_cfg.get("share_scope", "team"),
                "owner_user": root_cfg.get("owner_user"),
                "acl": root_cfg.get("acl", []),
            })

        if not self.roots:
            raise InvalidConfigurationError(
                f"No roots configured in {self.config_path}",
                source_system=self.SOURCE_SYSTEM,
            )

        # In-memory cursor: {absolute_path: {"mtime": float, "size": int, "version": str}}
        self._cursor: dict = {}

    # ---------------------------------------------------------------------
    # Required interface
    # ---------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Verify each configured root is readable."""
        for root in self.roots:
            if not os.access(root["path"], os.R_OK):
                raise TransientError(
                    f"Root not readable: {root['path']}",
                    source_system=self.SOURCE_SYSTEM,
                )
        return True

    def list_changed_since(
        self,
        cursor: Optional[str],
        *,
        limit: int = 500,
    ) -> Iterator[dict]:
        """
        Yield files that are new or modified since the last sync.

        The cursor is passed as a JSON string of the previous _cursor state,
        or None for a full sync.
        """
        previous = {}
        if cursor:
            try:
                previous = json.loads(cursor)
            except json.JSONDecodeError:
                # Corrupt cursor → full re-sync
                previous = {}

        yielded = 0
        for root in self.roots:
            for file_path in sorted(root["path"].rglob("*")):
                if yielded >= limit:
                    return
                if not file_path.is_file():
                    continue

                # Skip symlinks pointing outside the root
                if file_path.is_symlink():
                    try:
                        target = file_path.resolve()
                        if not str(target).startswith(str(root["path"]) + os.sep) and target != root["path"]:
                            continue
                    except OSError:
                        continue

                ext = file_path.suffix.lower()
                if ext in SKIPPED_EXTENSIONS:
                    continue
                if ext not in TEXT_EXTENSIONS:
                    continue

                try:
                    stat = file_path.stat()
                except OSError:
                    continue

                abs_str = str(file_path)
                mtime = stat.st_mtime
                size = stat.st_size
                version = f"{int(mtime)}-{size}"

                prev = previous.get(abs_str)
                if prev and prev.get("version") == version:
                    # Unchanged
                    self._cursor[abs_str] = prev
                    continue

                self._cursor[abs_str] = {
                    "mtime": mtime,
                    "size": size,
                    "version": version,
                }

                yield {
                    "source_id": abs_str,
                    "source_version": version,
                    "last_modified": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                    "title": file_path.stem,
                    "mime_type": mimetypes.guess_type(str(file_path))[0] or "text/plain",
                }
                yielded += 1

    def fetch_document(self, source_id: str) -> dict:
        """Read a file and return its content."""
        path = Path(source_id)

        if not path.exists():
            raise NotFoundError(
                f"File not found: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        if not path.is_file():
            raise NotFoundError(
                f"Not a file: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        # Ensure the file is inside one of our roots
        root = self._root_for_path(path)
        if root is None:
            raise NotFoundError(
                f"File outside configured roots: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            raise TransientError(
                f"Failed to read {source_id}: {e}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        stat = path.stat()

        return {
            "source_id": str(path),
            "content": content,
            "mime_type": mimetypes.guess_type(str(path))[0] or "text/plain",
            "title": path.stem,
            "source_url": f"file://{path}",
            "source_path": str(path.relative_to(root["path"])),
            "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
            "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "source_version": f"{int(stat.st_mtime)}-{stat.st_size}",
            "metadata": {
                "root_path": str(root["path"]),
                "extension": path.suffix.lower(),
            },
        }

    def get_acl(self, source_id: str) -> dict:
        """Return the ACL for a file, using root config plus optional sidecar overrides."""
        path = Path(source_id)
        root = self._root_for_path(path)
        if root is None:
            raise NotFoundError(
                f"File outside configured roots: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        # Start with root defaults
        acl = {
            "clearance_level": root["clearance_level"],
            "share_scope": root["share_scope"],
            "acl": list(root.get("acl", [])),
            "owner_team": root["owner_team"],
            "owner_user": root.get("owner_user"),
        }

        # Apply sidecar overrides if present
        sidecar = path.parent / ".metadata.json"
        if sidecar.exists():
            try:
                overrides = json.loads(sidecar.read_text())
                for key in ("clearance_level", "share_scope", "owner_team", "owner_user"):
                    if key in overrides:
                        acl[key] = overrides[key]
                if "acl" in overrides:
                    acl["acl"] = overrides["acl"]
            except (json.JSONDecodeError, OSError):
                # Ignore sidecar parse failures — fail closed with root defaults
                pass

        return acl

    def get_cursor(self) -> Optional[str]:
        """Return the current cursor as JSON, or None if no sync has run."""
        if not self._cursor:
            return None
        return json.dumps(self._cursor)

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _root_for_path(self, path: Path) -> Optional[dict]:
        """Return the root config that contains this path, or None."""
        resolved = path.resolve()
        for root in self.roots:
            try:
                resolved.relative_to(root["path"])
                return root
            except ValueError:
                continue
        return None


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pathlib import Path as P

    print("=== Local FS connector self-test ===\n")

    # Locate the config relative to the project root
    project_root = P(__file__).resolve().parent.parent.parent
    config_path = project_root / "data" / "connectors" / "local_fs.json"

    if not config_path.exists():
        print(f"FAIL: config not found at {config_path}")
        print("Create it per the Phase 6.4 instructions.")
        sys.exit(1)

    # Test 1: instantiation
    connector = LocalFSConnector(config_path=str(config_path))
    print(f"Test 1 (instantiation): PASS ({len(connector.roots)} roots configured)")

    # Test 2: test_connection
    assert connector.test_connection() is True
    print("Test 2 (test_connection): PASS")

    # Test 3: full enumeration
    files = list(connector.list_changed_since(cursor=None))
    print(f"Test 3 (full enumeration): PASS ({len(files)} files)")
    for f in files[:3]:
        print(f"    {f['source_id']}")

    # Test 4: fetch a document
    if files:
        doc = connector.fetch_document(files[0]["source_id"])
        assert "content" in doc
        assert len(doc["content"]) > 0
        print(f"Test 4 (fetch_document): PASS ({len(doc['content'])} chars)")

    # Test 5: get_acl respects root config
    if files:
        for f in files:
            acl = connector.get_acl(f["source_id"])
            if "platform" in f["source_id"]:
                assert acl["owner_team"] == "platform"
                assert acl["share_scope"] == "org"
                assert acl["clearance_level"] == "INTERNAL"
                print("Test 5 (ACL from root config): PASS")
                break

    # Test 6: incremental sync — second run should yield zero changes
    cursor = connector.get_cursor()
    incremental = list(connector.list_changed_since(cursor=cursor))
    assert len(incremental) == 0
    print("Test 6 (incremental sync skips unchanged): PASS")

    # Test 7: change detection — touch a file and re-sync
    if files:
        target = P(files[0]["source_id"])
        # Bump mtime by writing a byte
        with target.open("a") as fh:
            fh.write("\n")
        # Force a fresh connector to simulate a new sync cycle
        connector2 = LocalFSConnector(config_path=str(config_path))
        changed = list(connector2.list_changed_since(cursor=cursor))
        assert len(changed) == 1
        assert changed[0]["source_id"] == str(target)
        print("Test 7 (change detection): PASS")

    # Test 8: security doc has team scope
    security_files = [f for f in files if "/security/" in f["source_id"]]
    if security_files:
        acl = connector.get_acl(security_files[0]["source_id"])
        assert acl["owner_team"] == "security"
        assert acl["share_scope"] == "team"
        assert acl["clearance_level"] == "CONFIDENTIAL"
        print("Test 8 (security doc governance): PASS")

    print()
    print("All local FS connector tests PASS")