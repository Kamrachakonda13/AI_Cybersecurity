"""
PDF filesystem connector for Phase 7.

Walks configured directories, extracts text from PDF files using pypdf, and
emits unified documents compatible with the Phase 6 pipeline.

Configuration is identical to the local_fs connector:
    {
      "connector_type": "pdf_fs",
      "tenant_id": "acme",
      "roots": [
        {"path": "/path/to/pdfs", "owner_team": "...",
         "clearance_level": "INTERNAL", "share_scope": "org"}
      ]
    }

Incremental sync uses mtime + size, same as the local FS connector.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .base import BaseConnector
from .exceptions import (
    InvalidConfigurationError,
    NotFoundError,
    TransientError,
)


class PDFFSConnector(BaseConnector):
    SOURCE_SYSTEM = "pdf_fs"

    def __init__(self, *, config_path: str, **kwargs):
        super().__init__(tenant_id="acme", owner_team="unknown", **kwargs)

        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise InvalidConfigurationError(
                f"Config not found: {self.config_path}",
                source_system=self.SOURCE_SYSTEM,
            )

        config = json.loads(self.config_path.read_text())
        self.tenant_id = config.get("tenant_id", "acme")

        self.roots = []
        for root_cfg in config.get("roots", []):
            root_path = Path(root_cfg["path"]).resolve()
            if not root_path.exists() or not root_path.is_dir():
                raise InvalidConfigurationError(
                    f"Root not found: {root_path}",
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
                "No roots configured",
                source_system=self.SOURCE_SYSTEM,
            )

        self._cursor: dict = {}

    def test_connection(self) -> bool:
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
        previous = {}
        if cursor:
            try:
                previous = json.loads(cursor)
            except json.JSONDecodeError:
                previous = {}

        yielded = 0
        for root in self.roots:
            for pdf_path in sorted(root["path"].rglob("*.pdf")):
                if yielded >= limit:
                    return
                if not pdf_path.is_file():
                    continue

                stat = pdf_path.stat()
                abs_str = str(pdf_path)
                mtime = stat.st_mtime
                size = stat.st_size
                version = f"{int(mtime)}-{size}"

                prev = previous.get(abs_str)
                if prev and prev.get("version") == version:
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
                    "last_modified": datetime.fromtimestamp(
                        mtime, tz=timezone.utc
                    ).isoformat(),
                    "title": pdf_path.stem,
                    "mime_type": "application/pdf",
                }
                yielded += 1

    def fetch_document(self, source_id: str) -> dict:
        path = Path(source_id)
        if not path.exists() or not path.is_file():
            raise NotFoundError(
                f"PDF not found: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        root = self._root_for_path(path)
        if root is None:
            raise NotFoundError(
                f"PDF outside configured roots: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        try:
            reader = PdfReader(str(path))
            pages = []
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        pages.append(f"[Page {i + 1}]\n{text.strip()}")
                except Exception:
                    continue
            content = "\n\n".join(pages)
        except PdfReadError as e:
            raise TransientError(
                f"Failed to read PDF {source_id}: {e}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        if not content.strip():
            raise TransientError(
                f"No extractable text in PDF {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        stat = path.stat()

        return {
            "source_id": str(path),
            "content": content,
            "mime_type": "application/pdf",
            "title": path.stem,
            "source_url": f"file://{path}",
            "source_path": str(path.relative_to(root["path"])),
            "created_at": datetime.fromtimestamp(
                stat.st_ctime, tz=timezone.utc
            ).isoformat(),
            "last_modified": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat(),
            "source_version": f"{int(stat.st_mtime)}-{stat.st_size}",
            "metadata": {
                "page_count": len(reader.pages),
                "root_path": str(root["path"]),
            },
        }

    def get_acl(self, source_id: str) -> dict:
        path = Path(source_id)
        root = self._root_for_path(path)
        if root is None:
            raise NotFoundError(
                f"PDF outside configured roots: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )
        return {
            "clearance_level": root["clearance_level"],
            "share_scope": root["share_scope"],
            "acl": list(root.get("acl", [])),
            "owner_team": root["owner_team"],
            "owner_user": root.get("owner_user"),
        }

    def get_cursor(self) -> Optional[str]:
        if not self._cursor:
            return None
        return json.dumps(self._cursor)

    def _root_for_path(self, path: Path) -> Optional[dict]:
        resolved = path.resolve()
        for root in self.roots:
            try:
                resolved.relative_to(root["path"])
                return root
            except ValueError:
                continue
        return None


if __name__ == "__main__":
    print("=== PDF connector self-test ===\n")
    import sys as _sys
    from pathlib import Path as _P

    project_root = _P(__file__).resolve().parent.parent.parent
    config_path = project_root / "data" / "connectors" / "pdf_fs.json"

    if not config_path.exists():
        print(f"FAIL: config not found at {config_path}")
        _sys.exit(1)

    c = PDFFSConnector(config_path=str(config_path))
    print(f"Test 1 (instantiation): PASS ({len(c.roots)} roots)")

    assert c.test_connection() is True
    print("Test 2 (test_connection): PASS")

    files = list(c.list_changed_since(cursor=None))
    print(f"Test 3 (enumeration): PASS ({len(files)} PDFs)")
    for f in files:
        print(f"    {Path(f['source_id']).name}")

    if files:
        doc = c.fetch_document(files[0]["source_id"])
        print(f"Test 4 (fetch_document): PASS ({len(doc['content'])} chars)")
        print(f"    First 100: {doc['content'][:100]!r}")

        acl = c.get_acl(files[0]["source_id"])
        print(f"Test 5 (ACL): PASS team={acl['owner_team']} clearance={acl['clearance_level']}")

    cursor = c.get_cursor()
    inc = list(c.list_changed_since(cursor=cursor))
    assert len(inc) == 0
    print("Test 6 (incremental sync): PASS")

    print()
    print("All PDF connector tests PASS")
