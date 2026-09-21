# VEYRA Admin Ethical Hacking Control Plane

VEYRA now has a dedicated **administrator-only Ethical Hacking** control plane.
It is intentionally separate from the normal SOC/operator experience.

## Access model

The POC uses `VEYRA_ADMIN_TOKEN` and the `X-VEYRA-Admin-Token` header. The
frontend stores the token only in session storage. This is a development gate,
not production identity management. Production should replace it with OIDC/SSO,
MFA, RBAC/ABAC and a privileged-access workflow.

Non-admin users:

- do not receive the Ethical Hacking navigation item;
- receive HTTP 403 from the admin APIs;
- cannot stage ethical-hacking jobs;
- cannot invoke an arbitrary shell through VEYRA.

## Tool registry

The admin registry catalogs network, web/API, identity, credential-audit,
network-defense, vulnerability, cloud/Kubernetes, endpoint/DFIR, malware,
reverse-engineering, threat-intelligence, detection-engineering and AI-security
tools.

A tool's `execution_profile` determines its boundary:

- `own_network` — local networks owned/authorized by the operator
- `approved_scope` — explicitly approved assessment scope
- `lab_or_approved_worker` — isolated lab or approved assessment worker
- `isolated_lab_only` — cyber-range only
- `offline_audit_only` — offline authorized audit workflow
- `read_only_cloud` — read-only cloud identity
- `isolated_analysis_worker` — isolated forensic/malware worker
- `sensor` — telemetry/detection sensor
- `approved_connector` — API/feed integration

## Job lifecycle

```text
Admin
  -> Select tool
  -> Define target + scope
  -> Attach approval ticket
  -> Stage job
  -> Policy validation
  -> Isolated worker
  -> Tool execution
  -> Normalize results
  -> Evidence + provenance
  -> Finding / Security Graph
  -> Human review
```

The current POC now implements the **job/evidence control plane** through staging, approval, queueing and normalized evidence ingestion. It still does not expose arbitrary shell,
payload delivery, persistence, credential attacks, C2, exploit replay or
hack-back from the browser/API.

## Current job/evidence plane

Admin APIs now create a deterministic job contract with a SHA-256 contract hash, validate the tool execution profile, store approval metadata, queue the contract for an external isolated worker, and accept normalized evidence with artifact hashes and provenance. The API itself never launches a process.

Endpoints:
- `POST /api/admin/ethical-hacking/jobs` — create contract
- `GET /api/admin/ethical-hacking/jobs` — admin job queue
- `POST /api/admin/ethical-hacking/jobs/{job_id}/approve` — approve
- `POST /api/admin/ethical-hacking/jobs/{job_id}/dispatch` — queue for isolated worker
- `POST /api/admin/ethical-hacking/jobs/{job_id}/evidence` — ingest normalized evidence
- `GET /api/admin/ethical-hacking/jobs/{job_id}/evidence` — retrieve evidence

The production worker should authenticate independently, re-check authorization/scope, execute only inside the declared isolation profile, sign results, and return evidence to VEYRA.

## Future worker contract

Each connector should declare:

```text
name, version, category, target_types, authorization,
isolation_profile, approval_level, rate_limit, credentials,
input_schema, output_schema, evidence_schema, rollback_strategy,
audit_events, provenance
```

High-impact actions require separate worker isolation, explicit scope, approval,
rate limits, signed/provenance-aware results and immutable audit events.


## Privileged tooling tier

All ethical-hacking tools are hidden behind the administrator control plane. VEYRA v2.4 also classifies high-impact tools as `privileged_admin`; these require a second `X-VEYRA-Privileged-Admin-Token` gate in addition to the normal admin token. This tier includes exploit frameworks, credential-audit/authentication-testing tools, SQLMap, high-speed scanners and active fuzzing/discovery tools. Staging, approval and dispatch of these jobs require the privileged gate. Production should replace POC tokens with SSO/OIDC, MFA and PAM/JIT elevation.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
