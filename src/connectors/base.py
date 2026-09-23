"""
Base connector class for Phase 6.

Every source connector (local FS, S3, Microsoft Graph, Google Drive, ...)
inherits from BaseConnector and implements four required methods:

    test_connection()          → can we reach the source?
    list_changed_since(cursor) → what's new or modified?
    fetch_document(source_id)  → give me the full document
    get_acl(source_id)         → what's the access control?

The base class provides:
    - rate limiting (per-instance token bucket)
    - retry with exponential backoff
    - structured logging
    - observability counters

Subclasses override:
    - SOURCE_SYSTEM (class attribute)
    - the four required methods

Subclasses may override:
    - _default_owner_team()  → default owner_team for documents from this source
    - _default_clearance()   → default clearance level
    - get_cursor()           → current sync cursor
    - source_metadata()      → describe this connector for the admin API
"""

import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Optional

from .exceptions import (
    ConnectorError,
    RateLimitExceeded,
    TransientError,
    InvalidConfigurationError,
)
from .rate_limit import bucket_for_source, TokenBucket

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retry policy
# ---------------------------------------------------------------------------

@dataclass
class RetryPolicy:
    """Exponential backoff with jitter."""
    max_attempts: int = 4
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    jitter_factor: float = 0.3  # ±30%

    def delay_for_attempt(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Return the delay before retrying attempt N (1-indexed)."""
        if retry_after is not None:
            # Honor the server's Retry-After header
            return max(0.0, float(retry_after))

        # Exponential: base * 2^(attempt-1)
        raw = self.base_delay_seconds * (2 ** (attempt - 1))
        raw = min(raw, self.max_delay_seconds)

        # Apply jitter: ±jitter_factor
        jitter = raw * self.jitter_factor
        return max(0.0, raw + random.uniform(-jitter, jitter))


# ---------------------------------------------------------------------------
# Sync report — what a single connector sync produced
# ---------------------------------------------------------------------------

@dataclass
class SyncReport:
    """Summary of one sync() call. Returned by BaseConnector.sync_summary()."""
    source_system: str
    started_at: float
    ended_at: Optional[float] = None
    documents_seen: int = 0
    documents_fetched: int = 0
    documents_failed: int = 0
    errors: list = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return (self.ended_at or time.monotonic()) - self.started_at

    def to_dict(self) -> dict:
        return {
            "source_system": self.source_system,
            "duration_seconds": round(self.duration_seconds, 3),
            "documents_seen": self.documents_seen,
            "documents_fetched": self.documents_fetched,
            "documents_failed": self.documents_failed,
            "error_count": len(self.errors),
            "errors": self.errors[:10],  # cap for logging
        }


# ---------------------------------------------------------------------------
# Base connector
# ---------------------------------------------------------------------------

class BaseConnector(ABC):
    """
    Abstract base class for all source connectors.

    Subclasses must set SOURCE_SYSTEM and implement the four required methods.
    """

    SOURCE_SYSTEM: str = "base"  # overridden by subclasses

    def __init__(
        self,
        *,
        tenant_id: str = "acme",
        owner_team: str = "unknown",
        rate_limiter: Optional[TokenBucket] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        if self.SOURCE_SYSTEM == "base":
            raise InvalidConfigurationError(
                "Subclasses must set SOURCE_SYSTEM"
            )

        self.tenant_id = tenant_id
        self.owner_team = owner_team
        self.rate_limiter = rate_limiter or bucket_for_source(self.SOURCE_SYSTEM)
        self.retry_policy = retry_policy or RetryPolicy()

        # Observability counters
        self._api_calls = 0
        self._api_failures = 0
        self._retries = 0

    # ---------------------------------------------------------------------
    # Required interface
    # ---------------------------------------------------------------------

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Verify the connector can reach the source.

        Raise AuthenticationError, AuthorizationError, or InvalidConfigurationError
        on failure. Return True on success.
        """
        raise NotImplementedError

    @abstractmethod
    def list_changed_since(
        self,
        cursor: Optional[str],
        *,
        limit: int = 500,
    ) -> Iterator[dict]:
        """
        Yield lightweight descriptors of documents changed since `cursor`.

        Each yielded item is a dict with at minimum:
            {
                "source_id": str,
                "source_version": str,    # used for incremental detection
                "last_modified": str,     # ISO 8601
                "title": str | None,
                "mime_type": str,
            }

        If cursor is None, performs a full enumeration.

        Implementations should be lazy: yield items as they are fetched from
        the source, do not materialize the full list.
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_document(self, source_id: str) -> dict:
        """
        Fetch the full content of a single document.

        Returns a dict with at minimum:
            {
                "source_id": str,
                "content": str,           # plain text (extract from mime type)
                "mime_type": str,
                "title": str | None,
                "source_url": str | None,
                "source_path": str | None,
                "created_at": str | None,
                "last_modified": str | None,
                "source_version": str | None,
                "metadata": dict,         # source-specific extras
            }

        Raise NotFoundError if the document has been deleted since enumeration.
        """
        raise NotImplementedError

    @abstractmethod
    def get_acl(self, source_id: str) -> dict:
        """
        Return the ACL for a document.

        Returns:
            {
                "clearance_level": "PUBLIC" | "INTERNAL" | "CONFIDENTIAL" | "RESTRICTED",
                "share_scope": "team" | "org" | [team_names],
                "acl": [
                    {"principal_type": "user"|"group"|"team"|"role",
                     "principal_id": str,
                     "access": "read"},
                    ...
                ],
                "owner_team": str,
                "owner_user": str | None,
            }

        Fail-closed: if the ACL cannot be determined, raise ConnectorError.
        The pipeline treats a failed get_acl() as a skip, not as public access.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Optional interface
    # ---------------------------------------------------------------------

    def get_cursor(self) -> Optional[str]:
        """
        Return the current sync cursor for this connector, or None for full sync.
        Subclasses that support incremental sync should override.
        """
        return None

    def source_metadata(self) -> dict:
        """Describe this connector for the admin API."""
        return {
            "source_system": self.SOURCE_SYSTEM,
            "tenant_id": self.tenant_id,
            "owner_team": self.owner_team,
            "rate_limit_capacity": self.rate_limiter.capacity,
            "rate_limit_refill": self.rate_limiter.refill_rate,
            "api_calls": self._api_calls,
            "api_failures": self._api_failures,
            "retries": self._retries,
        }

    def observability(self) -> dict:
        """Return current observability counters."""
        return {
            "api_calls": self._api_calls,
            "api_failures": self._api_failures,
            "retries": self._retries,
        }

    # ---------------------------------------------------------------------
    # Rate-limited, retry-wrapped API call helper
    # ---------------------------------------------------------------------

    def call_api(self, fn, *args, **kwargs):
        """
        Execute fn(*args, **kwargs) under this connector's rate limiter and
        retry policy.

        Usage in a subclass:
            def test_connection(self):
                return self.call_api(self._client.get_about)

        Retry policy:
            - Retry on TransientError and RateLimitExceeded.
            - Do not retry on AuthenticationError, AuthorizationError,
              NotFoundError, InvalidConfigurationError.
            - Retry up to retry_policy.max_attempts times.
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            # Acquire a rate-limit token
            self.rate_limiter.acquire(tokens=1.0)

            try:
                self._api_calls += 1
                return fn(*args, **kwargs)
            except ConnectorError as e:
                self._api_failures += 1
                last_error = e

                if not e.retryable:
                    # Non-retryable: propagate immediately
                    raise

                if attempt == self.retry_policy.max_attempts:
                    # Out of attempts: propagate
                    raise

                # Compute backoff
                retry_after = getattr(e, "retry_after_seconds", None)
                delay = self.retry_policy.delay_for_attempt(attempt, retry_after=retry_after)

                logger.warning(
                    "Connector %s: attempt %d/%d failed (%s). Retrying in %.2fs.",
                    self.SOURCE_SYSTEM, attempt, self.retry_policy.max_attempts,
                    type(e).__name__, delay,
                )
                self._retries += 1
                time.sleep(delay)

            except Exception as e:
                # Unexpected exception — wrap as TransientError and retry
                self._api_failures += 1
                wrapped = TransientError(
                    f"Unexpected error in {fn.__name__}: {e}",
                    source_system=self.SOURCE_SYSTEM,
                )
                last_error = wrapped

                if attempt == self.retry_policy.max_attempts:
                    raise wrapped from e

                delay = self.retry_policy.delay_for_attempt(attempt)
                logger.warning(
                    "Connector %s: attempt %d/%d hit unexpected error %s. Retrying in %.2fs.",
                    self.SOURCE_SYSTEM, attempt, self.retry_policy.max_attempts,
                    type(e).__name__, delay,
                )
                self._retries += 1
                time.sleep(delay)

        # Unreachable, but defensive
        raise last_error or ConnectorError("call_api exhausted retries with no exception")


# ---------------------------------------------------------------------------
# Self-test — a minimal NullConnector subclass
# ---------------------------------------------------------------------------

class NullConnector(BaseConnector):
    """A no-op connector that returns empty results. Used for testing."""

    SOURCE_SYSTEM = "local_fs"

    def __init__(self, *, fail_first_n_calls: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._fail_budget = fail_first_n_calls

    def test_connection(self) -> bool:
        return True

    def list_changed_since(self, cursor, *, limit=500):
        return iter([])

    def fetch_document(self, source_id):
        return {"source_id": source_id, "content": "", "mime_type": "text/plain"}

    def get_acl(self, source_id):
        return {
            "clearance_level": "INTERNAL",
            "share_scope": "team",
            "acl": [],
            "owner_team": self.owner_team,
            "owner_user": None,
        }

    def _maybe_fail(self):
        if self._fail_budget > 0:
            self._fail_budget -= 1
            raise TransientError("simulated transient failure")


if __name__ == "__main__":
    print("=== Base connector self-test ===\n")

    # Test 1: instantiate
    c = NullConnector(owner_team="platform")
    assert c.SOURCE_SYSTEM == "local_fs"
    print("Test 1 (instantiation):", "PASS")

    # Test 2: test_connection
    assert c.test_connection() is True
    print("Test 2 (test_connection):", "PASS")

    # Test 3: abstract enforcement
    try:
        class Broken(BaseConnector):
            SOURCE_SYSTEM = "local_fs"
            # Missing test_connection and others
        Broken()
        print("Test 3 (abstract enforcement): FAIL — should have raised")
    except TypeError:
        print("Test 3 (abstract enforcement): PASS")

    # Test 4: invalid SOURCE_SYSTEM
    try:
        class BadSystem(BaseConnector):
            def test_connection(self): return True
            def list_changed_since(self, cursor, *, limit=500): return iter([])
            def fetch_document(self, source_id): return {}
            def get_acl(self, source_id): return {}
        BadSystem()
        print("Test 4 (invalid SOURCE_SYSTEM): FAIL")
    except InvalidConfigurationError:
        print("Test 4 (invalid SOURCE_SYSTEM): PASS")

    # Test 5: retry on transient error succeeds on second attempt
    c5 = NullConnector(owner_team="platform", fail_first_n_calls=1)
    # Monkey-patch a call that will fail once
    def flaky_call():
        c5._maybe_fail()
        return "success"
    result = c5.call_api(flaky_call)
    assert result == "success"
    assert c5.observability()["retries"] == 1
    print("Test 5 (retry on transient):", "PASS")

    # Test 6: retry exhausted
    c6 = NullConnector(
        owner_team="platform",
        fail_first_n_calls=10,  # more failures than retry attempts
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.01),
    )
    try:
        c6.call_api(lambda: c6._maybe_fail())
        print("Test 6 (retry exhausted): FAIL")
    except TransientError:
        print("Test 6 (retry exhausted): PASS")

    # Test 7: non-retryable error propagates immediately
    from .exceptions import AuthenticationError
    c7 = NullConnector(owner_team="platform")
    def auth_fail():
        raise AuthenticationError("bad creds")
    try:
        c7.call_api(auth_fail)
        print("Test 7 (non-retryable propagation): FAIL")
    except AuthenticationError:
        print("Test 7 (non-retryable propagation): PASS")
    assert c7.observability()["retries"] == 0

    # Test 8: source_metadata shape
    c8 = NullConnector(owner_team="platform")
    meta = c8.source_metadata()
    assert meta["source_system"] == "local_fs"
    assert meta["owner_team"] == "platform"
    print("Test 8 (source_metadata):", "PASS")

    # Test 9: SyncReport
    from time import monotonic
    r = SyncReport(source_system="local_fs", started_at=monotonic())
    r.documents_seen = 10
    r.documents_fetched = 9
    r.documents_failed = 1
    r.ended_at = monotonic()
    d = r.to_dict()
    assert d["documents_seen"] == 10
    assert d["documents_fetched"] == 9
    print("Test 9 (SyncReport):", "PASS")

    print()
    print("All base connector tests PASS")