# VEYRA v2.8 — Managed Security Worker Fabric

## What problem this solves

The SaaS control plane should not become the machine that contains every security binary. VEYRA therefore separates **catalog/control** from **execution**.

### Control plane

- UI
- RBAC
- Sudo
- permissions
- approvals
- scopes
- job contracts
- marketplace
- evidence
- audit

### Worker plane

- Kali/Linux worker
- AI security worker
- cloud posture worker
- DFIR worker
- network sensor/worker
- future Windows/macOS worker

## Worker states

- `pending` — registered but not yet verified
- `online` — heartbeat received
- `offline` — heartbeat expired
- `quarantined` — worker blocked by policy

## Tool states

A global catalog entry and worker inventory are deliberately different.

A tool may be:

- requested
- installing
- healthy
- outdated
- failed
- quarantined
- unavailable

## API

### Register worker

`POST /api/workers/register`

Registers metadata only. It does not execute anything on the worker.

### Heartbeat

`POST /api/workers/{worker_id}/heartbeat`

Records worker liveness. Production should replace this POC endpoint with workload identity/signature authentication.

### List workers

`GET /api/workers`

### Report tool state

`POST /api/workers/{worker_id}/tools/report`

Workers report version, state, binary path, checksum, SBOM reference and verification timestamp.

### Worker tool inventory

`GET /api/workers/{worker_id}/tools`

### Installation plan

`GET /api/workers/{worker_id}/install-plan/{tool_id}`

Returns a policy-bound plan. It does not run a package manager.

## Production worker contract

A production worker should authenticate with a short-lived workload identity and accept only signed contracts containing:

- tenant
- worker ID
- tool ID
- immutable artifact ID
- version
- checksum
- requested operation
- allowed inputs
- scope
- expiration
- approval reference
- policy hash

The worker should return:

- execution receipt
- stdout/stderr hashes or structured output
- artifact hashes
- SBOM reference
- exit status
- start/end time
- tool version
- worker identity
- policy hash

## Security rule

Never expose `shell`, `exec`, arbitrary `apt`, arbitrary `pip`, or unrestricted command strings from the customer-facing API. Tool execution should be selected from a registry and represented as typed parameters.
