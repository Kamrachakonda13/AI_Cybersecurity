# Retry Policy for API Calls

All outbound API calls use exponential backoff with jitter. The base delay is 200 milliseconds. Maximum retries are 3 attempts after the initial call, giving 4 total attempts.

Backoff delay for attempt N is calculated as base_delay * 2^(N-1), with jitter applied uniformly in the range [0.5x, 1.5x] of the computed delay. This prevents retry storms when a downstream service recovers.

After 3 failed retries, the request is placed on an asynchronous retry queue with a maximum delay of 1 hour. Permanent failures (any 4xx response other than 408 and 429) are never retried.

Idempotency keys are required for all POST requests to prevent duplicate operations during retries. Idempotency keys must be UUIDv4 and are retained for 24 hours.

Circuit breakers open after 20 consecutive failures to a downstream service and remain open for 60 seconds before allowing a single probe request.