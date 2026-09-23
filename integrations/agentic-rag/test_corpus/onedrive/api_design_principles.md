# API Design Principles

## Versioning

All public APIs must be versioned. Use path-based versioning: `/v1/`, `/v2/`.

## Idempotency

All POST endpoints that create resources must accept an Idempotency-Key header.

## Pagination

Use cursor-based pagination. Return a `next_cursor` in the response envelope.

## Errors

Return structured errors with a `code`, `message`, and optional `details` array.