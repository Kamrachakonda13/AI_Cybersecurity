# Platform Deployment Runbook

## Pre-deployment checklist

- All tests passing in CI
- Change approved by a senior engineer
- Rollback plan documented and reviewed
- Change freeze window not in effect

## Deployment steps

1. Merge to `main` branch triggers staging deployment.
2. Verify staging for 15 minutes.
3. Promote to production using blue-green strategy.
4. Monitor error rate and latency for 30 minutes.

## Rollback procedure

If error rate exceeds 1% or p95 latency exceeds 500ms for more than 2 minutes:

    ./scripts/rollback.sh --to-previous

Rollback must complete within 5 minutes.