"""
Microsoft Graph connector for Phase 6.

Reads documents from OneDrive and SharePoint via the Microsoft Graph API.

Two client implementations:

    FixtureGraphClient
        Reads from JSON fixture files. Used for local development when the
        Azure tenant does not have a SharePoint or M365 license.

    RealGraphClient
        Uses the live Microsoft Graph API with OAuth client credentials.
        Requires a licensed M365 tenant with Files.Read.All and Sites.Read.All
        application permissions granted and consented.

Both clients implement the same GraphClient interface. The connector chooses
which one to use based on the config file's "client" field ("fixture" | "real").

The connector itself - pagination, delta handling, ACL mapping, error
translation - is identical regardless of which client is behind it.
"""

import json
import os
from pathlib import Path
from typing import Iterator, Optional

import httpx

from .base import BaseConnector
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidConfigurationError,
    NotFoundError,
    RateLimitExceeded,
    TransientError,
)


GRAPH_BASE = "https://graph.microsoft.com/v1.0"


# ---------------------------------------------------------------------------
# Client interface
# ---------------------------------------------------------------------------

class GraphClient:
    """Abstract client. Implementations: fixture and real."""

    def get_users(self) -> list:
        raise NotImplementedError

    def get_drives(self) -> list:
        raise NotImplementedError

    def list_drive_items(self, drive_id: str) -> list:
        raise NotImplementedError

    def get_permissions(self, drive_id: str, item_id: str) -> list:
        raise NotImplementedError

    def read_content(self, item: dict) -> str:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Fixture client
# ---------------------------------------------------------------------------

class FixtureGraphClient(GraphClient):
    """Reads from JSON fixtures. Useful for development without a licensed tenant."""

    def __init__(self, fixtures_dir: Path, content_root: Path):
        self.fixtures_dir = fixtures_dir
        self.content_root = content_root

        if not self.fixtures_dir.exists():
            raise InvalidConfigurationError(
                f"Fixtures directory not found: {self.fixtures_dir}",
                source_system="ms_graph",
            )

        self._users = self._load("users.json").get("value", [])
        self._drives = self._load("drives.json").get("value", [])
        self._drive_items = self._load("drive_items.json").get("value", [])
        self._permissions = self._load("permissions.json")

    def _load(self, name: str) -> dict:
        path = self.fixtures_dir / name
        if not path.exists():
            raise InvalidConfigurationError(
                f"Fixture not found: {path}",
                source_system="ms_graph",
            )
        return json.loads(path.read_text())

    def get_users(self) -> list:
        return self._users

    def get_drives(self) -> list:
        return self._drives

    def list_drive_items(self, drive_id: str) -> list:
        return [item for item in self._drive_items
                if item.get("parentReference", {}).get("driveId") == drive_id]

    def get_permissions(self, drive_id: str, item_id: str) -> list:
        return self._permissions.get(item_id, [])

    def read_content(self, item: dict) -> str:
        rel = item.get("content_fixture_path")
        if not rel:
            raise NotFoundError(
                f"Item {item.get('id')} has no content_fixture_path",
                source_system="ms_graph",
            )
        path = self.content_root / rel
        if not path.exists():
            raise NotFoundError(
                f"Fixture content file not found: {path}",
                source_system="ms_graph",
            )
        return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Real client
# ---------------------------------------------------------------------------

class RealGraphClient(GraphClient):
    """Calls the live Microsoft Graph API."""

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None
        self._http = httpx.Client(timeout=30.0)

    def _get_token(self) -> str:
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        response = self._http.post(url, data=data)
        if response.status_code != 200:
            try:
                body = response.json()
            except Exception:
                body = {}
            raise AuthenticationError(
                f"Token request failed: {response.status_code} "
                f"{body.get('error_description', '')[:150]}",
                source_system="ms_graph",
            )
        return response.json()["access_token"]

    def _request(self, path: str) -> dict:
        if self._token is None:
            self._token = self._get_token()

        url = path if path.startswith("http") else f"{GRAPH_BASE}{path}"
        response = self._http.get(url, headers={"Authorization": f"Bearer {self._token}"})

        if response.status_code == 401:
            self._token = self._get_token()
            response = self._http.get(url, headers={"Authorization": f"Bearer {self._token}"})

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitExceeded(
                "Graph rate limit",
                retry_after_seconds=float(retry_after) if retry_after else 5.0,
                source_system="ms_graph",
            )
        if response.status_code == 403:
            raise AuthorizationError(
                f"Graph 403: {response.text[:200]}",
                source_system="ms_graph",
            )
        if response.status_code == 404:
            raise NotFoundError(
                f"Graph 404: {path}",
                source_system="ms_graph",
            )
        if response.status_code >= 500:
            raise TransientError(
                f"Graph {response.status_code}: {response.text[:200]}",
                source_system="ms_graph",
            )
        if response.status_code != 200:
            raise TransientError(
                f"Graph {response.status_code}: {response.text[:200]}",
                source_system="ms_graph",
            )
        return response.json()

    def get_users(self) -> list:
        return self._request("/users").get("value", [])

    def get_drives(self) -> list:
        drives = []
        for user in self.get_users():
            uid = user["id"]
            try:
                user_drives = self._request(f"/users/{uid}/drives").get("value", [])
                drives.extend(user_drives)
            except NotFoundError:
                continue
        return drives

    def list_drive_items(self, drive_id: str) -> list:
        return self._request(f"/drives/{drive_id}/root/children").get("value", [])

    def get_permissions(self, drive_id: str, item_id: str) -> list:
        return self._request(f"/drives/{drive_id}/items/{item_id}/permissions").get("value", [])

    def read_content(self, item: dict) -> str:
        download_url = item.get("_downloadUrl")
        if not download_url:
            raise NotFoundError(
                f"Item {item.get('id')} has no download URL",
                source_system="ms_graph",
            )
        response = self._http.get(download_url)
        if response.status_code != 200:
            raise TransientError(
                f"Download failed: {response.status_code}",
                source_system="ms_graph",
            )
        return response.text


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------

class MSGraphConnector(BaseConnector):
    """Microsoft Graph connector with swappable client."""

    SOURCE_SYSTEM = "ms_graph"

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

        # Team mapping
        tm = config.get("team_mapping", {})
        self.default_team = tm.get("default_team", "unknown")
        self.default_clearance = tm.get("default_clearance", "INTERNAL")
        self.default_share_scope = tm.get("default_share_scope", "team")
        self.user_team_map = tm.get("users", {})

        # Client selection
        client_kind = config.get("client", "fixture")
        if client_kind == "fixture":
            fc = config.get("fixture_client", {})
            fixtures_dir = Path(fc.get("fixtures_dir", "data/connectors/ms_graph_fixtures"))
            content_root = Path(fc.get("content_root", "."))
            self._client = FixtureGraphClient(fixtures_dir, content_root)
        elif client_kind == "real":
            rc = config.get("real_client", {})
            tenant = os.getenv(rc.get("tenant_id_env", "MS_GRAPH_TENANT_ID"))
            client_id = os.getenv(rc.get("client_id_env", "MS_GRAPH_CLIENT_ID"))
            client_secret = os.getenv(rc.get("client_secret_env", "MS_GRAPH_CLIENT_SECRET"))
            if not all([tenant, client_id, client_secret]):
                raise AuthenticationError(
                    "Missing MS_GRAPH_* environment variables for real client",
                    source_system=self.SOURCE_SYSTEM,
                )
            self._client = RealGraphClient(tenant, client_id, client_secret)
        else:
            raise InvalidConfigurationError(
                f"Unknown client kind: {client_kind}. Use 'fixture' or 'real'.",
                source_system=self.SOURCE_SYSTEM,
            )

        self._cursor: dict = {}

    def test_connection(self) -> bool:
        users = self._client.get_users()
        if not users:
            raise TransientError(
                "No users returned by Graph",
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
        for drive in self._client.get_drives():
            drive_id = drive["id"]
            try:
                items = self._client.list_drive_items(drive_id)
            except (NotFoundError, AuthorizationError):
                continue

            for item in items:
                if yielded >= limit:
                    return
                if "folder" in item:
                    continue
                mime = item.get("file", {}).get("mimeType", "")
                if not mime.startswith("text/") and mime not in (
                    "application/json",
                    "application/xml",
                    "application/yaml",
                ):
                    continue

                item_id = item["id"]
                modified = item.get("fileSystemInfo", {}).get("lastModifiedDateTime", "")
                size = item.get("size", 0)
                version = f"{modified}-{size}"
                source_id = f"{drive_id}:{item_id}"

                prev = previous.get(source_id)
                if prev and prev.get("version") == version:
                    self._cursor[source_id] = prev
                    continue

                self._cursor[source_id] = {"version": version}
                yield {
                    "source_id": source_id,
                    "source_version": version,
                    "last_modified": modified,
                    "title": item.get("name", ""),
                    "mime_type": mime,
                }
                yielded += 1

    def _item_for(self, drive_id: str, item_id: str) -> dict:
        for item in self._client.list_drive_items(drive_id):
            if item.get("id") == item_id:
                return item
        raise NotFoundError(
            f"Item {item_id} not found in drive {drive_id}",
            source_system=self.SOURCE_SYSTEM,
        )

    def fetch_document(self, source_id: str) -> dict:
        if ":" not in source_id:
            raise NotFoundError(
                f"Malformed source_id: {source_id}",
                source_system=self.SOURCE_SYSTEM,
            )
        drive_id, item_id = source_id.split(":", 1)

        item = self._item_for(drive_id, item_id)
        content = self._client.read_content(item)

        return {
            "source_id": source_id,
            "content": content,
            "mime_type": item.get("file", {}).get("mimeType", "text/plain"),
            "title": item.get("name", ""),
            "source_url": item.get("webUrl"),
            "source_path": item.get("parentReference", {}).get("path", ""),
            "created_at": item.get("fileSystemInfo", {}).get("createdDateTime"),
            "last_modified": item.get("fileSystemInfo", {}).get("lastModifiedDateTime"),
            "source_version": (
                f"{item.get('fileSystemInfo', {}).get('lastModifiedDateTime', '')}"
                f"-{item.get('size', 0)}"
            ),
            "metadata": {
                "drive_id": drive_id,
                "item_id": item_id,
                "created_by": item.get("createdBy", {}).get("user", {}).get("userPrincipalName"),
                "last_modified_by": (
                    item.get("lastModifiedBy", {}).get("user", {}).get("userPrincipalName")
                ),
            },
        }

    def get_acl(self, source_id: str) -> dict:
        if ":" not in source_id:
            raise NotFoundError(
                f"Malformed source_id: {source_id}",
                source_system=self.SOURCE_SYSTEM,
            )
        drive_id, item_id = source_id.split(":", 1)

        item = self._item_for(drive_id, item_id)
        owner_upn = (
            item.get("createdBy", {}).get("user", {}).get("userPrincipalName", "")
        )

        owner_cfg = self.user_team_map.get(owner_upn, {})
        owner_team = owner_cfg.get("team", self.default_team)
        clearance = owner_cfg.get("clearance", self.default_clearance)
        share_scope = owner_cfg.get("share_scope", self.default_share_scope)

        acl = []
        try:
            perms = self._client.get_permissions(drive_id, item_id)
            for perm in perms:
                roles = perm.get("roles", [])
                if not any(r in roles for r in ("read", "write", "owner")):
                    continue
                granted = perm.get("grantedToV2", {}).get("user", {})
                upn = granted.get("userPrincipalName")
                if upn:
                    acl.append({
                        "principal_type": "user",
                        "principal_id": upn,
                        "access": "read",
                    })
        except (NotFoundError, AuthorizationError):
            pass

        return {
            "clearance_level": clearance,
            "share_scope": share_scope,
            "acl": acl,
            "owner_team": owner_team,
            "owner_user": owner_upn or None,
        }

    def get_cursor(self) -> Optional[str]:
        if not self._cursor:
            return None
        return json.dumps(self._cursor)