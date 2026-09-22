# VEYRA Phase 6 — "One-Stop Security Operations Shop"

**Status:** In Progress (P6-A foundation partially delivered as P4-3)
**Start date:** 2026-09-22
**Estimated total effort:** 25-35 hours across multiple sessions
**Depends on:** P0-P5 complete (all CI green, 61 commits, P5 closed with 61 total)
**Current baseline (2026-09-22):** 421 backend tests passing, 75.42% line coverage (70% floor enforced), frontend 73.64% coverage, `npm run build` green (1865 modules, 431 kB)

## Progress Tracker

| Sub-phase | Status | Commits | Notes |
|---|---|---|---|
| **P6-A** Checklist Registry | ✅ Partial — P4-3 delivered | `2cb5699`, `4692c1c`, `bfda286` | 61 checklists across 11 domains, runner stub, 36 tests, `docs/CHECKLISTS.md`. Remaining: API routes + model entities |
| **P6-B** Live Sensors + Baseline + Drop Diagnosis | ⬜ Not started | — | — |
| **P6-C** Status Chip + Chart Library | ⬜ Not started | — | — |
| **P6-D** Team Dashboards | ⬜ Not started | — | — |
| **P6-E** Live Monitoring + Checklist Library UI | ⬜ Not started | — | — |
| **P6-F** Checklist Runner UI | ⬜ Not started | — | — |
| **P6-G** Alerts + Notifications | ⬜ Not started | — | — |
| **P6-H** Trends + Historical View | ⬜ Not started | — | — |

## Vision

Extend VEYRA from a security control plane into a **one-stop security operations shop**
where the team can:

1. **Browse** a comprehensive library of cybersecurity checklists covering every domain
2. **Run** governed checklist evaluations with evidence capture and signed receipts
3. **Monitor** live sensor telemetry (Wi-Fi APs, Ethernet links, device joins/drops)
4. **Diagnose** connection drops and tampering events with root-cause hypotheses
5. **Visualize** pass/warn/fail state via status chips and charts (green → amber → yellow → semi-red → red)
6. **Operate** per-team dashboards (Blue, Red, SOC, IR, Cloud, AI, Supply Chain, Governance)

## Boundaries (governance-coherent with v5.0)

| Concern | Rule |
|---|---|
| **Sensor scope** | Only authorized networks/devices; token-gated ingest |
| **Evidence** | Every sensor event has timestamp + provenance + SHA-256 |
| **Baselines** | Explicitly approved, versioned, attributed to an owner |
| **Actions** | No autonomous enforcement — approval-gated, worker-executed |
| **Data retention** | Configurable, documented, auditable |
| **AI involvement** | Advisory only — never authoritative for status |
| **New checklists** | Must declare: purpose, owner, cadence, scope, evidence, remediation, tier |
| **No offensive capability added** | Only observe/correlate/prioritize — no attacks, no deauth, no injection |

**The "no hack-back, no C2, no credential attacks" boundary extends to every new surface.**

## Architecture
─────────────────────────────────────────────────────────────────┐
│ VEYRA v5.0 Console (frontend) │
│ │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│ │ Checklists │ │ Live Ops │ │ Team Dash │ │ Trends │ │
│ └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│ ▲ ▲ ▲ ▲ │
│ └──────────────┴────────────────┴──────────────┘ │
│ │ │
│ StatusChip, StatusPie, Sparkline, DropTimeline │
└────────────────────────────┼────────────────────────────────────┘
│ REST + WebSocket (future)
┌────────────────────────────▼────────────────────────────────────┐
│ VEYRA Control Plane (backend) │
│ │
│ ┌──────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│ │ checklist_ │ │ live_sensor_ │ │ state_engine │ │
│ │ registry.py │ │ ingest.py │ │ .py │ │
│ └──────────────────┘ └────────────────┘ └──────────────┘ │
│ ▲ ▲ ▲ │
│ ┌──────┴───────┐ ┌─────────┴────────┐ ┌──────┴───────┐ │
│ │ checklist_ │ │ baseline_engine │ │ drop_ │ │
│ │ runner.py │ │ (Wi-Fi/Ethernet) │ │ diagnosis.py │ │
│ └──────────────┘ └──────────────────┘ └──────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
│ HTTP ingest (token-gated)
┌────────────────────────────▼────────────────────────────────────┐
│ Sensors │
│ • local Wi-Fi sensor (macOS/Linux) │
│ • endpoint agent (collectors/endpoint-agent.py) │
│ • lab/collector.py (LAN discovery) │
│ • external probes (future) │
└─────────────────────────────────────────────────────────────────┘


## Sub-Phases

### P6-A — Checklist Registry (foundation)
**Effort:** 3-4 hr | **Files:** backend services, models, API, tests, docs | **Status:** 🟡 Partial — registry + runner + tests + docs done as P4-3

- [x] `backend/app/services/checklist_registry.py` — 61 checklists across 11 domains (P4-3a `2cb5699`, P4-3b `4692c1c`)
- [x] `backend/app/services/checklist_runner.py` — governed stub (validate + surface metadata, no execution) (P4-3c `bfda286`)
- [x] `backend/tests/services/test_checklist_registry.py` — 21 tests (P4-3a/b)
- [x] `backend/tests/services/test_checklist_runner.py` — 15 tests (P4-3c)
- [x] `docs/CHECKLISTS.md` — human-readable index (61 checklists, 11 domains)
- [ ] `backend/app/models/entities.py` — extend with `ChecklistDefinition`, `ChecklistRun`, `ChecklistResult`, `ChecklistReceipt` _(deferred to P6-A completion)_
- [ ] `backend/app/api/routes.py` — 4 new routes under `/api/v60/` _(next — see P6-A remaining)_
- [ ] CI: extend docs-drift validator to cover `docs/CHECKLISTS.md` drift against `checklist_registry.py`

**P6-A remaining (next session, ~45 min):**
1. Add API routes: `GET /api/v60/checklists`, `GET /api/v60/checklists/{id}`, `POST /api/v60/checklists/{id}/run`, `GET /api/v60/checklists/domains` (all read-only / stub execution, under existing `require_admin` gate where appropriate).
2. Add DB models only if persistence is needed; otherwise keep runner stateless and defer `entities.py` to P6-F (governed worker wiring).
3. Add `scripts/validate_checklists.py` or extend `scripts/validate_tool_documentation.py` to cross-check `docs/CHECKLISTS.md` against `CHECKLISTS` (counts per domain, IDs).
4. Add `docs-drift` CI step for `docs/CHECKLISTS.md`.

### P6-B — Live Sensors + Baseline + Drop Diagnosis (foundation)
**Effort:** 4-6 hr

- `backend/app/services/live_sensor_ingest.py` — normalizer
- `backend/app/services/baseline_engine.py` — baseline vs current drift
- `backend/app/services/drop_diagnosis.py` — root-cause hypotheses
- `collectors/wifi_sensor.py` — dedicated Wi-Fi tamper monitor
- `collectors/endpoint-agent.py` — extended (Wi-Fi scan, Ethernet state, link events)
- Extend `backend/app/models/entities.py` with sensor models
- Extend `backend/app/api/routes.py` with `/api/v61/` routes
- `backend/tests/test_live_sensors.py` — ~40 tests

### P6-C — Status Chip + Chart Component Library (UI foundation)
**Effort:** 2-3 hr

- `frontend/src/components/StatusChip.jsx`
- `frontend/src/components/StatusPie.jsx`
- `frontend/src/components/Sparkline.jsx`
- `frontend/src/components/Sparkbar.jsx`
- `frontend/src/components/HeatGrid.jsx`
- `frontend/src/components/DropTimeline.jsx`
- `frontend/src/components/TrendCard.jsx`
- `frontend/src/__tests__/components.test.jsx` — ~30 tests
- Pure SVG, no external chart library

### P6-D — Team Dashboards
**Effort:** 4-6 hr

- `frontend/src/v62_team_dash.jsx` — one dashboard per team
- `frontend/src/__tests__/v62.test.jsx` — ~20 tests
- Each dashboard: StatusChip per checklist + StatusPie + sparkline + drill-down

### P6-E — Live Monitoring + Checklist Library UI
**Effort:** 3-4 hr

- `frontend/src/v60_checklists.jsx` — browse + run checklists
- `frontend/src/v61_live_ops.jsx` — live Wi-Fi/Ethernet/device/drop view
- `frontend/src/__tests__/v60_v61.test.jsx` — ~25 tests

### P6-F — Checklist Runner UI
**Effort:** 3-4 hr

- Wire checklist runs to governed workers
- Show evidence + receipts
- Approval gates for high-impact checks

### P6-G — Alerts + Notifications
**Effort:** 2-3 hr

- Webhook / Slack / email on state change
- Chip degradation → notify owner
- Drop events → notify on-call

### P6-H — Trends + Historical View
**Effort:** 2-3 hr

- Posture over time
- MTTR per checklist
- Coverage %
- Regression detection

## The Status Chip Model

100% ───────────────────────── GREEN ✓ healthy
80% ───────────────────────── AMBER ⚠ minor issues (warning)
50% ───────────────────────── YELLOW ⚠ multiple issues (degraded)
20% ───────────────────────── SEMI-RED ⚠ serious issues
0% ───────────────────────── RED ✗ critical / failing


**Rule:** chip colour = worst result in the checklist run. Any critical check fails ⇒ RED, regardless of pass percentage.

## Checklist Domains

**Live Monitoring & Physical Layer**
Wi-Fi AP baseline, Wi-Fi tamper detection, Ethernet link monitoring, new device connections, connection drop diagnosis, wired traffic anomaly

**Identity & Access**
MFA coverage, privileged account review, session anomaly, brute-force detection, token expiry, service account review, sudo audit

**Endpoint**
Patch level, running services baseline, USB/DLP events, AV/EDR health, autorun entries, startup items

**Cloud & Container**
Public exposure, IAM privilege drift, container image digest, RBAC baseline, secret scan, K8s CIS baseline

**AI/Agent**
Prompt injection battery, RAG retrieval audit, MCP server inventory, tool allowlist drift, agent identity, trajectory assurance

**Network Defense**
IDS/NSM health (Suricata), flow baseline, DNS anomalies, TLS cert expiry, segmentation check

**DFIR**
Evidence custody, case SLAs, timeline completeness, hash verification, YARA rule health

**Governance**
Doc coverage, tool access matrix, approval SLAs, license review, SBOM currency

**Supply Chain**
SBOM freshness, SLSA provenance presence, dependency CVE scan, build reproducibility, signing key rotation

**Red Team**
Rules of engagement, scope enforcement, engagement wrap-up, findings triage

**Blue Team**
Detection coverage, alert triage SLA, false positive rate, playbook currency

## Directory Additions

### Backend

backend/app/services/
├── checklist_registry.py
├── checklist_runner.py
├── live_sensor_ingest.py
├── baseline_engine.py
├── drop_diagnosis.py
└── state_engine.py

### Frontend
frontend/src/components/
├── StatusChip.jsx
├── StatusPie.jsx
├── Sparkline.jsx
├── Sparkbar.jsx
├── HeatGrid.jsx
├── DropTimeline.jsx
└── TrendCard.jsx

frontend/src/
├── v60_checklists.jsx
├── v61_live_ops.jsx
├── v62_team_dash.jsx
└── v63_trends.jsx


### Sensors
collectors/
├── endpoint-agent.py (extended)
└── wifi_sensor.py

### Docs
docs/
├── CHECKLISTS.md
├── CHECKLIST_FRAMEWORK.md
├── LIVE_MONITORING.md
├── STATUS_CHIP_MODEL.md
└── TEAM_DASHBOARDS.md


## Success Criteria

- All checklists have complete docs validated by CI
- Every sensor event has timestamp + SHA-256 + provenance
- Every checklist run produces a signed receipt
- Team dashboards render chips + charts with real state
- No external enforcement from the console — workers only
- 100% backend service coverage maintained
- Frontend coverage extended to cover new components
- All CI jobs green

## Verification Baseline (2026-09-22 — before P6-B)

Run as a suite of targeted commands before starting P6-B:

| Check | Command | Expected |
|---|---|---|
| Project structure | `ls backend/app/services/ | wc -l` | 50+ modules |
| All imports resolve | `python -m compileall -q backend/app` | zero errors |
| Tests pass | `pytest -q` (from `backend/`) | 421 passed |
| Frontend build | `npm run build` (from `frontend/`) | 1865 modules, 431 kB |
| Frontend tests | `npm run test:coverage` | 73.64% Stmts, green |
| Validators | `PYTHONPATH=backend python scripts/validate_tool_documentation.py` | 587/587 verified |
| No duplicate declarations | `npm run build` catches `PARSE_ERROR: Identifier already declared` | green |
| CI workflows parse | `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` | valid YAML |
| Untracked files | `git status` | only `docs/CHECKLISTS.md` (now tracked) |

**2026-09-22 result:** all checks green. Backend 421 tests (75.42% coverage, 70% floor enforced), frontend build green, validators green, all 4 CI jobs parse. No stale files. `docs/CHECKLISTS.md` was untracked — committed as part of this doc fix.

