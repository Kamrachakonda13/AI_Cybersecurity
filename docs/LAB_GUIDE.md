# VEYRA Secure Local Lab — Red + Blue on your laptop (no cloud needed)

Runs entirely in Docker on macOS. You own every target. **Never point these
workflows at external sites, client infra, or the internet.**

## 1. Start

```bash
# main platform + isolated lab target
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
open http://localhost:3000   # console
open http://localhost:8000/docs  # API
curl -s http://localhost:4101/   # lab vulnerable web (laptop view)
```

Stop / wipe lab data:

```bash
docker compose -f docker-compose.yml -f docker-compose.lab.yml down
docker compose down -v   # also wipes postgres volume (fresh seed)
```

## 2. Guardrails (read before handing to either team)

| Rule | How enforced |
|---|---|
| Lab-only targets | `backend/app/services/assess.py: LAB_HOSTS = vulnerable-web, localhost, *.lab` — anything else is public-internet path (passive checks only, rate-limited) |
| No exploitation | No Metasploit/Burp-active/Nuclei-intrusive execution anywhere in the platform; catalog marks them `governed / disabled` |
| Approval boundary | Private/lab URLs return `pending_approval` unless `approval_confirmed:true` + audit-logged (`web_assessment_pending_approval`) |
| Least privilege containers | `docker-compose.lab.yml`: `cap_drop: ALL`, `no-new-privileges`, `read_only`, `USER nobody`, cpu/mem limits, bridge network only |
| No host access | No `network_mode: host`, no `privileged:true`, no bind-mounts of `/`, DB creds stay in compose env |

## 3. Red-team exercises (attackers — lab target ONLY)

1. **Posture sweep (governed):** UI → Offensive Security → `http://vulnerable-web:4101` → Assess → expect `pending_approval` → resubmit approved → findings: missing HSTS/CSP, banner `VEYRA-Lab/1.0`, `robots.txt`, plaintext HTTP.
2. **Manual review (safe strings only):** `curl` `/admin`, `/robots.txt`, `/api/users?name=lab-test`, `POST /ai/chat {"prompt":"hello"}`. Record notes — do NOT brute-force, fuzz, or DoS.
3. **Graph question:** `GET /api/graph/answer?kind=port_owner` — which process owns the exposed port? Correlate to high-privilege identity.
4. Stretch (outside VEYRA, still lab-only): `nmap -sV vulnerable-web` from a throwaway container on the same compose network. Import conclusions manually as audit notes.

## 4. Blue-team exercises (defenders — same activity)

1. **Run the demo:** `python3 lab/red_blue_demo.py` — ingests a simulated password-spray session + lateral flow, then prints attack paths.
2. **Detect:** UI → Security Graph → confirm `internet → web-prod-01 → vector-db` path; Identity → `red-lab anomaly 0.91 PRIVILEGED`; audit log shows `web_assessment_*` + `ingest_*`.
3. **Respond (advisory):** `POST /api/ai/investigate {"question":"Investigate red-lab session"}` → evidence bundle, human approval before any action.
4. **Harden lab:** add a header in `lab/vulnerable-web/app.py`, rebuild, re-assess, watch header_score rise and findings close.

## 5. Team split suggestion

- **Red (2-3):** own `lab/vulnerable-web`, write scope doc (hosts + techniques ALLOWED), file findings via assessment API.
- **Blue (2-3):** own VEYRA console, write detections (graph answer queries + anomaly thresholds), triage red findings, keep audit trail.
- Swap roles weekly. Keep a shared rule: if it's not in the scope doc + approval log, it doesn't happen.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
