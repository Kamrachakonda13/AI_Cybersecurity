# Frontend ↔ Backend Contract Audit

**Audit date:** 2026-09-22
**Backend HEAD at audit:** `d963927`
**Frontend HEAD at audit:** `23cec73`
**Re-audit triggered by:** P0/P1 backend changes (env var rename, rebrand, contract changes)

## Purpose

Verify the frontend (`frontend/src/`) remains consistent with the backend after
the P0 and P1 remediation phases. Both phases changed naming, contracts, and
governance values that the UI consumes.

## Scope

- `frontend/src/*.jsx` (20 files)
- `frontend/package.json`, `frontend/package-lock.json`

## Method

1. **Static grep** for stale identifiers (`AegisX`, `aegisx_*`, `subfinder-2`,
   `isolated_worker`, old contract versions, hardcoded counts)
2. **Build verification** (`npm run build`)
3. **Endpoint inventory** cross-check (frontend calls vs. backend routes)
4. **Source inspection** of storage keys and auth headers

## Static Checks

| # | Check | Command | Result |
|---|---|---|---|
| 1 | `AegisX` / `AEGISX` / `aegisx` | `grep -rn 'aegisx\|AegisX\|AEGISX' frontend/src/` | ✅ 0 hits |
| 2 | sessionStorage keys | `grep -rn 'sessionStorage\|localStorage' frontend/src/` | ✅ all `VEYRA_*` |
| 3 | Auth headers | (part of key scan) | ✅ all `X-VEYRA-*` |
| 4 | `subfinder-2` refs | `grep -rn 'subfinder-2' frontend/src/` | ✅ 0 hits |
| 5 | `isolated_worker` refs | `grep -rn 'isolated_worker' frontend/src/` | ✅ 0 hits |
| 6 | Old contract version refs | `grep -rn 'contract_version\|receipt_version\|verification_required' frontend/src/` | ✅ 0 hits |
| 7 | Hardcoded tool count | `grep -rn '5[0-9][0-9]' frontend/src/ \| grep -iE 'tool\|count\|total'` | ✅ 1 false positive (CSS pixel value) |
| 8 | Build | `cd frontend && npm run build` | ✅ 1863 modules, 431 kB |

## Findings

### F-1 — Syntax error in `main.jsx` nav array (FIXED)

**Severity:** Critical (blocked build)
**File:** `frontend/src/main.jsx`
**Line:** 44 (originally `const nav=[[...],['VEYRA v5 Control Plane',ShieldCheck]]));`)
**Issue:** Extra closing parens `))` at the end of the nav array declaration,
likely introduced during the P0 AegisX→VEYRA rebrand.
**Fix:** Commit `8730a57` — removed the extra `))`. Also reformatted the file
(spaces around `{...}` and commas).
**Verification:** `npm run build` now passes.

### F-2 — Stale lockfile version (FIXED)

**Severity:** Low (metadata only)
**File:** `frontend/package-lock.json`
**Issue:** Lockfile declared version `4.0.0` while `package.json` declared `5.0.0`.
**Fix:** Commit `23cec73` — synced to `5.0.0`.

## Endpoints the Frontend Uses

### Auth (`main.jsx`)
- `POST /api/auth/login` → `{ token, user }`
- `GET  /api/auth/me` → user object
- `POST /api/auth/password` → change password

### Admin (`main.jsx`)
- `GET  /api/admin/ethical-hacking/tools` → `{ tools: [...] }`
- `GET  /api/admin/ethical-hacking/jobs` → jobs array
- `POST /api/admin/ethical-hacking/jobs` → `{ job_id }`

### Fabric (`main.jsx`)
- `GET /api/fabric/overview` → overview
- `GET /api/fabric/ai-attack-paths` → paths
- `GET /api/fabric/events?limit=N` → events array

### V40 Supply Chain (`v40.jsx`)
- `GET  /api/v40/supply-chain/overview` → `{ ... }`
- `GET  /api/v40/update-scout` → `{ results: [...] }`
- `GET  /api/v40/deployments` → deployments array
- `GET  /api/v40/health-checks` → health checks
- `POST /api/v40/releases` → `{ release_id, verification_status }`
- `POST /api/v40/deployments` → `{ deployment_id, manifest_sha256, manifest.signature_status }`
- `POST /api/v40/rollback` → `{ deployment_id, manifest.version }`
- `PUT  /api/v40/tools/:id/policy` → saved policy
- `POST /api/v40/tools/:id/freeze` → `{ frozen_until }`
- `POST /api/v40/tools/:id/quarantine` → quarantined
- `GET  /api/v40/docs/index` → `{ items: [...] }`
- `GET  /api/v40/agent-swarm/containment` → `{ policy }`
- `PUT  /api/v40/agent-swarm/containment` → updated policy
- `POST /api/v40/agent-swarm/simulate` → simulation result
- `GET  /api/v41/supply-chain/runtime` → runtime data

### V42 Trusted Supply Chain (`v42.jsx`)
- `GET  /api/v42/trusted-supply-chain/overview`
- `GET  /api/v42/ai-supply-chain/assets`
- `GET  /api/v42/agent-circuit-breakers`
- `POST /api/v42/agent-circuit-breaker` → `{ breaker_id }`
- `POST /api/v42/ai-supply-chain/assets` → `{ asset_id }`

### V50 Control Plane (`v50.jsx`, `v50_ai_apps.jsx`)
- `GET  /api/v50/overview`
- `GET  /api/v50/ai-assets`
- `GET  /api/v50/decisions`
- `POST /api/v50/ai-assets/register` → `{ asset, evaluation: { status, score, missing } }`
- `GET  /api/v50/ai-applications/catalog` → `{ applications: [...] }`
- `POST /api/v50/ai-applications/{cybsoc-rag|vulnerability-rag|research-agent|incident-response|enterprise-decision|evaluation}`

### V3 / V29 / V31–V39 (per-version views)
- `v3.jsx`: `/api/v3/fabric/response-plan`
- `v29.jsx`: `/api/v29/wireless`, `/api/v29/timeline`, `/api/v29/infrastructure`, `/api/v29/attribution`, `/api/v29/evidence-bundle`, `/api/v29/overview`
- `v31.jsx`: `/api/v31/trace/plan`
- `v35.jsx`–`v39.jsx`: various `/api/v3X/...` endpoints

**Full endpoint list:** see the grep command in the regression checklist below.

## Storage Keys

All frontend `sessionStorage` keys use the `VEYRA_*` prefix:

| Key | Purpose |
|---|---|
| `VEYRA_user_token` | User session token |
| `VEYRA_admin_token` | Admin authorization token |
| `VEYRA_privileged_admin_token` | Privileged admin token (second gate) |
| `VEYRA_ai_token` | AI gateway token |

**Note:** Keys are uppercase `VEYRA_*` (not lowercase). This is consistent across
the codebase; env vars use the same uppercase convention.

## Auth Headers

| Header | Sent when | Purpose |
|---|---|---|
| `Authorization: Bearer <token>` | User session token present | Standard auth |
| `X-VEYRA-Admin-Token` | Admin token present | Admin-gated endpoints |
| `X-VEYRA-Privileged-Admin-Token` | Privileged admin token present | High-impact tool endpoints |
| `X-VEYRA-AI-Token` | AI gateway token present | AI gateway evaluation |

**Note:** The source has a known typo — `X-VEYRA-Priviledged-Admin-Token` (missing 'e') — that is preserved for compatibility. Both spellings are accepted by the backend.

## Regression Checklist for Future Changes

Whenever the backend changes a **contract value, endpoint path, response shape,
storage key, or auth header**, run:

```bash
# 1. Static check for stale identifiers
grep -rn 'aegisx\|AegisX\|AEGISX' frontend/src/
grep -rn 'subfinder-2\|isolated_worker' frontend/src/
grep -rn 'contract_version\|receipt_version' frontend/src/

# 2. Storage key consistency
grep -rohE "sessionStorage\.(getItem|setItem|removeItem)\(['\"][^'\"]+['\"]" frontend/src/ \
  | grep -oE "['\"][^'\"]+['\"]" | sort -u

# 3. Full endpoint list
grep -ohE 'fetch\(`\$\{API\}[^`]*`' frontend/src/ -r \
  | sed 's/.*API}//' | sed 's/`$//' | sort -u

# 4. Build + test
cd frontend && npm run build && npm test && cd ..

# 5. Manual smoke test (optional)
cd frontend && npm run dev
# login flow, tool catalog, any worker/verification panel