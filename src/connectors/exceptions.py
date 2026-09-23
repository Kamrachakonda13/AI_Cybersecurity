"""
Exception hierarchy for the connector framework.

Every connector raises one of these exceptions. The pipeline catches them
and decides whether to skip the document, retry, or halt the sync.
"""


class ConnectorError(Exception):
    """Base class for all connector errors."""
    retryable = False

    def __init__(self, message: str, *, source_system: str = None, source_id: str = None):
        super().__init__(message)
        self.source_system = source_system
        self.source_id = source_id

    def to_dict(self) -> dict:
        return {
            "type": type(self).__name__,
            "message": str(self),
            "source_system": self.source_system,
            "source_id": self.source_id,
            "retryable": self.retryable,
        }


class AuthenticationError(ConnectorError):
    """Credentials are invalid, expired, or missing."""
    retryable = False


class AuthorizationError(ConnectorError):
    """Authenticated but not permitted to access this resource."""
    retryable = False


class RateLimitExceeded(ConnectorError):
    """The source API rate limit has been hit."""
    retryable = True

    def __init__(self, message: str, *, retry_after_seconds: float = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds


class TransientError(ConnectorError):
    """Temporary failure: network timeout, 5xx, connection reset."""
    retryable = True


class NotFoundError(ConnectorError):
    """The requested document or path does not exist."""
    retryable = False


class InvalidConfigurationError(ConnectorError):
    """The connector was constructed with bad configuration."""
    retryable = False


class CursorExpiredError(ConnectorError):
    """
    The sync cursor is no longer valid at the source. A full re-sync is required.
    Returned by list_changed_since() when the source has rotated its cursor.
    """
    retryable = False


if __name__ == "__main__":
    # Self-test: exception hierarchy and to_dict
    errs = [
        AuthenticationError("bad credentials", source_system="ms_graph"),
        RateLimitExceeded("too many requests", retry_after_seconds=30.0),
        NotFoundError("no such file", source_system="local_fs", source_id="/tmp/x"),
        TransientError("timeout"),
    ]
    for e in errs:
        d = e.to_dict()
        print(f"{d['type']:<25} retryable={d['retryable']}  message={d['message']}")

    # Verify subclass relationships
    assert issubclass(AuthenticationError, ConnectorError)
    assert issubclass(RateLimitExceeded, ConnectorError)
    assert RateLimitExceeded("x").retryable is True
    assert AuthenticationError("x").retryable is False
    print("\nAll exception hierarchy assertions PASS")