# API Retry Policy

All outbound API calls use exponential backoff with jitter.

- Base delay: 200ms
- Max retries: 3 (4 total attempts)
- Backoff for attempt N: base_delay * 2^(N-1)
- Jitter: uniform in [0.5x, 1.5x]

After 3 failed retries, requests are queued for asynchronous retry.

Idempotency keys are required for POST requests. Keys must be UUIDv4 and are retained for 24 hours.


