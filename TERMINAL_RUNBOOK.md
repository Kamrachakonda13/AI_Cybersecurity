# VEYRA v2.7 — Terminal Runbook (end to end)

Copy-paste commands to go from zero to a fully working platform with all tools.
Run everything from the project root:

```bash
cd /path/to/VEYRA_POC_v2_5_1_WiFi_LAN_Visibility
```

Prerequisites: Docker Desktop, `python3`, Xcode command-line tools
(`xcode-select --install` — needed for Wi-Fi network names on modern macOS).

---

## 1. First-time setup (once)

```bash
# 1a. Create backend env from the template
cp backend/.env.example backend/.env

# 1b. Set the sudo bootstrap login (12+ char password).
#     These seed the single `sudo` account on FIRST startup only.
#     Never commit real credentials to Git or package them in a ZIP.
grep -E "AEGISX_SUDO" backend/.env
# AEGISX_SUDO_USERNAME=sudo.admin
# AEGISX_SUDO_PASSWORD=<strong-12+-character-secret>

# 1c. Verify docker is up
docker --version && docker compose version
```

> After first login, change the password via **My Password** in the console,
> then remove/rotate the bootstrap values per `docs/IDENTITY_PERMISSIONS_V25.md`.

## 2. Start the platform

```bash
# 2a. Build + start postgres, backend, frontend (detached)
docker compose up --build -d

# 2b. Watch it come up
docker compose ps
docker compose logs --tail=20 backend

# 2c. Health checks (backend seeds demo data on fresh DB)
curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/overview
curl -s -o /dev/null -w "frontend:%{http_code}\n" http://localhost:3000/
```

| Service  | URL                          |
|----------|------------------------------|
| Console  | http://localhost:3000        |
| API docs | http://localhost:8000/docs   |
| Health   | http://localhost:8000/health |

## 3. Log in (admin)

Console → log in as `Kam` / your sudo password. First login forces a password
change (`must_change_password: true`). Manage users at **User & Permissions**
(sudo only). CLI equivalent:

```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Kam","password":"<your-password>"}'
```

## 4. Wi-Fi sensor (Nearby Wi-Fi Networks panel)

The browser cannot touch the Wi-Fi radio; a tiny read-only localhost sensor
(`collectors/endpoint-agent.py --sensor`, port 8765) feeds the Scan button.
On modern macOS, SSIDs resolve via the Apple-signed swift runner
(`collectors/wifi-scan-jit.swift`) — no per-app Location approval needed.

```bash
# 4a. Manual run (foreground, for testing)
python3 collectors/endpoint-agent.py --sensor
# → VEYRA local Wi-Fi sensor listening on http://127.0.0.1:8765

# 4b. Verify it (second terminal)
curl -s http://127.0.0.1:8765/health
curl -s "http://127.0.0.1:8765/wifi/scan" | python3 -m json.tool | head -n 20

# 4c. Permanent install — auto-start at every login (already done on this Mac)
cp installers/com.aegisx.wifi-sensor.plist ~/Library/LaunchAgents/com.aegisx.wifi-sensor.plist
launchctl load ~/Library/LaunchAgents/com.aegisx.wifi-sensor.plist
launchctl list | grep aegisx   # → com.aegisx.wifi-sensor running
curl -s http://127.0.0.1:8765/health

# 4d. Then in console: Network → Scan nearby Wi-Fi
```

## 5. LAN device discovery (My LAN devices panel)

```bash
# 5a. Sweep YOUR OWN private LAN (asks nothing with --yes; refuses non-private ranges)
python3 collectors/endpoint-agent.py --discover auto --yes --once

# 5b. Verify what landed
curl -s "http://localhost:8000/api/discovery/summary"
curl -s "http://localhost:8000/api/discovery/hosts?limit=200" \
  | python3 -c "import sys,json; [print(r['ip_address'],'|',r.get('hostname'),'|',r.get('mac'),'|',r.get('vendor')) for r in json.load(sys.stdin)]"
```

Names resolve via unicast rDNS → mDNS/Bonjour → NetBIOS. Phones with
randomized MACs may stay `host-...` — identify by elimination, then **Trust**
known devices in the console to build the baseline.

## 6. Endpoint agent (heartbeat sync)

```bash
# 6a. One-shot sync: hostname/IPs/MAC/ports/USB/DLP-lite → /api/collector/heartbeat
python3 collectors/endpoint-agent.py --api http://localhost:8000 --once

# 6b. Daemon mode (every 5 min) + periodic LAN re-sweep (every 30 min)
python3 collectors/endpoint-agent.py --discover auto --interval 1800 --yes
```

## 7. Lab device collector (passive arp)

```bash
# 7a. Preview only — parses YOUR arp table, sends nothing
python3 lab/collector.py --api http://localhost:8000 --dry-run

# 7b. Ingest neighbours with owner tag
python3 lab/collector.py --api http://localhost:8000 --post --owner "Blue team"

# 7c. Active lab ping-sweep (private /16-or-smaller only, prompts YES)
python3 lab/collector.py --active 192.168.0.0/24 --post
```

## 8. Red vs Blue demo (needs lab target overlay)

```bash
# 8a. Rebuild with lab overlay if you want vulnerable-web :4101
#     (this project ships base compose only; see docs/LAB_GUIDE.md)
curl -s http://localhost:4101/   # lab target when present

# 8b. End-to-end demo: governed assessment → attack telemetry → attack paths
python3 lab/red_blue_demo.py
python3 lab/red_blue_demo.py --api http://localhost:8000 --target http://localhost:4101
```

## 9. Backend tests

```bash
cd backend && PYTHONPATH=. python3 -m pytest tests -q
```

## 10. Frontend build check

```bash
cd frontend && npm install && npm run build
```

## 11. Key API calls (curl cookbook)

```bash
API=http://localhost:8000

# Inventory & posture
curl -s $API/api/overview
curl -s $API/api/findings | head -c 500; echo
curl -s "$API/api/graph/attack-path?max_paths=5" | head -c 500; echo
curl -s "$API/api/graph/answer?kind=internet_to_data" | head -c 500; echo

# Governed web assessment (lab/private needs approval_confirmed:true)
curl -s -X POST $API/api/assessments/web \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost:4101","approval_confirmed":true}'

# Threat intel + MITRE
curl -s -X POST $API/api/threat-intel/refresh | head -c 300; echo
curl -s $API/api/mitre/coverage | head -c 300; echo

# AI investigation (advisory, evidence-first)
curl -s -X POST $API/api/ai/investigate \
  -H "Content-Type: application/json" \
  -d '{"question":"Investigate the latest critical finding"}' | head -c 500; echo

# Local agent gateway example (needs AEGISX_AI_GATEWAY_TOKEN env)
AEGISX_AI_GATEWAY_TOKEN=change-me-ai-gateway AEGISX_URL=http://localhost:8000 \
  python3 examples/local_agent_gateway.py
```

Full endpoint map: `README.md` → "API endpoints", or open `/docs`.

## 12. Stop / reset

```bash
docker compose down            # stop, keep postgres data
docker compose down -v         # stop + WIPE postgres volume (fresh seed next start)
docker compose logs -f backend # follow backend logs
```

## 13. Troubleshooting

| Symptom | Fix |
|---|---|
| `Bind for 0.0.0.0:5432 failed` | Another stack holds the ports: `docker ps`, then `docker compose down` in the OLD project dir (or `docker stop <name>`) |
| Backend `failed to resolve host 'postgres'` / containers lose network | `docker compose down && docker compose up --build -d` (Docker Desktop network glitch) |
| Frontend blank + `vite:oxc ... already been declared` | Duplicate icon import in `frontend/src/main.jsx` — remove the dup, `docker compose up --build -d frontend` |
| `SENSOR OFFLINE` / empty Wi-Fi list | Sensor not running: §4 (`launchctl list \| grep aegisx`, else manual run) |
| `Invalid username or password` on fresh DB | Backend missing sudo env: check `AEGISX_SUDO_*` in `docker-compose.yml` + `backend/.env`, then `docker compose up -d backend` (seeds only when `user_accounts` is empty) |
| Wi-Fi rows without names | Needs Xcode CLT (`xcode-select --install`); sensor uses `collectors/wifi-scan-jit.swift` via `/usr/bin/swift` |
| LAN devices all `host-...` | Router has no local DNS; mDNS/NetBIOS auto-tried on sweep — phones may never answer; identify + Trust manually |
| BSSID column `—` | Withheld by macOS without a persisting Location grant; SSIDs are unaffected |

Safety: collectors scan **only your own** private LAN; assessments are
passive + approval-gated; nothing here attacks, exploits, or monitors
third-party networks. See `docs/NETWORK_VISIBILITY_GUIDE.md`.

## 14. Tool Runner + Tool Marketplace (v2.7)

The console now exposes the expanded security-tool catalog. The UI is intentionally
Kali-like — search, select a tool, choose named profiles, review scope and submit.
There is no arbitrary browser shell.

```bash
API=http://localhost:8000
TOKEN=$(curl -s -X POST $API/api/auth/login -H "Content-Type: application/json" \
  -d '{"username":"sudo.admin","password":"<your-password>"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Catalog count + categories
curl -s $API/api/tools/marketplace -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('tools:',d['count'])"

# Tool runner form
curl -s $API/api/admin/ethical-hacking/tools/nmap/form \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; print([f['name'] for f in json.load(sys.stdin)['fields']])"

# Installation manifest (does NOT install anything)
curl -s $API/api/tools/nmap/install-plan \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Sudo can queue an installation request to a managed worker.
curl -s -X POST $API/api/tools/install-requests \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"tool_id":"nmap","worker_id":"worker-kali-01"}' | python3 -m json.tool

# Sudo tool run → governed job queued for the isolated worker
curl -s -X POST $API/api/admin/ethical-hacking/jobs/run \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"tool":"Nmap","target":"lab-web","scope":["lab-web"],"environment":"lab","purpose":"Authorized lab assessment","params":{"profile":"Quick port sweep"}}' \
  | python3 -m json.tool
```

### Managed worker rule

VEYRA SaaS does **not** execute `apt`, `pip`, PowerShell or arbitrary shell. A
customer/security-admin selects a worker; the worker validates the signed manifest,
package provenance, version pin, signature/hash and SBOM before installation.

High-impact tools remain privileged-admin gated. Customer users receive only the
tool levels assigned by the single Sudo administrator.

### Tool Academy

The **Tool Academy** page explains purpose, safe operating boundary, evidence and
defensive interpretation. It deliberately avoids turning the product into an
attack recipe.

### Catalog source

The expanded Kali portion follows the current Kali Linux 2026.3.2
`kali-linux-everything` inventory. The catalog is refreshed as Kali changes; it is
not a promise that future Kali packages will remain static.

See `docs/TOOL_ECOSYSTEM_V27.md`.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).

## v2.8 AI Ecosystem and Workers

### Inspect AI ecosystem

```bash
curl -H "Authorization: Bearer $AEGISX_SESSION_TOKEN" http://localhost:8000/api/ai-ecosystem/overview
curl -H "Authorization: Bearer $AEGISX_SESSION_TOKEN" http://localhost:8000/api/ai-ecosystem/tools
```

### Register a development worker

```bash
curl -X POST http://localhost:8000/api/workers/register \
  -H "Authorization: Bearer $AEGISX_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"worker_id":"kali-lab-01","name":"Kali Lab Worker","kind":"kali","platform":"kali-linux-amd64","capabilities":["security-tools","ai-security","dfir","network"]}'
```

### Worker inventory

```bash
curl -H "Authorization: Bearer $AEGISX_SESSION_TOKEN" http://localhost:8000/api/workers
curl -H "Authorization: Bearer $AEGISX_SESSION_TOKEN" http://localhost:8000/api/workers/kali-lab-01/tools
```

These are POC control-plane APIs. Production worker authentication must use short-lived workload identity and signed messages.


## VEYRA v3.0 — Adversary Intelligence & Wireless Defense Fabric

- First-class Wireless Security Center: AP/client inventory, trusted baseline, rogue candidates and evidence workflow.
- Attack Timeline: cross-source chronology across flows, sessions and audit events.
- Infrastructure Investigation: service → process → PID → user attribution plus high-risk flow review.
- Attribution & Evidence: hypothesis-only attribution, supporting/contradicting evidence, and evidence-bundle staging.
- Defensive boundary: no hack-back, credential capture, deauthentication, persistence, disruption or unrestricted shell execution through these surfaces.
- New API: `/api/v29/overview`, `/api/v29/wireless`, `/api/v29/timeline`, `/api/v29/infrastructure`, `/api/v29/attribution`, `/api/v29/evidence-bundle`.

## v3.0 Full Security Operations Fabric

From `backend/`:

```bash
PYTHONPATH=. pytest -q
```

New service smoke test:

```bash
PYTHONPATH=. pytest -q tests/test_v3_fabric.py
```

New API surfaces:

- `GET /api/v3/fabric/overview`
- `GET /api/v3/fabric/graph`
- `GET /api/v3/fabric/reconstruction?limit=100`
- `GET /api/v3/fabric/ai-investigation`
- `POST /api/v3/fabric/response-plan`
- `GET /api/v3/fabric/recovery`

The response-plan endpoint stages a plan only. Actual containment remains outside the API and must be approved and dispatched through the managed worker/security policy plane.


## v3.1 Sudo Arsenal / Terminal usage
See `docs/TERMINAL_RUNBOOK_V31.md` and `docs/TOOL_USAGE_CATALOG_V31.md`. Every tool has a documented UI workflow and a worker-local terminal starting point (`<tool> --help` / version). VEYRA does not accept arbitrary browser shell commands.


## v3.1.1 Tool Help Contract

For any tool, start with the tool's VEYRA Help panel. On an enrolled worker, the safe first command is the tool capability check shown in `docs/TOOL_USAGE_CATALOG_V31.md` (normally `<tool> --help` or `<tool> --version`). Do not substitute an arbitrary active command.

For AI/agent tools, use the dedicated managed AI worker or approved connector. Capture model/agent version, test corpus, policy decision, trace ID, artifact hash and timestamp.

See:
- `docs/TOOL_USAGE_CATALOG_V31.md` — every tool
- `docs/AI_CUTTING_EDGE_2026_TEAM_GUIDE.md` — AI security learning path
- `docs/AI_LATEST_2026.md` — current AI-security baseline

## v3.3 readiness validation
From the repository root:

```bash
python scripts/validate_tool_documentation.py
```

This is a documentation/CI check. It does not execute security tools.


## v3.6 Security Radar

Validate the tool catalog and documentation before promotion:

```bash
python scripts/validate_tool_documentation.py
```

Review `docs/SECURITY_RADAR_V36.md` before installing any newly scouted tool. Experimental tools must remain on isolated workers until promotion criteria are met.

## v3.7 Graph Intelligence validation

```bash
python -m compileall backend/app
pytest -q backend/tests/test_v37_graph_intelligence.py
python scripts/validate_tool_documentation.py
```

Graph Intelligence is read-only. High-impact response remains governed by RBAC/Sudo, scope, approval, worker execution and evidence controls.
