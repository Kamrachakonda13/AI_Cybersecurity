# Security Incident Retrospective

## Incident summary

On August 14, an expired API key was used to access a staging environment.

## Timeline

- 09:15 — Alert fired for anomalous staging access
- 09:22 — On-call engineer acknowledged
- 09:45 — Key rotation completed
- 10:30 — Post-mortem initiated

## Action items

- Enforce automatic key rotation
- Add staging access to anomaly detection
- Document key lifecycle in runbook
