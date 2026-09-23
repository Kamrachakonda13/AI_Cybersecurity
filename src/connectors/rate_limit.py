"""
Per-connector rate limiting.

Each connector instance has its own TokenBucket. The bucket is filled at a
configured rate (tokens per second) up to a configured burst capacity. Every
API call consumes one token. If no token is available, the caller blocks
until one is.

This is the classic token bucket algorithm:

    capacity: maximum tokens in the bucket
    refill_rate: tokens per second
    tokens: current token count
    last_refill: timestamp of last refill
"""

import threading
import time
from typing import Optional


class TokenBucket:
    """Thread-safe token bucket rate limiter."""

    def __init__(self, capacity: float, refill_rate: float):
        """
        capacity:    maximum tokens the bucket can hold
        refill_rate: tokens added per second
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self):
        """Add tokens based on elapsed time. Caller must hold the lock."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed > 0:
            added = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + added)
            self.last_refill = now

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        """
        Block until `tokens` tokens are available, or until `timeout` seconds
        have elapsed. Returns True if acquired, False if timed out.
        """
        deadline = None if timeout is None else time.monotonic() + timeout

        while True:
            with self._lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                # Compute how long until enough tokens are available
                needed = tokens - self.tokens
                wait = needed / self.refill_rate

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                wait = min(wait, remaining)

            # Sleep in small increments to allow other threads to acquire
            time.sleep(min(wait, 0.1))

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Non-blocking variant. Returns True if acquired immediately."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def available(self) -> float:
        """Return the current token count (for observability)."""
        with self._lock:
            self._refill()
            return self.tokens


# ---------------------------------------------------------------------------
# Preconfigured rate limits per source system
# ---------------------------------------------------------------------------

# These match real API quotas as of publication:
#   - Google Drive:      ~1000 requests / 100 seconds / user
#   - Microsoft Graph:   ~10000 requests / 10 minutes per app
#   - S3:                ~5500 GET/sec per prefix
#   - Confluence:        ~100 requests / minute / user
#   - Jira:              ~100 requests / minute / user
#   - Slack:             ~1 request / second per method
#   - Local:             effectively unlimited

DEFAULT_RATE_LIMITS = {
    "local_fs":       {"capacity": 1000.0, "refill_rate": 1000.0},  # virtually unlimited
    "s3":             {"capacity": 100.0,  "refill_rate": 50.0},
    "ms_graph":       {"capacity": 50.0,   "refill_rate": 16.0},    # ~10000/10min
    "google_drive":   {"capacity": 20.0,   "refill_rate": 10.0},    # ~1000/100sec
    "sharepoint":     {"capacity": 50.0,   "refill_rate": 16.0},    # uses Graph
    "m365":           {"capacity": 50.0,   "refill_rate": 16.0},    # uses Graph
    "powerbi":        {"capacity": 20.0,   "refill_rate": 10.0},
    "tableau":        {"capacity": 20.0,   "refill_rate": 10.0},
    "confluence":     {"capacity": 5.0,    "refill_rate": 1.7},     # ~100/min
    "jira":           {"capacity": 5.0,    "refill_rate": 1.7},     # ~100/min
    "slack":          {"capacity": 3.0,    "refill_rate": 1.0},
    "notion":         {"capacity": 3.0,    "refill_rate": 3.0},     # 3 req/sec
}


def bucket_for_source(source_system: str) -> TokenBucket:
    """Return a TokenBucket configured for the given source system."""
    config = DEFAULT_RATE_LIMITS.get(source_system)
    if config is None:
        # Safe default for unknown sources
        config = {"capacity": 10.0, "refill_rate": 5.0}
    return TokenBucket(
        capacity=config["capacity"],
        refill_rate=config["refill_rate"],
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Rate limiter self-test ===\n")

    # Test 1: immediate acquisition when bucket is full
    b = TokenBucket(capacity=5.0, refill_rate=1.0)
    assert b.try_acquire() is True
    assert b.try_acquire() is True
    print("Test 1 (immediate acquisition):", "PASS")

    # Test 2: exhaustion
    for _ in range(3):
        b.try_acquire()
    assert b.try_acquire() is False
    print("Test 2 (bucket exhaustion):", "PASS")

    # Test 3: refill over time
    b2 = TokenBucket(capacity=10.0, refill_rate=100.0)
    for _ in range(10):
        b2.try_acquire()
    assert b2.try_acquire() is False
    time.sleep(0.05)  # at 100 tokens/sec, 50ms should add ~5 tokens
    assert b2.try_acquire() is True
    print("Test 3 (refill over time):", "PASS")

    # Test 4: blocking acquire
    b3 = TokenBucket(capacity=1.0, refill_rate=20.0)
    b3.try_acquire()
    t0 = time.monotonic()
    ok = b3.acquire(timeout=1.0)
    elapsed = time.monotonic() - t0
    assert ok is True
    assert 0.02 <= elapsed <= 0.2
    print(f"Test 4 (blocking acquire): PASS  (waited {elapsed*1000:.0f}ms)")

    # Test 5: timeout
    b4 = TokenBucket(capacity=1.0, refill_rate=0.1)
    b4.try_acquire()
    ok = b4.acquire(timeout=0.1)
    assert ok is False
    print("Test 5 (timeout returns False):", "PASS")

    # Test 6: invalid config
    try:
        TokenBucket(capacity=0, refill_rate=1)
        print("Test 6 (invalid config): FAIL — should have raised")
    except ValueError:
        print("Test 6 (invalid config): PASS")

    # Test 7: default rate limits for all known sources
    for source in ["local_fs", "s3", "ms_graph", "google_drive", "sharepoint",
                   "confluence", "jira", "slack", "notion", "powerbi", "tableau"]:
        bucket = bucket_for_source(source)
        assert bucket.capacity > 0
    print("Test 7 (rate limits for all sources):", "PASS")

    print()
    print("Sample rates:")
    for source in ["local_fs", "s3", "ms_graph", "google_drive", "slack"]:
        cfg = DEFAULT_RATE_LIMITS[source]
        print(f"  {source:<15} capacity={cfg['capacity']:>6}  refill={cfg['refill_rate']:>6}/sec")