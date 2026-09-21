# VEYRA v3.5 — Security Lifecycle

## Purpose

VEYRA v3.5 turns the platform into a continuous security operating model:

**Discover → Understand → Validate → Investigate → Correlate → Contain → Recover → Prove → Learn → Continuously revalidate.**

The lifecycle is a control-plane and evidence model. It does not execute arbitrary security commands and does not provide hack-back.

## Stage guide

| Stage | Team question | Typical evidence |
|---|---|---|
| Discover | What exists? | assets, services, AI assets |
| Understand | What is normal and important? | ownership, criticality, dependencies |
| Validate | Do controls work? | scoped test results |
| Investigate | What happened? | timelines, endpoint/AI traces |
| Correlate | How is it connected? | graph links, threat intel |
| Contain | How do we stop impact? | approved containment receipt |
| Recover | Is trusted state restored? | recovery verification |
| Prove | Can we demonstrate it? | hashes, provenance, attestations |
| Learn | What should change? | detections, remediation, training |
| Revalidate | Did the fix remain effective? | schedules, drift comparisons |

## UI

Open **Security Lifecycle** in the VEYRA console. Review the stage status and current plan. An `ATTENTION` stage should be addressed before lower-priority work.

## API

- `GET /api/v35/lifecycle/overview`
- `GET /api/v35/lifecycle/plan`
- `GET /api/v35/lifecycle/plan?focus=investigate`

## Terminal

The lifecycle API is intentionally plan-only. Use it to inspect readiness from an authenticated administration environment:

```bash
curl -H "Authorization: Bearer $AEGISX_TOKEN" \
  "$AEGISX_URL/api/v35/lifecycle/overview"

curl -H "Authorization: Bearer $AEGISX_TOKEN" \
  "$AEGISX_URL/api/v35/lifecycle/plan?focus=validate"
```

Actual security-tool commands remain worker-local and must follow the individual tool's Markdown guide, authorized scope, approval and evidence requirements.

## Governance

All validation and response work requires explicit authorization, scope, Sudo/RBAC, approval where required, isolated managed workers, signed contracts, evidence hashing and audit logging.
