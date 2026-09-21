
> Current release: **VEYRA v3.7 — Security Radar & Ecosystem Scout**
# VEYRA — AI-Native Cybersecurity Operations, Cloud & AI Security Platform

VEYRA is a security control plane that correlates network, endpoint, identity, cloud, data and AI-security signals into one operational model with an explainable risk engine, a Security Graph with attack-path analysis, governed assessment jobs, static forensics, and separate Red/Blue team workflows.


## v3.6 — Security Radar & Ecosystem Scout

VEYRA v3.6 continuously scouts the security ecosystem and separates mature recommendations from experimental candidates. It adds Security Radar, 11 newly documented tool integrations, and an explicit promotion lifecycle based on provenance, security review, license review, version pinning, SBOM, isolated-worker validation and documentation.

The latest radar incorporates OWASP's 2026 Agent Control Standard and GenAI framework crosswalk, Kubernetes policy/runtime work such as Kyverno and Inspektor Gadget, and emerging AI-agent runtime controls. See `docs/SECURITY_RADAR_V36.md` and `docs/TOOL_SCOUT_V36.md`.

## v3.1 — Sudo Security Arsenal & Adversary Trace Fabric

VEYRA v3.1.1 adds a privileged Sudo Security Arsenal over the existing governed worker fabric. The catalog now exposes **577 security tools/integrations** through a single policy-aware registry, with per-tool UI guidance, terminal guidance, execution boundaries, expected evidence and access tiers.

New UI/API surfaces:
- **Sudo Security Arsenal** — privileged tool catalog, per-tool guidance and terminal start/help instructions.
- **Adversary Trace** — defensive investigation workflow for source/destination correlation, evidence preservation, TI enrichment, timeline reconstruction and containment planning.
- `GET /api/v31/arsenal/overview`
- `GET /api/v31/arsenal/tools`
- `GET /api/v31/arsenal/tools/{tool_id}`
- `POST /api/v31/trace/plan`

Every catalog entry is documented in `docs/TOOL_USAGE_CATALOG_V31.md`. Operational design is in `docs/SUDO_SECURITY_ARSENAL_V31.md`, incident tracing in `docs/ADVERSARY_TRACE_V31.md`, and worker-terminal usage in `docs/TERMINAL_RUNBOOK_V31.md`.

Kali's current metapackage model groups tools across wireless/802.11, Bluetooth, RFID, SDR, web, exploitation, forensics, reverse engineering and other domains; VEYRA follows the same breadth but keeps third-party binaries on managed workers rather than inside the SaaS API. citeturn0search0turn0search1

For active incidents, VEYRA uses evidence preservation and containment rather than hack-back. CISA guidance includes isolation, firewall filtering, credential/secret rotation and blocking/logging unauthorized access as containment measures. citeturn0search24turn0search25

## Current capabilities (v2.7 platform foundation)

- Enterprise console: Overview KPI tiles (all clickable with drill-downs), Security Graph, SOC, Network, Offensive Security, Forensics, Endpoint (+devices/DNS), Cloud, AI Security, Data Security, Identity (+brute-force), Governance, Red Team, Blue Team
- Asset, service, port and process/user attribution (expected vs unexpected baseline)
- Identity, privileged-account, session, DNS-query and login-attempt telemetry + ingestion APIs
- Device inventory via consented collector (`lab/collector.py`: arp neighbours, lab ping-sweep)
- Wi-Fi/LAN neighbour discovery: names, IPs, MACs, offline vendor lookup (`services/discovery.py`, Network-section panel)
- Network-flow telemetry + ingestion; browsing as DNS metadata (never page content)
- Findings, incidents, deterministic explainable risk scoring (formula in `backend/app/services/risk.py`)
- Threat-intel records with CISA KEV / MITRE ATT&CK seed data + `kev`/`exploited` flags
- Security Graph (`backend/app/services/graph.py`): BFS attack paths internet → sensitive data + 6 correlation answers
- Safe web-posture assessment (headers/TLS/banner/robots) with private/lab approval gate + rate limit + audit
- Static-only forensics (`backend/app/services/forensics.py`): eml/phishing, Office macro, PDF active content, PE/ELF headers, PCAP flows/DNS, IOC + YARA-like heuristics — never executes samples
- Severity + category remediation playbooks (`GET /api/remediation`), Red/Blue doctrine (`GET /api/teams/red|blue`), live-session triage on own telemetry (`POST /api/session/triage`)
- Evidence-first AI investigation endpoint (advisory mode, human approval required)
- Isolated lab target (`lab/vulnerable-web`) + red/blue demo script + 5 guide docs
- Live CISA KEV + NVD ingestion (`CveRecord`, refresh endpoint, optional 24h scheduler)
- MITRE ATT&CK knowledge (16 techniques incl. 2 ATLAS concepts) + per-finding coverage
- Attack paths with per-path risk + choke-point ranking
- Endpoint agent (`collectors/endpoint-agent.py`): heartbeat sync, ports, USB, DLP-lite secret scan; token-gated ingest
- USB/DLP events with auto-findings (mass storage on C5 hosts; allowed secrets)
- Cloud adapters: Prowler-JSON import + live read-only AWS scan (S3/SG/IAM)
- AI red evaluation battery (lab gateways, approval-gated) + vector-DB tenant enforcement + retrieval audit
- SOAR engine: 4 playbooks, approval-gated runs, DB-safe execution (revoke sessions, block indicators, incidents)
- PostgreSQL persistence + Docker Compose (base + lab overlay), backend test suite

## v2.7 — Kali + AI/Cloud Security Tool Ecosystem

VEYRA now maintains one governed tool catalog for the security console. The base
85-tool registry is expanded with a large Kali Linux 2026.3.2-derived catalog and
additional enterprise AI/cloud/AppSec/DFIR/identity tooling.

### New UI surfaces

- **Tool Runner** — Kali-style guided forms, searchable catalog, role-aware access,
  approval requests and evidence/job status.
- **Tool Marketplace** — select a managed security worker and request installation
  of an approved tool package. The SaaS API never accepts arbitrary package or shell
  commands.
- **Tool Academy** — category-aware help and operational guidance for every tool.
- **User & Permissions** — sudo-controlled per-user tool entitlements continue to
  apply to the expanded catalog.

### Managed worker architecture

```text
Customer / Sudo
      │
      ▼
VEYRA UI ── policy + RBAC + scope + approval ──► Job / Install Manifest
      │                                             │
      │                                             ▼
      │                                      Signed Worker
      │                                             │
      │                                   package/tool execution
      │                                             │
      ◄──────── evidence + hashes + SBOM + audit ───┘
```

Third-party tools are not bundled into the SaaS image. A managed worker is the
execution environment. High-impact tooling is privileged-admin gated and all jobs
retain explicit scope, purpose and provenance.

See `docs/TOOL_ECOSYSTEM_V27.md` for the complete operating model.

## Safety boundary

VEYRA is designed as a defensive security control plane. It can catalog and
coordinate a broad security-tool ecosystem, but it does **not** expose an
unrestricted attack console.

- Security-tool integrations are governed connectors with explicit target scope,
  approval, isolation, rate limits, audit trails and result provenance.
- Exploit replay, credential attacks, payload delivery, persistence, C2 and
  hack-back are not exposed through the browser/API.
- Active testing belongs in the isolated lab/cyber-range or an explicitly
  authorized assessment environment.
- For an active incident, VEYRA prioritizes evidence preservation, static
  analysis, telemetry correlation, threat-intelligence enrichment and
  attribution hypotheses. It does not retaliate against suspected attackers.
- Monitoring (devices/DNS/logins) is limited to systems and networks for which
  the operator has authorization and an appropriate notice/retention policy.

See `docs/TOOLING_MATRIX.md` and `docs/INCIDENT_REVERSE_ENGINEERING.md`.

## AI / RAG / agent security direction

VEYRA should treat AI as a security workload **and** as an analyst-assistance
layer. The next generation of the platform will add:

- Hybrid RAG: lexical + vector retrieval + metadata authorization + reranking.
- Graph RAG: Security Graph context combined with document evidence.
- Evidence/provenance bundles: source, timestamp, tenant, hash and retrieval path.
- Agent observability: model calls, tool calls, MCP/A2A interactions, memory reads,
  approvals and external side effects.
- Agent Control Plane: tool allowlists, capability scopes, time limits,
  transaction budgets, approval gates and policy decisions.
- MCP security inventory and runtime policy enforcement.
- Agent-to-agent trust and message validation.
- Memory/context poisoning detection and rollback.
- Model / prompt / tool / skill supply-chain inventory and signing/provenance.
- AI red-team evaluation with repeatable regression suites and attack replay in
  the lab.
- LLM/agent telemetry using OpenTelemetry-compatible traces.
- Cost/unbounded-consumption controls, model routing and circuit breakers.
- Model-behavior evaluation: hallucination/grounding, refusal, policy adherence,
  data leakage and tool-use correctness.
- NIST AI RMF / GenAI Profile, MITRE ATLAS and OWASP GenAI/Agentic mappings.

These should be implemented behind deterministic policy controls; an LLM must
not be the authority that grants itself permissions or decides whether a
destructive action is safe.


- No arbitrary shell, no exploitation replay (Metasploit/Burp-active disabled by design), no payload delivery, no hack-back.
- Assessments are passive checks over http(s) with target validation (blocks metadata IP/userinfo), lab/private approval gate, per-host cooldown, batch/size caps, and an audit row per action.
- Monitoring (devices/DNS/logins) is lawful-basis only: your own network/devices with authorization + user notice. See `docs/NETWORK_VISIBILITY_GUIDE.md`, `docs/FORENSICS_GUIDE.md`.

## Run

```bash
cp backend/.env.example backend/.env
docker compose up --build                                  # platform only
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build   # + lab target
python3 lab/red_blue_demo.py                               # red→blue end-to-end demo
python3 lab/collector.py --dry-run                         # passive device discovery preview
```

Frontend: http://localhost:3000 · API docs: http://localhost:8000/docs · Health: http://localhost:8000/health · Lab target: http://localhost:4101

Tests: `cd backend && PYTHONPATH=. python3 -m pytest tests -q` (backend test suite) · Frontend build: `cd frontend && npm run build`
Production ops (tokens, schedules, backups): `docs/PRODUCTION_GUIDE.md`

## Recommended next implementation phases

### v1.6 — Security-tool control plane
Create a connector registry for network discovery, web assessment, API testing,
cloud posture, identity assessment, container/Kubernetes security, packet/network
analysis, endpoint/DFIR, malware triage and AI red teaming. Each connector should
declare: supported targets, read/write level, required approval, isolation class,
rate limit, credentials, evidence outputs and rollback characteristics.

### v1.7 — Detection engineering + evidence lake
Add normalized events, Sigma-style detections, YARA rule execution in an isolated
analysis worker, IOC lifecycle, evidence objects, chain-of-custody metadata,
timeline reconstruction and alert deduplication/correlation.

### v1.8 — Production RAG + Security Graph RAG
Introduce PostgreSQL/OpenSearch for operational search, Qdrant (or another
dedicated vector service) for embeddings, hybrid retrieval, reranking, document
ACL filtering and graph-aware context. Every AI answer should return evidence
IDs/citations and retrieval-policy decisions.

### v1.9 — Agent Control Plane
Introduce controlled AI agents for triage, threat hunting, evidence collection,
cloud review and remediation recommendation. Add MCP/A2A inventories, tool
capabilities, per-agent identity, approval gates, action budgets and full
OpenTelemetry traces.

### v2.0 — Incident reverse-engineering workbench
Correlate PCAP/DNS/HTTP/auth/process/file/EDR/cloud/AI telemetry into an attack
timeline; enrich IOCs with threat intelligence; compare behaviors to ATT&CK/ATLAS;
produce attribution hypotheses with confidence and evidence. Attribution is
probabilistic and evidence-based, never a claim based on a single IOC.

See `docs/TOOLING_MATRIX.md`, `docs/AI_SECURITY_ARCHITECTURE.md`,
`docs/INCIDENT_REVERSE_ENGINEERING.md`, and `docs/HELP.md`.

## Architecture

```text
React Console (frontend/src/main.jsx, 15s poll)
      |
FastAPI API (backend/app/api/routes.py)
      |
  +---+------------------------------------------------------------------+
  | risk | graph | assess | forensics | visibility | teams | seed |
  +---+------------------------------------------------------------------+
      |
  SQLAlchemy models (backend/app/models/entities.py) → PostgreSQL
```

## Repository structure — what each file does

```text
backend/
  Dockerfile              # backend image (uvicorn app.main:app:8000); rebuild after any backend change
  requirements.txt        # fastapi, uvicorn, sqlalchemy, psycopg, httpx, python-multipart, pytest
  .env.example            # DATABASE_URL, CORS_ORIGINS, APP_ENV
  app/
    main.py               # FastAPI app factory: lifespan (create_all + seed), CORS, router, /health
    db.py                 # engine/SessionLocal/Base/get_db; Postgres w/ sqlite fallback
    models/
      __init__.py         # re-exports (import side effect registers tables; keep in sync w/ routes+seed)
      entities.py         # 20 tables: Asset Service Identity SessionEvent NetworkFlow ThreatIntel
                          #   CloudResource AIAsset Finding Incident AuditEvent Device DnsQuery LoginAttempt
                          #   CveRecord UsbEvent DlpEvent RetrievalEvent SoarRun DiscoveredHost
    api/
      routes.py           # ALL /api/* endpoints (see table below) + safety gates (caps, approval, cooldown)
    services/
      risk.py             # calculate_risk() weighted formula + severity() bands (≥80/≥60/≥35)
      seed.py             # idempotent demo dataset (4 assets → findings → intel → cloud → AI)
      graph.py            # build_graph() / attack_paths() BFS+risk+chokepoints / answer_question() 6 kinds
      assess.py           # TOOL_CATALOG, validate_target/is_lab_host/check_cooldown/score_headers/assess_web_posture
      forensics.py        # analyze_bytes() + _parse_{eml,ooxml,pe,elf,pcap} + KALI_FORENSICS_CATALOG
      visibility.py       # brute_force_candidates() (≥5 fails) + browsing_summary()
      discovery.py        # OUI table + vendor_for_mac() + upsert_discovery() (MAC-first identity)
      teams.py            # SEVERITY_PLAYBOOKS + CATEGORY_PLAYBOOKS(17) + RED_TEAM + BLUE_TEAM doctrine
      threatintel.py      # parse_kev_csv()/parse_nvd() + refresh_kev()/refresh_nvd() + 24h auto-refresh loop
      mitre.py            # TECHNIQUES(16) + map_finding() rules + coverage()
      cloud_adapters.py   # ADAPTERS + import_prowler() + aws_live_scan() (injected clients, read-only)
      ai_red.py           # PROBES battery + refused() + evaluate() (lab/private + approval only)
      vectordb.py         # check_retrieval() tenant policy + log_retrieval() (deny → HIGH finding)
      soar.py             # PLAYBOOKS(4) + run_playbook()/approve_run() (approval-gated, DB-safe actions)
  tests/                  # test_risk/test_v12/test_forensics/test_visibility/test_teams/test_production (31 total)
frontend/
  Dockerfile              # Node 22 + Vite dev :3000; VITE_API_URL → backend
  src/main.jsx            # whole console: nav, SEV_HELP/why*() explainers, 21 views incl. WifiPanel/ThreatPanels/
                          # CloudOpsPanel/AiOpsPanel/UsbDlpPanel/SoarPanel, DrillModal/DetailModal (16 kinds)
  src/styles.css          # dark theme + clickable/modal/helpbar styles
collectors/
  endpoint-agent.py       # consented agent (stdlib only): heartbeat, ports, USB, DLP-lite → heartbeat/dlp ingest
                          # + `--discover auto [--interval N --yes]` Wi-Fi sweep → discovery ingest (private ranges only)
lab/
  vulnerable-web/app.py   # intentional training target (headers/admin/robots/AI echo); nobody user
  collector.py            # consented device collector (arp passive; --active lab CIDR w/ YES confirm)
  red_blue_demo.py        # approved assessment → ingest attack telemetry → verify attack paths
docs/
  LAB_GUIDE.md / NETWORK_VISIBILITY_GUIDE.md / FORENSICS_GUIDE.md / POC_ROADMAP.md
docker-compose.yml        # postgres + backend + frontend (bridge network, pg volume)
docker-compose.lab.yml    # overlay: vulnerable-web (cap_drop ALL, read-only, cpu/mem caps)
```

## Function / class dependency map

| Function / class | Lives in | Depends on (inputs) | Used by (dependents) |
|---|---|---|---|
| `calculate_risk()`, `severity()` | `services/risk.py` | nothing (pure) | `seed.py`, `POST /api/risk/calculate`; bands feed `SEV_HELP` (frontend) + `SEVERITY_PLAYBOOKS` (`teams.py`) — keep ≥80/≥60/≥35 in sync |
| `seed(db)` | `services/seed.py` | all models, `risk` | `main.lifespan` (once per fresh DB) |
| `build_graph(db)` | `services/graph.py` | Session; Asset→Service→Identity→Session→Flow→Cloud→AI→Finding tables | `attack_paths()`, `answer_question()`, `GET /api/graph` |
| `attack_paths(db)` | `services/graph.py` | `build_graph`, `_adjacency`, `_is_sensitive` | `GET /api/graph/attack-path`, GraphView, demo script |
| `answer_question(db, kind)` | `services/graph.py` | per-kind tables | `GET /api/graph/answer` (6 kinds) |
| `validate_target/is_lab_host/check_cooldown/score_headers/assess_web_posture` | `services/assess.py` | `httpx`; called in that order by the route | `POST /api/assessments/web` (findings + audit on success) |
| `analyze_bytes() + _parse_*` | `services/forensics.py` | bytes only (stdlib struct/zipfile/email) | `POST /api/forensics/analyze` (audit-logged, memory-only) |
| `brute_force_candidates()`, `browsing_summary()` | `services/visibility.py` | `LoginAttempt` / `DnsQuery` rows | `GET /api/logins/summary`, `GET /api/dns/top`, Identity/Endpoint views, triage |
| `OUI`, `vendor_for_mac()`, `upsert_discovery()` | `services/discovery.py` | `DiscoveredHost` rows | `POST /api/ingest/discovery`, `GET /api/discovery/*`, Network Wi-Fi panel |
| KEV/NVD `parse_*` (pure) + `refresh_*` (injected fetch) | `services/threatintel.py` | CISA CSV / NVD 2.0 payloads | `POST /api/threat-intel/refresh`, 24h loop, `CveRecord` + mirrored intel |
| `TECHNIQUES`, `map_finding()`, `coverage()` | `services/mitre.py` | `Finding` rows | `GET /api/mitre/*`, Ops MITRE panel |
| `import_prowler()`, `aws_live_scan()` (injected clients) | `services/cloud_adapters.py` | Prowler JSON / boto3 (optional) | `POST /api/cloud/import-prowler|/scan` |
| `PROBES`, `refused()`, `evaluate()` | `services/ai_red.py` | lab gateway HTTP (injected post) | `POST /api/ai/evaluate` (lab/private + approval) |
| `check_retrieval()`, `log_retrieval()` | `services/vectordb.py` | `AIAsset` owners | `POST|GET /api/ai/retrieval-audit` |
| `PLAYBOOKS`, `run_playbook()`, `approve_run()` | `services/soar.py` | Asset/Session/Incident/ThreatIntel | `POST|GET /api/soar/*`, Governance panel |
| `SEVERITY_/CATEGORY_PLAYBOOKS`, `RED_/BLUE_TEAM` | `services/teams.py` | `risk` bands (must match) | `GET /api/remediation`, `GET /api/teams/*`, Red/Blue views |
| `get_db`, `Base/engine/SessionLocal` | `app/db.py` | `DATABASE_URL` env | every route + `lifespan` |
| Entity classes (14) | `models/entities.py` | `app.db.Base` | routes, services, seed (via `models/__init__.py`) |
| `DrillModal` / `DetailModal`, `why*()` | `frontend/src/main.jsx` | API state (assets, findings, …) | every clickable tile/row |

## API endpoints

Inventory & posture: `GET /health`, `/api/overview`, `/api/assets`, `/api/network/ports`, `/api/network/flows`, `/api/findings`, `/api/incidents`, `/api/audit`, `/api/identities`, `/api/sessions`, `/api/threat-intel`, `/api/cloud/resources`, `/api/ai/assets`, `/api/devices`, `/api/dns/top`, `/api/logins/attempts`, `/api/logins/summary`, `/api/discovery/hosts`, `/api/discovery/summary`
Graph: `GET /api/graph`, `/api/graph/attack-path?max_paths=`, `/api/graph/answer?kind=` (internet_to_data|connection_owner|port_owner|privileged_access|ai_data_access|cloud_exposure)
Ingest (capped batches, audit-logged, optional `COLLECTOR_TOKEN` gate): `POST /api/ingest/{network-flows,sessions,services,devices,dns,logins,usb,dlp,discovery}` + `POST /api/collector/heartbeat` (agent sync)
Assess & intel: `POST /api/risk/calculate`, `/api/ai/investigate` (advisory), `/api/assessments` (approval job), `/api/assessments/web` (passive + approval gate + cooldown), `GET /api/tools/catalog`
Threat & MITRE: `POST /api/threat-intel/refresh`, `GET /api/threat-intel/cves`, `GET /api/mitre/{techniques,coverage}`
Cloud & AI & response: `GET /api/cloud/adapters`, `POST /api/cloud/{import-prowler,scan}`, `GET /api/ai/probes`, `POST /api/ai/evaluate`, `POST|GET /api/ai/retrieval-audit`, `GET /api/soar/playbooks`, `POST|GET /api/soar/runs`, `POST /api/soar/runs/{id}/approve`
Forensics & teams: `POST /api/forensics/analyze` (5 MB, memory-only), `GET /api/forensics/tools`, `GET /api/remediation?severity=&category=`, `GET /api/teams/{red,blue}`, `POST /api/session/triage`

## Scope check — requested roadmap vs current state (v1.5: all items production-built)

| Requested item | Status | What exists | Operate / extend |
|---|---|---|---|
| Live NVD/CISA ingestion | ✅ Built | `services/threatintel.py` (pure parsers + injected-fetch refresh), `CveRecord` + mirrored intel, refresh endpoint, optional 24h loop | Set `THREATINTEL_AUTO_REFRESH=true` or cron the endpoint; add `NVD_API_KEY` for rate |
| MITRE correlation | ✅ Built | 16-technique base (14 enterprise + 2 labelled ATLAS concepts), rule mapper, `GET /api/mitre/coverage`, Ops panel | Extend `TECHNIQUES` + `map_finding` rules as new finding shapes appear |
| Attack-path analysis | ✅ Built | BFS + per-path risk + choke-point ranking, 3 endpoints, GraphView, tests | Tune `max_depth`; schedule recompute if telemetry grows |
| Endpoint collector | ✅ Built | `collectors/endpoint-agent.py` (heartbeat/ports/USB/DLP-lite, stdlib-only) + token-gated heartbeat | Deploy via cron/launchd; set `COLLECTOR_TOKEN` |
| Cloud adapters | ✅ Built | Prowler-JSON import + live read-only AWS scan (S3/SG/IAM), registry endpoint, Cloud panel | Add `AWS_*` read-only creds for live scan; add providers to `ADAPTERS` |
| AI security testing | ✅ Built | 7-probe battery (lab/private + approval), findings on fail, probes metadata endpoint | Point at lab gateway, approve, re-run to LOW before release |
| Vector DB security | ✅ Built | Tenant policy (`owner` vs requesting tenant), deny→HIGH finding, retrieval audit log + panel | Tag each vector store `owner` = tenant; review denials |
| USB/DLP | ✅ Built | `UsbEvent`/`DlpEvent` + auto-findings + agent collection + Endpoint panels | Authorise expected devices; close DLP gaps per playbook |
| SOAR | ✅ Built | 4 playbooks, pending→approved→completed runs, DB-safe actions, Governance panel | Wire perimeter/IAM webhooks behind the same gate as next step |

Remaining operational work (not features): HTTPS termination, Postgres backups, OIDC/RBAC, K8s manifests — see `docs/PRODUCTION_GUIDE.md` and `docs/POC_ROADMAP.md` slices 11–13.

## v1.6 — Administrator-only Ethical Hacking Control Plane

VEYRA now includes a dedicated administrator-only ethical-hacking tool registry.
The registry covers network discovery, attack-surface mapping, web/API testing,
identity assessment, credential auditing, exploit-validation frameworks,
packet analysis, vulnerability management, AppSec/IaC, cloud/Kubernetes,
endpoint/DFIR, malware/reverse engineering, threat intelligence, detection
engineering and AI security.

The admin APIs are protected by `VEYRA_ADMIN_TOKEN` in this POC. High-impact pentest tools additionally require `VEYRA_PRIVILEGED_ADMIN_TOKEN` (second gate; production should use PAM/MFA). Non-admin users
are not shown the Ethical Hacking section and are rejected by the backend with
HTTP 403. Production must replace the POC token with OIDC/SSO + MFA + RBAC/ABAC
and privileged-access management.

**Important:** tool registration is not equivalent to authorization. VEYRA
stages approved work for isolated workers; it does not expose arbitrary shell,
exploit replay, payload delivery, credential attacks, persistence, C2 or
hack-back through the browser/API.

See `docs/ADMIN_ETHICAL_HACKING.md`.

## v1.6 — Current AI-security direction (September 2026)

The roadmap now explicitly includes the **OWASP Agent Control Standard (ACS)**,
OWASP GenAI LLM Top 10 2026, OWASP Top 10 for Agentic Applications 2026, the
OWASP GenAI Security Industry Framework Crosswalk, MCP authorization/policy,
A2A trust controls, OpenTelemetry GenAI/agent traces, Graph RAG, memory security,
AI supply-chain provenance and continuous AI red-team regression. NIST AI RMF
critical-infrastructure alignment is also included.

See `docs/AI_LATEST_2026.md` and `docs/AI_SECURITY_ARCHITECTURE.md`.


## v1.7 — Governed Security Tool Execution & Evidence Plane

The admin ethical-hacking area now includes a governed job/evidence control plane. Administrators can create a tool contract, define explicit scope and approval ticket, approve it, queue it for an independently isolated worker, and ingest normalized evidence with provenance and SHA-256 artifact hashing.

**Important:** the FastAPI service never launches Nmap, Metasploit, Burp, credential-audit tools, malware, payloads, shells or arbitrary commands. Execution belongs to a separately authenticated worker that must re-check authorization and isolation policy.

Lifecycle: `Admin → Tool Registry → Scope/Policy → Approval → Job Contract → Isolated Worker Queue → Evidence/Provenance → Findings/Security Graph`.

## v1.8 — AI / Agent Security Control Plane

VEYRA now includes dedicated coverage for enterprise GenAI, agentic AI, MCP-connected agents, A2A workflows, RAG/vector stores and internally developed/local agents. The AI Security console provides a governed integration catalog, control domains and deterministic local-agent posture assessment.

New governed AI security integrations include **NeuralTrust, Lakera Guard / Check Point AI Guardrails, TrojAI, CalypsoAI / F5 AI Security, Garak, Promptfoo, Adversarial Robustness Toolbox, HiddenLayer, Robust Intelligence and NeMo Guardrails**.

The architecture aligns to the current **OWASP GenAI LLM Top 10 2026, OWASP Agentic Applications 2026 and OWASP Agent Control Standard**, alongside MITRE ATLAS and NIST AI RMF. See `docs/AI_AGENT_SECURITY_CONTROL_PLANE.md`.

### v1.8 worker boundary

The governed execution plane now has a separate worker-to-control-plane boundary. Worker authentication uses `VEYRA_WORKER_TOKEN`; job contracts can be signed with `VEYRA_WORKER_SIGNING_SECRET`. The API accepts normalized evidence rather than arbitrary commands. Production workers should run in isolated infrastructure with network egress controls, ephemeral credentials, resource limits and independent authorization.

## v1.9 — AI Security Gateway & Agent Runtime

VEYRA now includes a deterministic AI Security Gateway for organization-owned GenAI applications, agentic AI, MCP-connected agents, A2A workflows and local agents. It provides agent enrollment, operation/tool allowlists, risk thresholds, high-impact approval gates, prompt/context risk checks, trace IDs and runtime evidence hashing. The gateway is a control boundary; it does not execute model or tool side effects. See `docs/AI_GATEWAY_RUNTIME.md`.

The runtime telemetry vocabulary is designed to align with current OpenTelemetry GenAI agent conventions (`invoke_agent`, `plan`, `retrieval`, memory and tool execution) and the OWASP Agent Control Standard's inspectability, traceability, instrumentation and runtime-control principles.


## v2.0 — VEYRA AI Security Fabric

VEYRA v2.0 unifies the platform into a cross-plane security fabric covering observation, detection, intelligence, response and governance. The new Security Fabric view correlates endpoint/network/identity/cloud/AI telemetry, governed security-tool jobs, evidence and agent runtime events.

The fabric adds a deterministic AI attack-path engine for organization-owned identities, local/internal agents, AI applications, vector stores, tools and cloud resources. It exposes `GET /api/fabric/overview`, `POST /api/fabric/events`, `GET /api/fabric/events` (admin), and `GET /api/fabric/ai-attack-paths` (admin).

AI governance is aligned with the current OWASP Agent Control Standard, OWASP Agentic Applications 2026 and NIST AI RMF / GenAI Profile. OWASP ACS emphasizes inspectability, traceability, instrumentation and runtime control; NIST's GenAI Profile provides lifecycle-oriented risk-management guidance.

See `docs/SECURITY_FABRIC_V20.md`.


## v2.1 — Autonomous Security Operations Fabric

Added an evidence-first autonomous SOC pipeline: alert → evidence preservation → deterministic correlation → attack-path reasoning → AI investigation → evidence bundle → risk/confidence → human approval → governed SOAR → verification → closure/learning. AI remains advisory; authorization, severity, provenance and consequential actions remain deterministic and approval-gated. See `docs/AUTONOMOUS_SOC_V21.md`.


## v2.2 — Continuous Detection & Response Mesh

VEYRA v2.2 adds a continuous detection/response mesh connecting normalized telemetry, deterministic detections, autonomous investigations, approval-gated response and post-action verification. See `docs/DETECTION_RESPONSE_MESH_V22.md`.

## v2.3 — Autonomous Investigation & Threat Intelligence Fusion

VEYRA v2.3 connects the Detection Mesh and Autonomous SOC to an evidence-first intelligence fusion layer. Investigations can now correlate locally ingested threat intelligence, map behavior to MITRE ATT&CK / ATLAS, preserve provenance references, and produce confidence-scored attribution hypotheses.

**Important:** attribution is hypothesis-only. VEYRA does not claim an attacker identity from weak evidence, and AI does not authorize response actions. Human approval and deterministic policy remain authoritative.

See `docs/INTEL_FUSION_V23.md`.

## v2.4 — Autonomous Pentesting Agents & AI Tooling

VEYRA v2.4 introduces a governed AI pentest-planning layer. The `veyra-pentest-agent` converts an authorized natural-language objective into a deterministic tool chain, records explicit scope and approval metadata, and hands the plan to an isolated worker boundary. It does not expose arbitrary shell execution or automatic exploit/WAF-bypass payload generation.

AI-enhanced traditional tooling covers result triage, evidence correlation, finding clustering, malware-analysis summarization and next-step planning. See `docs/PENTEST_AGENTS_V24.md`.

## v2.4 tool access hardening

VEYRA v2.4 contains an 85-tool governed security catalog. All ethical-hacking tools are admin-only. High-impact tools are additionally classified as `privileged_admin` and require a second privileged-admin authorization gate before staging, approval or dispatch. See `docs/TOOL_ACCESS_MATRIX_V24.md`.

The catalog is an integration/governance layer; third-party binaries such as Nmap, Metasploit, Burp Suite, SQLMap, Wireshark and Hashcat are not bundled into the web application container. Approved versions should run in isolated security workers.

## v2.5 — Identity, Passwords & Click-to-Select Tool Permissions

VEYRA now includes a console identity layer and a comprehensive **User & Permissions** page. The design uses one and only one `sudo` account; all other accounts use lower roles (`security_admin`, `security_operator`, `analyst`, `viewer`). The sudo administrator can create users, change roles, enable/disable accounts, change tool permissions and manage the security-tool access matrix without terminal commands.

Per-tool access is selected by clicking one of four levels: **No access**, **View**, **Plan**, or **Request execution**. High-impact tools remain marked **Privileged Admin** and retain the platform's approval/isolated-worker boundary.

Users can change their own password from **My Password**. Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes in the POC, with a 12-character minimum. Production should use enterprise OIDC/SAML + MFA/WebAuthn and PAM.

See:
- `docs/IDENTITY_PERMISSIONS_V25.md`
- `docs/COMPLETE_TOOL_EDUCATION_GUIDE_V25.md`

## v2.5.1 — Wi-Fi + LAN Visibility

Network now has separate **Nearby Wi-Fi Networks** and **My LAN Devices** windows, with a Router Mode A/B dropdown. Nearby Wi-Fi uses the read-only local Wi-Fi sensor; LAN devices use the VEYRA discovery/endpoint collector. Devices can be marked Trusted/Untrusted from the GUI. Unexpected-device investigation is evidence-first and does not perform deauthentication, attacks, or disruption.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).

## Documentation index

| Document | What it explains |
|---|---|
| [`docs/CODEBASE_GUIDE_V27.md`](docs/CODEBASE_GUIDE_V27.md) | **Complete source-code/file/folder help guide** — start here when you want to understand what every implementation file does. |
| [`docs/TOOL_HELP_CATALOG_V27.md`](docs/TOOL_HELP_CATALOG_V27.md) | **Per-tool help for all 477 catalog entries** — purpose, safe workflow, access tier, evidence and common mistakes. |
| [`docs/TOOL_ECOSYSTEM_V27.md`](docs/TOOL_ECOSYSTEM_V27.md) | Tool catalog, Marketplace, worker architecture and provenance. |
| [`docs/COMPLETE_TOOL_EDUCATION_GUIDE_V25.md`](docs/COMPLETE_TOOL_EDUCATION_GUIDE_V25.md) | Tool-by-tool educational guidance. |
| [`docs/TOOL_RUNNER_V26.md`](docs/TOOL_RUNNER_V26.md) | Tool Runner permissions, requests, approvals and execution lifecycle. |
| [`docs/NETWORK_VISIBILITY_GUIDE.md`](docs/NETWORK_VISIBILITY_GUIDE.md) | Wi-Fi/LAN visibility and trusted-device workflow. |
| [`docs/IDENTITY_PERMISSIONS_V25.md`](docs/IDENTITY_PERMISSIONS_V25.md) | Sudo, users, passwords and tool permissions. |
| [`docs/PRODUCTION_GUIDE.md`](docs/PRODUCTION_GUIDE.md) | Production secrets, deployment and hardening. |
| [`TERMINAL_RUNBOOK.md`](TERMINAL_RUNBOOK.md) | Terminal setup, commands, health checks and troubleshooting. |
| [`TODO.md`](TODO.md) | Current engineering backlog and known limitations. |


## Understanding every piece of the code

If you are maintaining VEYRA yourself, do not rely on memory or scattered comments. The release now ships two generated references:

- **`docs/CODEBASE_GUIDE_V27.md`** — file/folder inventory plus Python classes/functions, API symbols, frontend components, feature-to-code map, and maintenance rules.
- **`docs/TOOL_HELP_CATALOG_V27.md`** — help cards for every registered security tool.

Use them together: find the feature in the codebase guide, then use the Tool Help Catalog for the security-tool behavior and governance model. The backend remains authoritative for permissions even if a UI control is hidden.

## v2.8 — Cutting-edge AI Security Ecosystem

VEYRA v2.8 adds **111 AI-security integration candidates** across LLM red teaming, agent security, MCP/A2A, RAG, vector databases, adversarial ML, AI supply chain, observability, governance and AI incident response. Together with the 477 extended security-tool catalog, the platform now exposes a 588-entry governed tool ecosystem.

Read:

- `docs/AI_ECOSYSTEM_V28.md` — AI security capabilities and architecture
- `docs/SECURITY_WORKER_FABRIC_V28.md` — managed worker architecture
- `docs/CODEBASE_GUIDE_V27.md` — codebase orientation
- `docs/TOOL_HELP_CATALOG_V27.md` — per-tool help

The **AI Ecosystem** UI provides searchable AI security integrations. The **Security Workers** UI tracks managed worker nodes and worker-reported tool state. The **Tool Marketplace** combines the general and AI catalogs.

The SaaS control plane does not expose arbitrary shell execution. Actual third-party tools belong on managed, isolated workers under scope, RBAC/Sudo, approval, provenance, version pinning, SBOM and evidence controls.


## VEYRA v3.0 — Adversary Intelligence & Wireless Defense Fabric

- First-class Wireless Security Center: AP/client inventory, trusted baseline, rogue candidates and evidence workflow.
- Attack Timeline: cross-source chronology across flows, sessions and audit events.
- Infrastructure Investigation: service → process → PID → user attribution plus high-risk flow review.
- Attribution & Evidence: hypothesis-only attribution, supporting/contradicting evidence, and evidence-bundle staging.
- Defensive boundary: no hack-back, credential capture, deauthentication, persistence, disruption or unrestricted shell execution through these surfaces.
- New API: `/api/v29/overview`, `/api/v29/wireless`, `/api/v29/timeline`, `/api/v29/infrastructure`, `/api/v29/attribution`, `/api/v29/evidence-bundle`.

## v3.0 — Full Security Operations Fabric

VEYRA v3.0 adds a unified operational layer across the existing security ecosystem. The new **Full Security Fabric**, **Unified Security Graph**, **AI Attack Reconstruction**, **AI SOC Investigator**, and **Governed Response & Recovery** views connect telemetry into a single defensive lifecycle.

The new orchestration service is `backend/app/services/v3_fabric.py` and the frontend module is `frontend/src/v3.jsx`.

See [`docs/SECURITY_OPERATIONS_FABRIC_V30.md`](docs/SECURITY_OPERATIONS_FABRIC_V30.md) and [`V3_RELEASE_NOTES.md`](V3_RELEASE_NOTES.md).


## v3.2 — Team Security Academy & Documentation Fabric

VEYRA v3.2 adds a role-based Team Security Academy and makes per-tool documentation a release requirement. The registry contains 577 security tools/integrations and every registered entry now has an individual Markdown help page under `docs/tools/`. Each page explains what the tool does, why VEYRA uses it, when to use it, the UI workflow, terminal starting point, permissions, scope, evidence, interpretation, remediation, verification and common mistakes.

New documentation:
- `docs/TOOL_HELP_INDEX_V32.md`
- `docs/TEAM_OPERATIONS_PLAYBOOK_V32.md`
- `docs/tools/*.md` (one file per registered tool)
- `docs/AI_CUTTING_EDGE_2026_TEAM_GUIDE.md`

New API:
- `GET /api/v32/academy/overview`
- `GET /api/v32/academy/curriculum/{track}`

The execution model remains: identity → role → scope → approval → managed worker → evidence → audit.

## v3.1.1 — Complete Tool Help & Cutting-Edge AI Security

The team-facing tool manual now documents every catalog entry with:

- what the tool does;
- why VEYRA uses it;
- how to use it from the UI;
- a safe terminal starting point;
- expected evidence;
- common mistakes;
- the recommended next step.

The AI-security baseline also covers current LLM red teaming, agent evaluation, MCP/A2A security, agent skills, guardrails, observability, RAG, model artifact security, adversarial ML and AI supply-chain tooling. See `docs/TOOL_USAGE_CATALOG_V31.md` and `docs/AI_CUTTING_EDGE_2026_TEAM_GUIDE.md`.

## v3.3 Security Readiness
VEYRA v3.3 adds the Security Readiness Center, defensive team exercise library, AI security control matrix and automated per-tool documentation validation. See `docs/SECURITY_READINESS_V33.md` and `docs/RELEASE_CHECKLIST_V33.md`.


## v3.4 — Security Intelligence & Continuous Validation
VEYRA v3.4 adds a Continuous Validation control plane that turns inventory, telemetry, documentation and security-control metadata into repeatable, governed validation plans. It adds defensive priority signals, control-test scheduling metadata, AI runtime/data validation domains, and production hardening guidance. Actual security-tool execution remains scoped to authorised managed workers behind Sudo/approval/evidence controls.

See `docs/SECURITY_INTELLIGENCE_V34.md` and `docs/PRODUCTION_HARDENING_V34.md`.

## VEYRA v3.5 Security Lifecycle

The platform now uses the operating model: **Discover → Understand → Validate → Investigate → Correlate → Contain → Recover → Prove → Learn → Continuously revalidate.** See `docs/SECURITY_LIFECYCLE_V35.md` and `docs/OPERATING_MODEL_V35.md`.

## v3.7 — Security Graph Intelligence

VEYRA v3.7 adds a read-only Security Graph Intelligence layer. It correlates assets, identities, cloud resources, AI assets, findings, incidents, governed jobs and evidence receipts; surfaces hotspots/chokepoints; maps operational signals to security controls; and detects basic stale-evidence/remediation drift.

New APIs:
- `GET /api/v37/security-graph/intelligence`
- `GET /api/v37/security-graph/control-evidence`

New UI: **Graph Intelligence**.

## v3.8 — Security Posture Time Machine & AI/Endpoint Intelligence

VEYRA v3.8 adds temporal security posture, remediation proof and an ecosystem radar spanning frontier AI providers and Windows/macOS/Linux endpoints.

New APIs:
- `/api/v38/posture/current`
- `/api/v38/posture/history`
- `/api/v38/posture/changes`
- `/api/v38/posture/drift`
- `/api/v38/posture/remediation-proof`
- `/api/v38/posture/snapshot`
- `/api/v38/ai-endpoint-radar`

New UI: **Posture Time Machine**.

Research and operating model: `docs/SECURITY_POSTURE_TIME_MACHINE_V38.md` and `docs/AI_PROVIDER_AND_ENDPOINT_RADAR_V38.md`.

## v3.9 — Autonomous Exposure Validation Fabric

VEYRA v3.9 adds the **AI Security Research Lab** and continuous exposure validation across Windows, macOS, Linux, Kubernetes, Cloud and AI agents.

Core loop:

`Fingerprint → Correlate → Validate → Investigate → Contain (approval) → Remediate → Independently Prove → Revalidate`

New capabilities:
- rogue-agent candidate detection and investigation
- agent identity/tool/policy anomaly correlation
- endpoint + identity + network + AI correlation
- evidence-backed attack timeline reconstruction
- root-cause hypotheses with confidence boundaries
- approval-only containment plans
- Windows/macOS/Linux/Kubernetes/Cloud exposure matrix
- independent remediation-proof model
- AI Research Lab UI

Security boundary: no arbitrary SaaS shell, credential theft, persistence, destructive action, exploit delivery or hack-back capability.
