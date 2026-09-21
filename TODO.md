# VEYRA — Outstanding To-Do List

Check off as you go. Items are ordered by priority. Commands assume project root:
`/Users/kam/Downloads/VEYRA_POC_v2_5_1_WiFi_LAN_Visibility`

## 🔴 Security basics (do first)

- [ ] **Set the admin email + SMTP** so tool-approval requests arrive by email.
  Without this, requests only land in Tool Runner → Approval inbox + backend log.
  Edit project `.env`, then `docker compose up -d`:
  `VEYRA_ADMIN_EMAIL`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
  `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TLS`
- [ ] **Rotate the sudo bootstrap credentials.** First login forces a password
  change (My Password) — after that, remove/rotate `VEYRA_SUDO_USERNAME` /
  `VEYRA_SUDO_PASSWORD` from deployment config per
  `docs/IDENTITY_PERMISSIONS_V25.md`.
- [ ] **Rotate placeholder secrets** (still `change-me-*` defaults — fine for
  local laptop use, mandatory before any shared/production use):
  `VEYRA_ADMIN_TOKEN`, `VEYRA_PRIVILEGED_ADMIN_TOKEN`,
  `VEYRA_WORKER_TOKEN`, `VEYRA_WORKER_SIGNING_SECRET`,
  `VEYRA_AI_GATEWAY_TOKEN` (in `backend/.env`).
- [ ] **Set `COLLECTOR_TOKEN`** (backend env + compose) so ingest endpoints are
  token-gated instead of open.

## 🟡 Console baseline (10 minutes in the UI)

- [ ] **Trust your LAN devices:** Network → My LAN devices → mark your Mac,
  printer, router **TRUSTED**. Unknowns stay flagged until verified.
- [ ] **Set Expected SSID** for Router Mode A/B so Nearby Wi-Fi filters to
  your network.
- [ ] **Decide on test user `analyst1`** (created during verification):
  keep for testing the approval flow, or disable via User & Permissions.
- [ ] **Test Tool Runner as non-sudo:** log in as `analyst1`, open a
  read-only tool, send an approval request, approve it as sudo.
- [ ] **Review Approval inbox + Notifications** after the first real requests.

## 🔵 v2.7 tool ecosystem

- [ ] Provision at least one hardened managed Kali worker per customer/tenant.
- [ ] Implement worker-side signed install manifests with package signature/hash,
  version pinning, SBOM generation and rollback.
- [ ] Register worker heartbeat/capability inventory so Marketplace shows whether
  each tool is installed and healthy.
- [x] Per-tool educational help metadata for all 477 catalog entries; see
  `docs/TOOL_HELP_CATALOG_V27.md` and `/api/security-tool-academy`.
- [ ] Add per-tool version/update/uninstall UI with change approval.
- [ ] Add evidence parsers for common tool outputs (JSON/XML/SARIF/PCAP/EVTX).
- [ ] Refresh the Kali catalog automatically against an approved package source;
  review changes before publishing to customers.
- [ ] Add customer-tenant isolation for worker, tool, evidence and secrets.
- [ ] Add OpenTelemetry spans for install, run, evidence and approval lifecycle.
- [ ] Keep high-impact tools behind privileged-admin/Sudo controls.

## 🟢 Lab & intel (optional next steps)

- [ ] **Lab target overlay:** this folder ships base compose only
  (`docker-compose.lab.yml` referenced by `docs/LAB_GUIDE.md` is absent), so
  `python3 lab/red_blue_demo.py` has no `:4101` target. Recreate the overlay
  or run the demo against an approved local target.
- [ ] **Live threat intel:** set `NVD_API_KEY` and/or
  `THREATINTEL_AUTO_REFRESH=true`, or cron `POST /api/threat-intel/refresh`.
- [ ] **Re-sweep LAN periodically:** `python3 collectors/endpoint-agent.py
  --discover auto --yes --once` (or daemon mode) to catch new devices.

## ⚙️ Production hardening (before any non-local use)

Per `README.md` + `docs/PRODUCTION_GUIDE.md` — still open by design:
- [ ] HTTPS termination, Postgres backups, OIDC/RBAC + MFA (replace POC
  tokens), K8s manifests as needed.

## 🧹 Optional cleanup / follow-ups

- [ ] Remove obsolete experiment `installers/VEYRA WiFi Sensor.app`
  (superseded by `collectors/wifi-scan-jit.swift`; harmless if left).
- [ ] BSSID column shows `—` (macOS withholds it without a persisting
  Location grant; SSIDs unaffected). Revisit only if BSSID-level tracking
  is needed.
- [ ] Full backend suite has 7 pre-existing order-dependent failures
  (green file-by-file; see runbook §9). Fix only if CI-gating the suite.
- [ ] Monitor time-boxed grants: expired grants auto-read as `none`; review
  `Tool Runner → Job queue` and audit log (`GET /api/audit`) periodically.

## ✅ Already done (do not redo)

- Project running (`docker compose up --build -d`); frontend :3000,
  backend :8000, postgres healthy.
- Frontend duplicate-import crash fixed (`KeyRound`).
- Sudo account `Kam` seeded; compose forwards `VEYRA_SUDO_*`.
- Wi-Fi sensor permanent via LaunchAgent (`com.veyra.wifi-sensor`);
  SSID scan via `collectors/wifi-scan-jit.swift`.
- LAN discovery with mDNS/NetBIOS naming (7 devices, baseline started).
- Tool Runner: sudo one-click runs, per-tool forms, approval inbox,
  time-boxed grants (see `docs/TOOL_RUNNER_V26.md`, runbook §14).
- `TERMINAL_RUNBOOK.md` end-to-end command reference.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).

## v2.8 follow-up — production worker fabric

- [ ] Replace worker register/heartbeat shared admin authorization with workload identity + signed requests.
- [ ] Implement worker pull queue for signed installation manifests.
- [ ] Implement typed tool execution contracts and per-tool schemas.
- [ ] Implement streaming structured output and signed execution receipts.
- [ ] Add artifact cache with signature/SHA-256/SBOM verification.
- [ ] Add AIBOM generation and model provenance.
- [ ] Add AI agent circuit breaker / emergency shutdown.
- [ ] Add MCP server inventory and policy scanner.
- [ ] Add A2A identity and trust graph.
- [ ] Add AI model registry security and approval workflow.
- [ ] Add automated AI regression/security gates to CI/CD.
- [ ] Fix the remaining legacy test-isolation failures before release.


## VEYRA v3.0 — Adversary Intelligence & Wireless Defense Fabric

- First-class Wireless Security Center: AP/client inventory, trusted baseline, rogue candidates and evidence workflow.
- Attack Timeline: cross-source chronology across flows, sessions and audit events.
- Infrastructure Investigation: service → process → PID → user attribution plus high-risk flow review.
- Attribution & Evidence: hypothesis-only attribution, supporting/contradicting evidence, and evidence-bundle staging.
- Defensive boundary: no hack-back, credential capture, deauthentication, persistence, disruption or unrestricted shell execution through these surfaces.
- New API: `/api/v29/overview`, `/api/v29/wireless`, `/api/v29/timeline`, `/api/v29/infrastructure`, `/api/v29/attribution`, `/api/v29/evidence-bundle`.

## v4.0 follow-up before enterprise GA
- [ ] Connect TUF repository metadata verification in the isolated verification worker.
- [ ] Connect Cosign/Sigstore signature + attestation verification.
- [ ] Generate SBOMs with Syft for every immutable artifact.
- [ ] Scan artifacts/SBOMs with Grype and record OpenVEX where appropriate.
- [ ] Enforce SLSA/in-toto provenance acceptance policy.
- [ ] Move Artifact Vault to immutable object storage with retention/WORM controls.
- [ ] Replace admin-token worker auth with workload identity + signed requests.
- [ ] Add worker pull queue for signed v4 manifests.
- [ ] Add canary cohort and automatic rollback controller.
- [ ] Add customer/tenant-specific update policies.
- [ ] Add full dependency lock/hashes and image digests in production deployment.
- [ ] Run full 79-test legacy suite and fix the five known failures before CI gate.
- [ ] Verify frontend `npm ci && npm run build` in a network-enabled CI runner.

## v4.2 Trusted Supply Chain — Production Completion
- [ ] Connect managed workers to a real signed pull queue using workload identity.
- [ ] Deploy immutable artifact storage/WORM retention and disaster recovery.
- [ ] Configure TUF repository, root rotation and freshness policy.
- [ ] Configure Cosign/Sigstore identity and attestation policy.
- [ ] Generate Syft SBOMs on workers and retain immutable references.
- [ ] Enforce Grype vulnerability policy with KEV/EPSS-aware exceptions.
- [ ] Verify SLSA v1.2/in-toto provenance before trusted promotion.
- [ ] Implement real canary rollout controller and health telemetry ingestion.
- [ ] Implement worker-enforced automatic rollback.
- [ ] Bind update policies to tenant/workspace identity before multi-tenant production.
- [ ] Add model/AIBOM provenance and MCP/A2A publisher trust verification.
- [ ] Bind agent circuit breaker to network/identity enforcement plane.
- [ ] Establish quarterly recovery/rollback exercises.
