"""
S3 / MinIO connector for Phase 6.

Reads text documents from S3-compatible object storage. Works with:
    - MinIO (local dev)
    - AWS S3
    - Any S3-compatible storage (Cloudflare R2, Backblaze B2, Wasabi, ...)

Incremental sync:
    Version = ETag + size. If both unchanged, skip.

Security:
    Credentials are read from environment variables named in the config.
    Never store credentials in the config file itself.
"""

import json
import os
from datetime import timezone
from pathlib import Path
from typing import Iterator, Optional

import boto3
from botocore.client import Config as BotoConfig
from dotenv import load_dotenv
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
)

from .base import BaseConnector
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidConfigurationError,
    NotFoundError,
    TransientError,
)


load_dotenv()


TEXT_CONTENT_TYPES = {
    "text/plain", "text/markdown", "text/csv", "text/html", "text/xml",
    "application/json", "application/yaml", "application/x-yaml", "application/xml",
    "application/x-ndjson", "application/ld+json",
}


class S3Connector(BaseConnector):
    """S3-compatible object storage connector."""

    SOURCE_SYSTEM = "s3"

    def __init__(
        self,
        *,
        config_path: str,
        tenant_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            tenant_id=tenant_id or "acme",
            owner_team="unknown",
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
        # Endpoint resolution priority:
        # 1. Explicit config value (rare)
        # 2. MINIO_ENDPOINT environment variable (used by Docker Compose)
        # 3. AWS default (if neither is set)
        self.endpoint_url = (
            config.get("endpoint_url")
            or os.getenv("MINIO_ENDPOINT")
        )
        self.region = config.get("region", "us-east-1")

        access_key = os.getenv(config.get("access_key_env", "MINIO_ACCESS_KEY"))
        secret_key = os.getenv(config.get("secret_key_env", "MINIO_SECRET_KEY"))

        if not access_key or not secret_key:
            raise AuthenticationError(
                f"Missing credentials. Set {config.get('access_key_env')} "
                f"and {config.get('secret_key_env')} in the environment.",
                source_system=self.SOURCE_SYSTEM,
            )

        self._client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=BotoConfig(signature_version="s3v4"),
            region_name=self.region,
        )

        self.buckets = []
        for bucket_cfg in config.get("buckets", []):
            self.buckets.append({
                "name": bucket_cfg["name"],
                "owner_team": bucket_cfg.get("owner_team", "unknown"),
                "clearance_level": bucket_cfg.get("clearance_level", "INTERNAL"),
                "share_scope": bucket_cfg.get("share_scope", "team"),
                "owner_user": bucket_cfg.get("owner_user"),
                "acl": bucket_cfg.get("acl", []),
                "prefix_governance": bucket_cfg.get("prefix_governance", {}),
            })

        if not self.buckets:
            raise InvalidConfigurationError(
                "No buckets configured",
                source_system=self.SOURCE_SYSTEM,
            )

        self._cursor: dict = {}

    # ---------------------------------------------------------------------
    # Required interface
    # ---------------------------------------------------------------------

    def test_connection(self) -> bool:
        try:
            for bucket in self.buckets:
                self._client.head_bucket(Bucket=bucket["name"])
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("404", "NoSuchBucket"):
                raise NotFoundError(
                    f"Bucket not found: {bucket['name']}",
                    source_system=self.SOURCE_SYSTEM,
                )
            if code in ("403", "AccessDenied"):
                raise AuthorizationError(
                    f"Access denied to bucket: {bucket['name']}",
                    source_system=self.SOURCE_SYSTEM,
                )
            raise TransientError(
                f"Failed to reach S3: {e}",
                source_system=self.SOURCE_SYSTEM,
            )
        except EndpointConnectionError as e:
            raise TransientError(
                f"Cannot reach endpoint {self.endpoint_url}: {e}",
                source_system=self.SOURCE_SYSTEM,
            )
        except NoCredentialsError as e:
            raise AuthenticationError(
                f"No credentials: {e}",
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
        for bucket in self.buckets:
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket["name"]):
                for obj in page.get("Contents", []):
                    if yielded >= limit:
                        return
                    key = obj["Key"]
                    if key.endswith("/"):
                        continue

                    etag = obj["ETag"].strip('"')
                    size = obj["Size"]
                    version = f"{etag}-{size}"
                    source_id = f"{bucket['name']}/{key}"

                    prev = previous.get(source_id)
                    if prev and prev.get("version") == version:
                        self._cursor[source_id] = prev
                        continue

                    self._cursor[source_id] = {
                        "version": version,
                        "etag": etag,
                        "size": size,
                    }

                    yield {
                        "source_id": source_id,
                        "source_version": version,
                        "last_modified": obj["LastModified"].astimezone(timezone.utc).isoformat(),
                        "title": Path(key).stem,
                        "mime_type": self._guess_content_type(key),
                    }
                    yielded += 1

    def fetch_document(self, source_id: str) -> dict:
        if "/" not in source_id:
            raise NotFoundError(
                f"Malformed source_id (expected bucket/key): {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        bucket_name, key = source_id.split("/", 1)

        try:
            response = self._client.get_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("NoSuchKey", "404"):
                raise NotFoundError(
                    f"Object not found: {source_id}",
                    source_system=self.SOURCE_SYSTEM,
                    source_id=source_id,
                )
            raise TransientError(
                f"Failed to fetch {source_id}: {e}",
                source_system=self.SOURCE_SYSTEM,
            )

        body = response["Body"].read()
        content_type = response.get("ContentType", "application/octet-stream")

        content = body.decode("utf-8", errors="replace")

        return {
            "source_id": source_id,
            "content": content,
            "mime_type": content_type,
            "title": Path(key).stem,
            "source_url": f"s3://{bucket_name}/{key}",
            "source_path": key,
            "created_at": None,
            "last_modified": response["LastModified"].astimezone(timezone.utc).isoformat(),
            "source_version": f"{response['ETag'].strip(chr(34))}-{response['ContentLength']}",
            "metadata": {
                "bucket": bucket_name,
                "key": key,
                "etag": response["ETag"].strip('"'),
            },
        }

    def get_acl(self, source_id: str) -> dict:
        if "/" not in source_id:
            raise NotFoundError(
                f"Malformed source_id: {source_id}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        bucket_name, key = source_id.split("/", 1)
        bucket_cfg = next((b for b in self.buckets if b["name"] == bucket_name), None)
        if not bucket_cfg:
            raise NotFoundError(
                f"Bucket not configured: {bucket_name}",
                source_system=self.SOURCE_SYSTEM,
                source_id=source_id,
            )

        acl = {
            "clearance_level": bucket_cfg["clearance_level"],
            "share_scope": bucket_cfg["share_scope"],
            "acl": list(bucket_cfg.get("acl", [])),
            "owner_team": bucket_cfg["owner_team"],
            "owner_user": bucket_cfg.get("owner_user"),
        }

        best_prefix = None
        for prefix, override in bucket_cfg.get("prefix_governance", {}).items():
            if key.startswith(prefix):
                if best_prefix is None or len(prefix) > len(best_prefix):
                    best_prefix = prefix
                    for k in ("clearance_level", "share_scope", "owner_team", "owner_user"):
                        if k in override:
                            acl[k] = override[k]
                    if "acl" in override:
                        acl["acl"] = override["acl"]

        return acl

    def get_cursor(self) -> Optional[str]:
        if not self._cursor:
            return None
        return json.dumps(self._cursor)

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _guess_content_type(self, key: str) -> str:
        ext = Path(key).suffix.lower()
        mapping = {
            ".md": "text/markdown",
            ".txt": "text/plain",
            ".json": "application/json",
            ".yaml": "application/yaml",
            ".yml": "application/yaml",
            ".csv": "text/csv",
            ".html": "text/html",
            ".xml": "application/xml",
        }
        return mapping.get(ext, "application/octet-stream")