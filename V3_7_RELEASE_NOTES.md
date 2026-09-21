# VEYRA v3.7 Release Notes

## Security Graph Intelligence

- Unified read-only graph intelligence view.
- Graph hotspots and chokepoints.
- Correlated attack-path display.
- Control coverage mapping.
- Evidence receipt index.
- Basic drift signals for stale findings, incidents and evidence.
- AI explanation boundary: models may summarize/rank, but persisted telemetry/evidence remains authoritative.
- No new execution or containment bypass.

## Latest recommendations incorporated

The design was reviewed against current NIST CSF 2.0, OWASP Agent Control Standard and 2026 Agentic Applications guidance, MITRE ATLAS, Kyverno, TUF, OpenSSF Scorecard and Inspektor Gadget material.

## Validation

- Backend compile: required.
- v3.7 targeted tests: required.
- Documentation gate: required.
- Full historical suite: report actual pass/fail state; do not claim success if legacy tests remain broken.
