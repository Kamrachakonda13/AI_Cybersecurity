# VEYRA Phase 6 — Gap Analysis (One-Stop Security Operations Shop)

**Date:** 2026-09-22  
**HEAD at analysis:** `bfda286` (+ uncommitted P6-A-4..B)  
**Baseline tests:** 421 backend passing, frontend 73.64% Stmts, 658 tools in catalog  
**Plan:** `docs/PHASE_6_PLAN.md` (P6-A..H)

## 1. Existing coverage — what we have

| Layer | Inventory | Status |
|---|---|---|
| **Tool catalog** | `extended_catalog.py` (459) + `ai_cutting_edge_2026` (37) + `ai_ecosystem` (162) = **658 tools** across 57 categories | ✅ All cybersecurity categories present. Network: `Network Discovery 17`, `Network Defense 6`, `Firewall/WAF/VPC` via Cloud. Cloud: `Cloud 21`, `Cloud/Container 3`, `Kubernetes 17`, `IaC 3` |
| **Checklist registry** | 61 → **74** checklists (after this session) across 11 domains | ✅ Was 3/7 in P6-A. Now extended: `network_defense 9` (+firewall, WAF, VPC flow logs, NACL), `cloud_container 10` (+CloudTrail, encryption, key rotation, workload identity, CIS), `endpoint 7`, `governance 8` |
| **Runner stub** | `checklist_runner.py` validates + surfaces boundary/evidence, frozen dataclass | ✅ Tests 15 passing |
| **API** | `/api/v60/checklists*` (4 routes) added in `aa8bc4e` | ✅ Public + stub run. P6-A-4 now persists runs/receipts (`ChecklistRun/Result/Receipt`) |
| **Entities** | ~50 tables, but no checklist or sensor tables before | 🟡 Added: `ChecklistDefinition/Run/Result/Receipt`, `LiveSensorEvent`, `NetworkBaseline`, `DropEvent` |
| **Sensors** | `WifiNetwork`, `DiscoveredHost`, `Device`, `collectors/endpoint-agent.py` | 🟡 Wi-Fi scan exists, but no P6-B `live_sensor_ingest / baseline_engine / drop_diagnosis / state_engine` until this session |
| **Frontend** | `main.jsx` nav 44 sections, Tool Marketplace browses 658 tools, Tool Academy docs 587 | ✅ Marketplace covered Network/Cloud via categories; checklist UI + live-ops UI were missing |

## 2. User requirement — "all cybersecurity tools, Network security tools, Cloud security tools built into UI"

**Interpretation:** every network & cloud tool in the 658 catalog must be browsable/filterable from the console, with status-chip health per domain, not hidden behind an API.

**Gap before this session:**

| Requirement | Before | After |
|---|---|---|
| Browse all 658 tools with Network filter | Marketplace existed but no `Network Security` section; categories mixed | Checklist Library (`v60_checklists.jsx`) + Team Dash (`v62`) now expose `network_defense` and `cloud_container` as top-level filters; Marketplace already groups `Network Discovery/Defense`, `Cloud`, `Kubernetes`, `IaC` |
| Cloud security posture (public exposure, IAM, K8s, secrets, encryption, CloudTrail, CIS) | Only 5 cloud checklists | Now 10 cloud checklists covering the full Cloud Security lessons list |
| Network security posture (firewall, WAF, segmentation, flow, DNS, TLS, VPC/flow-log, NACL) | Only 5 network checklists | Now 9 network checklists mirroring Network Defense lessons |
| Cybersecurity breadth (vuln scan, EDR, phishing, backups) | Endpoint/governance had 5–6 each | Now 7 endpoint + 8 governance, closing SIEM/EDR/phishing gaps |
| Live ops for network/cloud | No normalized ingest, no baseline, no drop diagnosis | `live_sensor_ingest.py`, `baseline_engine.py`, `drop_diagnosis.py`, `/api/v61/*` (ingest/events/baselines/drops) |

## 3. P6-A..H — remaining gaps and how they close

| Sub-phase | Gap at `bfda286` | What lands this session |
|---|---|---|
| **P6-A** | 3/7: `entities.py` 0, routes only stubbed, CI drift no checklists, 36 tests | ✅ `entities.py` 4+3 models, runner persistence (`create_persisted_run`, `create_receipt`, `seed_definitions`), `/api/v60/runs`, `/api/v60/receipts/{id}`, `scripts/validate_checklists.py`, registry 74 + docs 74 synced, tests updated to 74 |
| **P6-B** | No sensor services, no `/api/v61` | ✅ `live_sensor_ingest.py` (hash + provenance), `baseline_engine.py` (approved/versioned + drift), `drop_diagnosis.py` (hypotheses), `state_engine.py` (chip), 7 routes, 3 new tables |
| **P6-C** | No chip library | ✅ 7 pure-SVG components: `StatusChip`, `StatusPie`, `Sparkline`, `Sparkbar`, `HeatGrid`, `DropTimeline`, `TrendCard` |
| **P6-D** | No per-team view | ✅ `v62_team_dash.jsx` — 8 teams (Blue/Red/SOC/IR/Cloud/AI/Supply/Gov) with chip + pie + sparkline |
| **P6-E** | No browse/run or live view | ✅ `v60_checklists.jsx` (search + domain filter + Run), `v61_live_ops.jsx` (events/baselines/drops, 15s poll) |
| **P6-F** | Runner UI not wired to workers | 🟡 Stub run wired to `create_persisted_run` + receipt; full worker execution deferred to existing `execution_plane` (governed, approval-gated). Existing `WorkerNode` flow already enforces isolated-worker boundary |
| **P6-G** | No alerts | 🟡 AuditEvents emitted on every run/ingest; webhook/Slack/email via existing `notify.py` is the extension point — not yet auto-triggered on chip degradation (documented as next) |
| **P6-H** | No history | 🟡 `v63_trends.jsx` (14-day runs, sensor volume, coverage heatmap, MTTR stub) — real time-series history requires P6-H DB aggregation (noted as next) |

## 4. Roadmap reconciliation

`NEXT_STEPS.md` P6-1..P6-9 (frontend coverage gate, `main.jsx` extraction, router, Playwright, SBOM vuln scan, Trivy, branch protection) are **not** P6-A..H. Decision: renumber as **P7 candidates** and fold frontend items under P6-C/E where they naturally fit (coverage gate → CI, router → view routing). See `docs/PHASE_6_PLAN.md` § Reconciliation.

## 5. What remains after this commit

- Real worker execution for checklist runs (P6-F beyond stub) — must go through `execution_plane` + `WorkerNode` contract, not direct shell.
- Auto-alert on chip `red`/`semi_red` → `notify.py` (P6-G).
- Historical aggregation for `state_engine` trends / MTTR (P6-H) — currently synthetic data in `v63`.
- CI `docs-drift` job extended to run `scripts/validate_checklists.py --check` (one-line addition).
- Enforce frontend coverage threshold 65% (mirror backend 70% floor) at CI.

All are non-blocking for "browse + run + live ops + team dashboards + trends" — the core One-Stop Shop is functional.
