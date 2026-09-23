# Deployment Procedures

Production deployments require approval from at least one senior engineer and pass all automated tests in the staging environment. Deployments are blocked during change freeze windows, which include the last 3 business days of each quarter.

Deployments use blue-green strategy. The new version receives 1% of traffic for 5 minutes, then 10% for 10 minutes, then 50% for 10 minutes, then 100%. Rollback is automatic if error rate exceeds 1% or latency p95 exceeds 500ms at any stage.

Database migrations are applied separately from code deployments and must be backward-compatible with the previous version. Destructive migrations (column drops, table drops) are forbidden; deprecated columns are renamed with a `_deprecated_` prefix and dropped 30 days later.

All deployments are logged with the deploying engineer, commit SHA, and rollback plan. Rollback must be executable within 5 minutes by any on-call engineer without the original deployer's involvement.