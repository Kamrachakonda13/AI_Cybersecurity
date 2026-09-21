# VEYRA v2.7 — Complete Codebase & Help Guide

> **Purpose:** This is the developer/operator map for the entire repository. It explains what every source file is responsible for, the important classes/functions/components inside it, and where to look when changing a feature. It complements the operational README and runbook.

## How to use this guide

1. Start with the architecture map below.
2. Find the feature you want to change.
3. Open the listed backend route, service, model, and frontend component.
4. Follow the data flow from UI → API → service → database/worker → evidence.
5. Keep authorization in the backend even when the UI hides an option.
6. For security-tool changes, update the registry, access tier, form, worker capability, help text, evidence parser, and tests together.

## Product layers

```text
React Console
   ↓
FastAPI API / authorization
   ↓
Security services + policy engines
   ↓
PostgreSQL models / evidence
   ↓
Governed worker contracts
   ↓
Managed security workers (Kali / cloud / DFIR / AI)
   ↓
Normalized evidence → Security Fabric → SOC / Graph / Risk
```

## Repository tree

```text
backend/        FastAPI application, services, models and tests
collectors/     Endpoint + Wi-Fi telemetry agents
frontend/       React/Vite operator console
docs/           Product, architecture, operations and education guides
examples/       Integration examples
installers/     Local sensor packaging
lab/            Isolated training/demo environment
docker-compose.yml   Local orchestration
```

## Complete file-by-file reference

### `README.md`

Primary product overview and quick-start. Keep release number, feature list, security boundaries, API examples, and documentation links synchronized with the implementation.

### `TERMINAL_RUNBOOK.md`

Operator command reference. It explains how to start, inspect, test, troubleshoot, and operate the platform from a terminal without bypassing the governed control plane.

### `TODO.md`

Current implementation backlog. Items marked security/production are prerequisites before shared or production deployment.

### `backend/.env.example`

Safe configuration template. Copy to `backend/.env`; never commit real credentials.

### `backend/.pytest_cache/.gitignore`

Project support/resource file.

### `backend/.pytest_cache/CACHEDIR.TAG`

Project support/resource file.

### `backend/.pytest_cache/README.md`

Markdown documentation.

### `backend/.pytest_cache/v/cache/lastfailed`

Project support/resource file.

### `backend/.pytest_cache/v/cache/nodeids`

Project support/resource file.

### `backend/Dockerfile`

Container build definition.

### `backend/app/__init__.py`

Python implementation file in the VEYRA backend/collector/lab layers.

### `backend/app/api/routes.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `require_admin` — line 39 — Accept legacy admin token or an authenticated console role with admin capability.
- `require_privileged_admin` — line 57 — Second gate for high-impact security tooling; use PAM/MFA in production.
- `_bearer_user` — line 66 — Console session user or None (never raises).
- `require_tool_access` — line 81 — API operation `require_tool_access`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `admin_ethical_tools` — line 107 — API operation `admin_ethical_tools`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `EthicalJobRequest` — line 112 — API operation `EthicalJobRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `stage_ethical_job` — line 123 — API operation `stage_ethical_job`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `admin_ethical_jobs` — line 162 — API operation `admin_ethical_jobs`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `approve_ethical_job` — line 173 — API operation `approve_ethical_job`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `dispatch_ethical_job` — line 186 — API operation `dispatch_ethical_job`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `EvidenceRequest` — line 198 — API operation `EvidenceRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_ethical_evidence` — line 202 — API operation `ingest_ethical_evidence`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `list_ethical_evidence` — line 218 — API operation `list_ethical_evidence`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ethical_tool_form` — line 227 — API operation `ethical_tool_form`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `run_ethical_job_now` — line 236 — One-click governed run.
- `PentestPlanRequest` — line 288 — API operation `PentestPlanRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `pentest_agent_catalog` — line 297 — API operation `pentest_agent_catalog`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `create_pentest_agent_plan` — line 302 — API operation `create_pentest_agent_plan`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `list_pentest_agent_plans` — line 313 — API operation `list_pentest_agent_plans`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `help_registry` — line 318 — Machine-readable module help and safe operating guidance.
- `clean` — line 322 — API operation `clean`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `require_collector` — line 325 — Optional shared-secret auth for machine ingest endpoints.
- `require_ai_gateway` — line 336 — API operation `require_ai_gateway`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `AIGatewayRequest` — line 343 — API operation `AIGatewayRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `AgentPolicyRequest` — line 352 — API operation `AgentPolicyRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `get_agent_policy` — line 361 — API operation `get_agent_policy`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `put_agent_policy` — line 368 — API operation `put_agent_policy`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_gateway_evaluate` — line 382 — API operation `ai_gateway_evaluate`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_gateway_trace` — line 398 — API operation `ai_gateway_trace`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_gateway_events` — line 403 — API operation `ai_gateway_events`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `fabric_overview` — line 410 — API operation `fabric_overview`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `FabricEventRequest` — line 414 — API operation `FabricEventRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `fabric_event` — line 425 — API operation `fabric_event`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `fabric_events` — line 433 — API operation `fabric_events`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `fabric_ai_attack_paths` — line 438 — API operation `fabric_ai_attack_paths`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `overview` — line 443 — API operation `overview`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `assets` — line 456 — API operation `assets`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ports` — line 460 — API operation `ports`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `flows` — line 465 — API operation `flows`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `findings` — line 470 — API operation `findings`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `incidents` — line 475 — API operation `incidents`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `audit` — line 479 — API operation `audit`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `identities` — line 483 — API operation `identities`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `sessions` — line 487 — API operation `sessions`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `threat_intel` — line 491 — API operation `threat_intel`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `cloud_resources` — line 495 — API operation `cloud_resources`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_assets` — line 499 — API operation `ai_assets`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `RiskRequest` — line 502 — API operation `RiskRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `risk` — line 513 — API operation `risk`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `InvestigationRequest` — line 517 — API operation `InvestigationRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `investigate` — line 522 — API operation `investigate`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `AssessmentRequest` — line 531 — API operation `AssessmentRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `create_assessment` — line 538 — API operation `create_assessment`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `graph` — line 546 — API operation `graph`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `graph_attack_path` — line 552 — API operation `graph_attack_path`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `graph_answer` — line 556 — API operation `graph_answer`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `FlowIn` — line 562 — API operation `FlowIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `SessionIn` — line 567 — API operation `SessionIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ServiceIn` — line 572 — API operation `ServiceIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_flows` — line 578 — API operation `ingest_flows`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_sessions` — line 587 — API operation `ingest_sessions`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_services` — line 596 — API operation `ingest_services`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `tools_catalog` — line 609 — API operation `tools_catalog`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `WebAssessmentRequest` — line 613 — API operation `WebAssessmentRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `web_assessment` — line 618 — API operation `web_assessment`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `forensics_tools` — line 651 — API operation `forensics_tools`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `forensics_analyze` — line 660 — API operation `forensics_analyze`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `DeviceIn` — line 677 — API operation `DeviceIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `DnsIn` — line 680 — API operation `DnsIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `LoginIn` — line 683 — API operation `LoginIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_devices` — line 688 — API operation `ingest_devices`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_dns` — line 710 — API operation `ingest_dns`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_logins` — line 722 — API operation `ingest_logins`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `devices` — line 733 — API operation `devices`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `dns_top` — line 738 — API operation `dns_top`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `login_attempts` — line 742 — API operation `login_attempts`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `logins_summary` — line 747 — API operation `logins_summary`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `remediation` — line 753 — API operation `remediation`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `team_red` — line 763 — API operation `team_red`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `team_blue` — line 768 — API operation `team_blue`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `TriageRequest` — line 772 — API operation `TriageRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `session_triage` — line 777 — Correlate a suspicious IP/username against YOUR OWN telemetry.
- `RefreshRequest` — line 820 — API operation `RefreshRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_allowlisted_get` — line 824 — Outbound GET restricted to threat-intel allowlist (+ optional NVD_API_KEY).
- `threat_refresh` — line 842 — API operation `threat_refresh`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `threat_cves` — line 856 — API operation `threat_cves`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `mitre_techniques` — line 867 — API operation `mitre_techniques`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `mitre_coverage` — line 872 — API operation `mitre_coverage`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `UsbIn` — line 878 — API operation `UsbIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `DlpIn` — line 881 — API operation `DlpIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_usb` — line 888 — API operation `ingest_usb`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `usb_events` — line 914 — API operation `usb_events`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `usb_summary` — line 919 — API operation `usb_summary`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_dlp` — line 929 — API operation `ingest_dlp`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `dlp_events` — line 954 — API operation `dlp_events`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `dlp_summary` — line 959 — API operation `dlp_summary`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `HbService` — line 972 — API operation `HbService`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `HbUsb` — line 976 — API operation `HbUsb`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `Heartbeat` — line 979 — API operation `Heartbeat`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `heartbeat` — line 984 — Agent sync: upsert device + asset, reconcile services, record USB. Returns counts.
- `ProwlerItem` — line 1023 — API operation `ProwlerItem`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `cloud_adapters` — line 1028 — API operation `cloud_adapters`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `cloud_prowler` — line 1033 — API operation `cloud_prowler`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `CloudScanRequest` — line 1041 — API operation `CloudScanRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `cloud_scan` — line 1045 — Live read-only AWS scan. 501 with setup guidance when boto3/creds are absent.
- `ai_probes` — line 1064 — Probe battery metadata (names/categories only — prompts execute server-side).
- `AiEvalRequest` — line 1069 — API operation `AiEvalRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_evaluate` — line 1074 — Run the injection/jailbreak battery against a LAB/PRIVATE AI gateway (approval-gated).
- `post_fn` — line 1094 — API operation `post_fn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `RetrievalIn` — line 1118 — API operation `RetrievalIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `retrieval_audit` — line 1122 — API operation `retrieval_audit`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `retrieval_list` — line 1130 — API operation `retrieval_list`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `soar_playbooks` — line 1138 — API operation `soar_playbooks`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `SoarRunRequest` — line 1142 — API operation `SoarRunRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `soar_runs` — line 1148 — API operation `soar_runs`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `soar_approve` — line 1156 — API operation `soar_approve`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `soar_list` — line 1164 — API operation `soar_list`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `DiscoveryIn` — line 1172 — API operation `DiscoveryIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_discovery` — line 1176 — API operation `ingest_discovery`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `discovery_hosts` — line 1187 — API operation `discovery_hosts`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `WifiNetworkIn` — line 1192 — API operation `WifiNetworkIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ingest_wifi_networks` — line 1202 — API operation `ingest_wifi_networks`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `WifiTrustUpdate` — line 1223 — API operation `WifiTrustUpdate`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `update_discovered_host_trust` — line 1227 — API operation `update_discovered_host_trust`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `discovery_wifi_networks` — line 1237 — API operation `discovery_wifi_networks`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `discovery_summary` — line 1242 — API operation `discovery_summary`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_security_catalog` — line 1258 — API operation `ai_security_catalog`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_security_controls` — line 1263 — API operation `ai_security_controls`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `AgentPostureRequest` — line 1267 — API operation `AgentPostureRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ai_agent_posture` — line 1282 — API operation `ai_agent_posture`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `WorkerHeartbeatRequest` — line 1287 — API operation `WorkerHeartbeatRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `WorkerEvidenceRequest` — line 1292 — API operation `WorkerEvidenceRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `require_worker` — line 1298 — API operation `require_worker`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `worker_next_job` — line 1306 — API operation `worker_next_job`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `worker_evidence` — line 1324 — API operation `worker_evidence`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `InvestigationStartRequest` — line 1340 — API operation `InvestigationStartRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ContainmentRequest` — line 1343 — API operation `ContainmentRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `ApprovalDecisionRequest` — line 1348 — API operation `ApprovalDecisionRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `autonomous_soc_overview` — line 1353 — API operation `autonomous_soc_overview`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `autonomous_soc_cases` — line 1364 — API operation `autonomous_soc_cases`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `autonomous_soc_investigate` — line 1369 — API operation `autonomous_soc_investigate`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `autonomous_soc_containment` — line 1375 — API operation `autonomous_soc_containment`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `autonomous_soc_approval` — line 1381 — API operation `autonomous_soc_approval`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `MeshAlertRequest` — line 1387 — API operation `MeshAlertRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `MeshResponseRequest` — line 1399 — API operation `MeshResponseRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `MeshVerifyRequest` — line 1404 — API operation `MeshVerifyRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `detection_mesh_overview` — line 1409 — API operation `detection_mesh_overview`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `detection_mesh_rules` — line 1424 — API operation `detection_mesh_rules`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `detection_mesh_alert` — line 1432 — API operation `detection_mesh_alert`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `detection_mesh_actions` — line 1438 — API operation `detection_mesh_actions`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `detection_mesh_response` — line 1443 — API operation `detection_mesh_response`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `detection_mesh_verify` — line 1449 — API operation `detection_mesh_verify`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `intel_fusion_overview` — line 1456 — API operation `intel_fusion_overview`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `intel_fusion_enrich` — line 1466 — API operation `intel_fusion_enrich`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `intel_fusion_case` — line 1472 — API operation `intel_fusion_case`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `intel_fusion_hypotheses` — line 1478 — API operation `intel_fusion_hypotheses`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `intel_fusion_enrichments` — line 1486 — API operation `intel_fusion_enrichments`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `LoginRequest` — line 1492 — API operation `LoginRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `PasswordChangeRequest` — line 1496 — API operation `PasswordChangeRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `UserCreateRequest` — line 1500 — API operation `UserCreateRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `UserUpdateRequest` — line 1509 — API operation `UserUpdateRequest`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_auth_user` — line 1520 — API operation `_auth_user`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_sudo` — line 1524 — API operation `_sudo`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_validate_permissions` — line 1528 — API operation `_validate_permissions`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_grant_expiry_from_value` — line 1540 — Normalise a permission value to (level, expires_at).
- `auth_login` — line 1550 — API operation `auth_login`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `auth_logout` — line 1560 — API operation `auth_logout`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `auth_me` — line 1571 — API operation `auth_me`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `auth_password` — line 1576 — API operation `auth_password`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `users_list` — line 1586 — API operation `users_list`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `users_tool_catalog` — line 1601 — API operation `users_tool_catalog`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `users_create` — line 1611 — API operation `users_create`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `users_update` — line 1628 — API operation `users_update`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `my_tool_permissions` — line 1652 — API operation `my_tool_permissions`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `AccessRequestIn` — line 1676 — API operation `AccessRequestIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `AccessDecideIn` — line 1682 — API operation `AccessDecideIn`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_tool_lookup` — line 1686 — API operation `_tool_lookup`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `_sudo_inbox_targets` — line 1690 — API operation `_sudo_inbox_targets`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `tool_access_request` — line 1699 — Any signed-in user may ask the sudo admin for tool rights (default read-only otherwise).
- `tool_access_requests` — line 1740 — Sudo sees every request; users see their own. Use status=all|pending|approved|denied|expired.
- `tool_access_decide` — line 1755 — Sudo decision. Approvals mint a time-boxed grant (2h/5h/24h/custom);
- `admin_notifications` — line 1805 — Sudo inbox: every access request email/log mirror + decisions. Users see
- `grant_duration_options` — line 1817 — API operation `grant_duration_options`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `tool_marketplace` — line 1823 — Managed security-tool catalog. Installation is planned/approved, never arbitrary shell.
- `tool_install_plan` — line 1833 — API operation `tool_install_plan`: handles the corresponding HTTP request, authorization/policy checks, persistence, and response formatting for the VEYRA console or collectors.
- `tool_install_request` — line 1845 — Create an auditable installation request; a managed worker performs the actual package operation.
- `security_tool_academy` — line 1873 — Safe, command-free learning guide for every integrated tool.

### `backend/app/db.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `Base` — line 24 — Implementation element `Base` used by VEYRA.
- `get_db` — line 27 — Implementation element `get_db` used by VEYRA.

### `backend/app/main.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `lifespan` — line 28 — Startup: create tables, seed demo data, optionally start KEV auto-refresh loop.
- `_ensure_columns` — line 32 — Implementation element `_ensure_columns` used by VEYRA.
- `health` — line 61 — Implementation element `health` used by VEYRA.

### `backend/app/models/__init__.py`

Python implementation file in the VEYRA backend/collector/lab layers.

### `backend/app/models/entities.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `now` — line 19 — Database model `now`: represents a persistent VEYRA security, identity, telemetry, governance, or evidence record.
- `Asset` — line 21 — Monitored host/workload. `criticality` 1–5 feeds risk directly; `external_exposure` seeds graph attack paths.
- `Service` — line 34 — Listening port on an asset with process/user attribution. `expected=False` means baseline drift (backdoor suspect).
- `Identity` — line 47 — Human/service account. `privilege` 4–5 = can reach sensitive workloads; `mfa_enabled=False` doubles takeover risk.
- `SessionEvent` — line 58 — Authenticated session: who (`username`) reached which asset, how, and how anomalous (`anomaly_score` ≥ 0.7 = critical).
- `NetworkFlow` — line 72 — One observed connection. `risk_score` ≥ 70 = possible exfil/lateral movement; feeds graph `flow` edges.
- `ThreatIntel` — line 87 — Intel record (CISA KEV CVE or MITRE ATT&CK technique). `exploited=True` raises the `threat` term in risk scoring.
- `CloudResource` — line 100 — Cloud inventory row (manual/API-ingested; live CSPM adapters are future work). `public_exposure` = directly reachable.
- `AIAsset` — line 112 — AI app/agent/vector-DB. `exposure=internet` + tool permissions = prompt-injection/data-egress surface; graph links agents to vector stores via `retrieves` edges.
- `Finding` — line 124 — Scored weakness on an asset. `severity`/`risk_score` come from `services/risk`; `kev`/`exposure` explain WHY it is critical.
- `Incident` — line 140 — SOC case needing a human decision. Status stays `open` until triaged; every response needs approval (Governance view).
- `AuditEvent` — line 151 — Immutable audit trail: every ingestion, assessment, triage and analysis writes one row. Never delete in production.
- `Device` — line 161 — Endpoint inventory heartbeat — YOUR OWN managed/lab devices only.
- `DnsQuery` — line 177 — DNS-metadata only (domain queried, NOT page content) — own network, consented.
- `LoginAttempt` — line 187 — Auth outcomes on YOUR OWN systems — detects password-spray / brute force.
- `CveRecord` — line 198 — Normalized CVE from live CISA KEV / NVD feeds (`services/threatintel.py`).
- `UsbEvent` — line 215 — USB device connect/block on a managed host (from endpoint agent heartbeat or ingest).
- `DlpEvent` — line 228 — Data-loss-prevention signal: sensitive file observed leaving its boundary.
- `RetrievalEvent` — line 243 — AI retrieval audit: which agent read which vector store, for which tenant, and whether policy allowed it.
- `SoarRun` — line 257 — SOAR playbook execution with approval boundary.
- `SecurityToolJob` — line 273 — Governed admin security-tool job contract. No browser command is stored/executed.
- `SecurityEvidence` — line 291 — Normalized evidence returned by an isolated worker; preserves provenance/hash.
- `DiscoveredHost` — line 307 — Observed LAN/Wi-Fi neighbour (NOT an enrolled agent).
- `AgentRuntimeEvent` — line 327 — Runtime telemetry/event envelope for internal agents, GenAI calls, MCP and A2A.
- `AgentPolicy` — line 342 — Deterministic runtime policy for an internal agent; LLMs never author policy.
- `UnifiedSecurityEvent` — line 354 — Cross-plane normalized event used by the VEYRA Security Fabric.
- `InvestigationCase` — line 371 — AI-assisted investigation case. AI proposes reasoning; policy/approval remain authoritative.
- `InvestigationEvidence` — line 389 — Evidence reference attached to a case; content stays normalized/provenance-aware.
- `InvestigationApproval` — line 402 — Human approval checkpoint before a consequential SOAR action.
- `InvestigationStep` — line 415 — Deterministic state transition log for the autonomous SOC pipeline.
- `DetectionRule` — line 425 — Deterministic detection rule. LLMs may explain matches but never author enforcement.
- `ResponseAction` — line 438 — Governed response action request and verification state; no direct side effects in POC.
- `AttributionHypothesis` — line 454 — Evidence-backed attribution hypothesis; never an asserted actor identity.
- `IntelEnrichment` — line 467 — Immutable-ish summary of local TI/ATT&CK/ATLAS enrichment for a case.
- `PentestAgentPlan` — line 479 — AI-generated, human-governed pentest plan. Stores plan/evidence metadata, not shell commands.
- `UserAccount` — line 495 — Console login account. Exactly one account may have role='sudo'.
- `UserToolPermission` — line 510 — Per-user tool entitlement: none, view, plan, or execute-request.
- `UserSession` — line 526 — Database model `UserSession`: represents a persistent VEYRA security, identity, telemetry, governance, or evidence record.
- `ToolAccessRequest` — line 535 — Non-sudo request for tool rights. Sudo approves with a time-boxed grant
- `AdminNotification` — line 554 — In-app copy of every outbound admin email (approval requests, decisions).
- `WifiNetwork` — line 568 — Observed nearby Wi-Fi network metadata from an enrolled local sensor.

### `backend/app/services/admin_tools.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `registry` — line 115 — Service function/class `registry`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/ai_gateway.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `utc` — line 20 — Service function/class `utc`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `content_risk` — line 22 — Service function/class `content_risk`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `decide` — line 28 — Service function/class `decide`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `trace_id` — line 49 — Service function/class `trace_id`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `event_hash` — line 51 — Service function/class `event_hash`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/ai_red.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `refused` — line 39 — True when a model reply looks like a refusal (case-insensitive phrase match).
- `evaluate` — line 45 — Run the probe battery via `post_fn(url, prompt)->reply`. Returns scored report.

### `backend/app/services/ai_security.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `catalog` — line 31 — Service function/class `catalog`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `controls` — line 34 — Service function/class `controls`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `assess_agent` — line 37 — Deterministic posture assessment; no attack payloads are generated.
- `check` — line 40 — Service function/class `check`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/assess.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `is_lab_host` — line 125 — True for lab-only hostnames (`LAB_HOSTS`, `*.lab`). Lab hosts are treated as private → approval gate applies.
- `validate_target` — line 131 — Validate an assessment target. Returns {host, private, scheme, lab} or raises ValueError.
- `check_cooldown` — line 162 — In-memory per-host rate limit (`COOLDOWN_SECONDS`). Raises ValueError when too soon; called by the web-assessment route before fetching.
- `score_headers` — line 176 — Score 6 security headers → {score 0–100, present[], missing[]}. Pure function; each missing header becomes a finding in `assess_web_posture`.
- `assess_web_posture` — line 184 — Passive fetch (single GET, 8s timeout, no payloads) + header/TLS/banner/robots heuristics.

### `backend/app/services/auth.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `hash_password` — line 15 — Service function/class `hash_password`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `verify_password` — line 22 — Service function/class `verify_password`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `issue_session` — line 33 — Service function/class `issue_session`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `current_user` — line 42 — Service function/class `current_user`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `require_sudo` — line 62 — Service function/class `require_sudo`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `require_role` — line 67 — Service function/class `require_role`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_expiry_active` — line 72 — Service function/class `_expiry_active`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `get_tool_level` — line 80 — Service function/class `get_tool_level`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `effective_tool_level` — line 88 — Sudo holds every tool at execute_request with no expiry; everyone else
- `grant_expiry` — line 95 — Service function/class `grant_expiry`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/autonomous_soc.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_now` — line 19 — Service function/class `_now`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_id` — line 20 — Service function/class `_id`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_sha` — line 21 — Service function/class `_sha`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_step` — line 22 — Service function/class `_step`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_severity` — line 26 — Service function/class `_severity`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `investigate_event` — line 32 — Service function/class `investigate_event`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `request_containment` — line 61 — Service function/class `request_containment`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `decide_approval` — line 69 — Service function/class `decide_approval`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `serialize_case` — line 84 — Service function/class `serialize_case`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `list_cases` — line 93 — Service function/class `list_cases`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/cloud_adapters.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_first_asset_id` — line 28 — Service function/class `_first_asset_id`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `import_prowler` — line 34 — Upsert CloudResources + FAIL Findings from Prowler-style items. Returns {resources, findings}.
- `aws_live_scan` — line 66 — Map AWS clients (real boto3 or test fakes) → CloudResource rows. Returns {resources, findings}.
- `upsert` — line 71 — Service function/class `upsert`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/discovery.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `normalize_mac` — line 64 — Upper-case colon form (`aa-bb-cc…`/`aabbcc…` → `AA:BB:CC…`). Returns '' when unusable.
- `vendor_for_mac` — line 72 — OUI lookup on the first 3 bytes. Returns vendor, 'Randomized (privacy MAC)',
- `upsert_discovery` — line 90 — Upsert neighbours by MAC (preferred) else IP. Returns {hosts, new}.

### `backend/app/services/execution_plane.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_utc` — line 17 — Service function/class `_utc`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `make_job_contract` — line 21 — Service function/class `make_job_contract`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `verify_contract_signature` — line 60 — Service function/class `verify_contract_signature`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `normalize_evidence` — line 68 — Service function/class `normalize_evidence`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/extended_catalog.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `build_tool_help` — line 473 — Create safe, per-tool education metadata for the UI.
- `extended_registry` — line 529 — Return base + extended catalog with normalized governance metadata.
- `install_manifest` — line 562 — Produce a managed-worker installation plan; does not install anything.

### `backend/app/services/fabric.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `utc` — line 12 — Service function/class `utc`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `stable_hash` — line 14 — Service function/class `stable_hash`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `normalize_event` — line 17 — Service function/class `normalize_event`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `security_fabric_overview` — line 24 — Service function/class `security_fabric_overview`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `ai_attack_paths` — line 44 — Correlate identity -> agent -> vector/data -> cloud/endpoint as a deterministic graph.
- `add` — line 48 — Service function/class `add`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `edge` — line 49 — Service function/class `edge`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_bfs_paths` — line 70 — Service function/class `_bfs_paths`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/forensics.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_strings` — line 70 — Extract printable ASCII runs (static, no execution). Capped at `cap` strings so huge binaries stay cheap.
- `detect_type` — line 87 — Magic-number file typing (ELF/PE/PDF/ZIP/PNG/JPEG/shebang/text). Header bytes only — never executes.
- `analyze_bytes` — line 111 — Pure static analysis. Never executes input.
- `_parse_eml` — line 247 — Parse .eml headers/body/attachments (stdlib `email`). Returns kind/from/subject/urls/attachments/has_spf_dkim.
- `_parse_ooxml` — line 273 — List Office OOXML zip members; flag `vbaProject.bin` (macro) + external rels. Returns kind/members/has_macro/external_links.
- `_parse_pe` — line 286 — Read PE section count via `e_lfanew` + suspicious-import strings. struct only — no disassembly (that is Ghidra's job).
- `_parse_elf` — line 304 — Read ELF class/machine (`ELF_MACHINES`) for triage context. Header bytes only.
- `_parse_pcap` — line 315 — Minimal pcap reader: Ethernet → IPv4 → TCP/UDP; DNS QNAMEs on udp/53.
- `_dns_qname` — line 361 — Decode one DNS QNAME from a UDP payload. Returns dotted name or '' on any parse failure.

### `backend/app/services/graph.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_asset_node` — line 16 — Canonical graph key for an asset row (`asset:<id>`). Used by every edge builder below.
- `build_graph` — line 21 — Compile DB telemetry into `{nodes, edges}`.
- `add_node` — line 34 — Service function/class `add_node`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `add_edge` — line 37 — Service function/class `add_edge`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_adjacency` — line 126 — Index edges by source node for BFS. Depends on: edge dicts from `build_graph`.
- `_is_sensitive` — line 134 — True when a node is a data-crown-jewel: explicit `sensitive` flag, any cloud/AI node, or C5 asset.
- `attack_paths` — line 146 — BFS from 'internet' to sensitive nodes. Returns list of {target, path}.
- `answer_question` — line 204 — Pre-canned correlation answers for the 6 flagship questions.

### `backend/app/services/help.py`

Python implementation file in the VEYRA backend/collector/lab layers.

### `backend/app/services/intel_fusion.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_now` — line 35 — Service function/class `_now`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_sha` — line 36 — Service function/class `_sha`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_event_text` — line 38 — Service function/class `_event_text`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_intel_matches` — line 42 — Service function/class `_intel_matches`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_hypotheses` — line 53 — Service function/class `_hypotheses`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `fuse_case` — line 74 — Service function/class `fuse_case`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `list_fusion_cases` — line 106 — Service function/class `list_fusion_cases`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/mitre.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `map_finding` — line 69 — Map one finding {title, severity, kev, exposure, cvss} → technique IDs (ordered, deduped).
- `coverage` — line 103 — Map every Finding row → techniques. Returns {techniques:[{…count}], unmapped, findings}.

### `backend/app/services/notify.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `admin_email` — line 17 — Service function/class `admin_email`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_smtp_config` — line 21 — Service function/class `_smtp_config`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `send_access_request_email` — line 32 — Returns (channel, status): channel is 'email' or 'log'.

### `backend/app/services/pentest_agents.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_sha` — line 30 — Service function/class `_sha`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `create_plan` — line 34 — Service function/class `create_plan`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/response_mesh.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_now` — line 19 — Service function/class `_now`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_id` — line 20 — Service function/class `_id`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_sha` — line 21 — Service function/class `_sha`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `ensure_rules` — line 23 — Service function/class `ensure_rules`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `connector_health` — line 29 — Service function/class `connector_health`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `evaluate_event` — line 39 — Service function/class `evaluate_event`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `ingest_alert` — line 50 — Service function/class `ingest_alert`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `request_response` — line 64 — Service function/class `request_response`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `verify_response` — line 74 — Service function/class `verify_response`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `serialize_action` — line 84 — Service function/class `serialize_action`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `list_actions` — line 87 — Service function/class `list_actions`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/risk.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `calculate_risk` — line 14 — Service function/class `calculate_risk`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `severity` — line 18 — Map a 0–100 risk score to a severity band (see module docstring).

### `backend/app/services/seed.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `seed` — line 16 — Service function/class `seed`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `seed_identity` — line 74 — Service function/class `seed_identity`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/soar.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_audit` — line 34 — Service function/class `_audit`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `_revoke_sessions_q` — line 39 — Service function/class `_revoke_sessions_q`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `run_playbook` — line 49 — Create (unapproved) or execute (approved) a playbook run. Returns run summary dict.
- `approve_run` — line 68 — Approve + execute a pending run. Errors on missing/already-decided runs.
- `_execute` — line 81 — Service function/class `_execute`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/teams.py`

Python implementation file in the VEYRA backend/collector/lab layers.

### `backend/app/services/threatintel.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `parse_kev_csv` — line 32 — Parse CISA KEV CSV text → [{cve_id, vendor, product, name, description, due_date}].
- `_nvd_score` — line 47 — Best CVSS from NVD metrics (prefers 3.1 → 3.0 → 2.0). Returns (score, severity).
- `parse_nvd` — line 60 — Parse NVD 2.0 response → [{cve_id, description, cvss, severity, published}].
- `upsert_cve` — line 76 — Insert or update one `CveRecord` + mirror `ThreatIntel` row. Returns True if created.
- `refresh_kev` — line 107 — Fetch KEV CSV via injected `fetch(url)->text`, upsert all rows. Returns {cves, new}.
- `refresh_nvd` — line 117 — Fetch NVD details for ≤20 CVE IDs via injected `fetch(url)->dict`. Returns {cves, new}.
- `_auto_refresh_loop` — line 130 — Production background loop: full KEV refresh every 24h. Never raises (logs only).
- `fetch` — line 135 — Service function/class `fetch`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.

### `backend/app/services/tool_forms.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `_base` — line 19 — Service function/class `_base`: implements part of the VEYRA security control plane. Read its module docstring first, then trace the callers in `backend/app/api/routes.py`.
- `get_form` — line 217 — Full runner schema for one registry tool dict.
- `build_contract_fields` — line 232 — Fold runner params into (target, scope, params). Raises ValueError on violations.

### `backend/app/services/vectordb.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `check_retrieval` — line 17 — Evaluate one retrieval against tenant policy. Returns {allowed, reason, known_store}.
- `log_retrieval` — line 32 — Persist the event; on DENY raise HIGH finding + audit. Returns {event, allowed, reason}.

### `backend/app/services/visibility.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `brute_force_candidates` — line 18 — Group FAILED logins by IP and username; flag ≥ `BRUTE_FORCE_THRESHOLD` (5) as candidates.
- `browsing_summary` — line 41 — Top domains by hits + per-device top domain from `DnsQuery` rows.

### `backend/requirements.txt`

Python runtime dependencies for the backend.

### `backend/tests/test_admin_tools.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_admin_tools_require_admin` — line 6 — Test symbol `test_admin_tools_require_admin`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_worker_requires_auth` — line 19 — Test symbol `test_worker_requires_auth`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_privileged_tool_requires_second_admin_gate` — line 28 — Test symbol `test_privileged_tool_requires_second_admin_gate`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_ai_gateway.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_gateway_requires_token` — line 10 — Test symbol `test_gateway_requires_token`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_gateway_enrollment_and_decision` — line 14 — Test symbol `test_gateway_enrollment_and_decision`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_gateway_blocks_unallowlisted_tool` — line 20 — Test symbol `test_gateway_blocks_unallowlisted_tool`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_ai_security.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_ai_security_catalog_and_controls` — line 6 — Test symbol `test_ai_security_catalog_and_controls`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_agent_posture` — line 17 — Test symbol `test_agent_posture`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_autonomous_soc_v21.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_autonomous_soc_investigate_and_approve` — line 6 — Test symbol `test_autonomous_soc_investigate_and_approve`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_detection_mesh_v22.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_detection_mesh_overview_and_rules` — line 8 — Test symbol `test_detection_mesh_overview_and_rules`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_alert_triggers_investigation` — line 15 — Test symbol `test_alert_triggers_investigation`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_duplicate_is_idempotent` — line 22 — Test symbol `test_duplicate_is_idempotent`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_discovery.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_mac_normalize_and_oui` — line 16 — Test symbol `test_mac_normalize_and_oui`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `_db` — line 31 — Test symbol `_db`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_upsert_matches_mac_then_updates` — line 38 — Test symbol `test_upsert_matches_mac_then_updates`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `_client` — line 55 — Test symbol `_client`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_discovery_routes` — line 65 — Test symbol `test_discovery_routes`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_execution_plane.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_execution_plane_admin_lifecycle` — line 6 — Test symbol `test_execution_plane_admin_lifecycle`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_execution_plane_non_admin` — line 25 — Test symbol `test_execution_plane_non_admin`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_fabric_v20.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_fabric_overview` — line 5 — Test symbol `test_fabric_overview`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_fabric_event_requires_collector_when_configured` — line 11 — Test symbol `test_fabric_event_requires_collector_when_configured`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_forensics.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_catalog_maps_kali_tools` — line 9 — Test symbol `test_catalog_maps_kali_tools`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_benign_text_is_low` — line 15 — Test symbol `test_benign_text_is_low`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_reverse_shell_is_critical` — line 22 — Test symbol `test_reverse_shell_is_critical`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_keyword_and_iocs_flagged` — line 28 — Test symbol `test_keyword_and_iocs_flagged`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_elf_detected` — line 36 — Test symbol `test_elf_detected`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_intel_fusion_v23.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `_seed_case` — line 9 — Test symbol `_seed_case`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_fusion_produces_intel_attack_mapping_and_hypotheses` — line 17 — Test symbol `test_fusion_produces_intel_attack_mapping_and_hypotheses`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_fusion_is_hypothesis_only` — line 24 — Test symbol `test_fusion_is_hypothesis_only`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_pentest_agents_v24.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_catalog_admin_and_plan_generation` — line 7 — Test symbol `test_catalog_admin_and_plan_generation`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_pentest_plan_rejects_unapproved_environment` — line 20 — Test symbol `test_pentest_plan_rejects_unapproved_environment`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_production.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `_db` — line 16 — Test symbol `_db`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_kev_parse_and_refresh` — line 35 — Test symbol `test_kev_parse_and_refresh`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_nvd_parse_and_refresh_caps` — line 50 — Test symbol `test_nvd_parse_and_refresh_caps`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_mitre_mapping_and_coverage` — line 60 — Test symbol `test_mitre_mapping_and_coverage`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_prowler_import_and_aws_mapping` — line 76 — Test symbol `test_prowler_import_and_aws_mapping`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_ai_eval_with_fake_gateway` — line 98 — Test symbol `test_ai_eval_with_fake_gateway`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_vectordb_policy_and_deny_finding` — line 108 — Test symbol `test_vectordb_policy_and_deny_finding`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_soar_approval_flow` — line 124 — Test symbol `test_soar_approval_flow`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `_client` — line 145 — Test symbol `_client`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_usb_auto_finding_and_collector_auth` — line 155 — Test symbol `test_usb_auto_finding_and_collector_auth`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_heartbeat_reconciles_services` — line 179 — Test symbol `test_heartbeat_reconciles_services`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_risk.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_risk_caps_at_100` — line 7 — Test symbol `test_risk_caps_at_100`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_severity` — line 10 — Test symbol `test_severity`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_teams.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `test_playbook_matrix_complete` — line 16 — Test symbol `test_playbook_matrix_complete`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_teams_have_no_exploit_instructions` — line 24 — Test symbol `test_teams_have_no_exploit_instructions`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `_client` — line 34 — Test symbol `_client`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_remediation_and_teams_endpoints` — line 46 — Test symbol `test_remediation_and_teams_endpoints`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_triage_requires_subject_and_correlates` — line 54 — Test symbol `test_triage_requires_subject_and_correlates`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_tool_governance.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `_client` — line 20 — Test symbol `_client`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `_auth` — line 42 — Test symbol `_auth`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_sudo_run_is_one_click_approved` — line 46 — Test symbol `test_sudo_run_is_one_click_approved`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_viewer_cannot_run_tools` — line 59 — Test symbol `test_viewer_cannot_run_tools`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_analyst_run_needs_grant_then_stays_pending` — line 67 — Test symbol `test_analyst_run_needs_grant_then_stays_pending`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_expired_grant_reads_as_none` — line 84 — Test symbol `test_expired_grant_reads_as_none`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_access_request_to_approval_flow` — line 98 — Test symbol `test_access_request_to_approval_flow`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_tool_form_schema_and_validation` — line 120 — Test symbol `test_tool_form_schema_and_validation`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_v12.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `db` — line 18 — Test symbol `db`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_graph_builds` — line 44 — Test symbol `test_graph_builds`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_attack_path_reaches_sensitive` — line 51 — Test symbol `test_attack_path_reaches_sensitive`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_answers` — line 58 — Test symbol `test_answers`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_validate_target_rejects` — line 64 — Test symbol `test_validate_target_rejects`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_validate_target_private_flag` — line 73 — Test symbol `test_validate_target_private_flag`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_score_headers` — line 78 — Test symbol `test_score_headers`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `backend/tests/test_visibility.py`

Automated regression tests for the named subsystem.

**Symbols:**
- `_db` — line 19 — Test symbol `_db`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_brute_force_candidate_flagged` — line 26 — Test symbol `test_brute_force_candidate_flagged`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_browsing_summary_counts` — line 37 — Test symbol `test_browsing_summary_counts`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_eml_phish_flags` — line 49 — Test symbol `test_eml_phish_flags`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_office_macro_flags` — line 59 — Test symbol `test_office_macro_flags`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `_pcap_one_dns` — line 69 — Test symbol `_pcap_one_dns`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.
- `test_pcap_dns_parsed_and_flagged` — line 83 — Test symbol `test_pcap_dns_parsed_and_flagged`: verifies a focused contract of the VEYRA backend. Run the individual test file while changing this area.

### `collectors/endpoint-agent.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `sh` — line 43 — Endpoint/sensor function `sh`: gathers or transforms local security telemetry before sending it to VEYRA.
- `identity` — line 50 — Endpoint/sensor function `identity`: gathers or transforms local security telemetry before sending it to VEYRA.
- `listening_ports` — line 61 — Parse listening TCP ports; returns [{port, protocol, service, process, user}].
- `usb_devices` — line 81 — List USB devices (names only — no content). Returns [{device, serial, action}].
- `dlp_scan` — line 98 — Regex secret-pattern scan of watched dirs (filenames + first 64KB). Returns DLP items.
- `post` — line 122 — Endpoint/sensor function `post`: gathers or transforms local security telemetry before sending it to VEYRA.
- `run_once` — line 131 — Endpoint/sensor function `run_once`: gathers or transforms local security telemetry before sending it to VEYRA.
- `local_subnet` — line 146 — Own /24 from the default-route source IP (UDP connect sends nothing).
- `ping_one` — line 158 — Endpoint/sensor function `ping_one`: gathers or transforms local security telemetry before sending it to VEYRA.
- `arp_map` — line 167 — Current IP→(mac, host?) from the arp table (no packets sent).
- `_dns_name` — line 181 — Decode a (possibly compressed) DNS name at offset; returns (name, next_off).
- `mdns_reverse` — line 205 — mDNS (Bonjour) reverse lookup: many home devices answer .local PTR even
- `netbios_name` — line 251 — NetBIOS node-status query (Windows/Samba boxes). UDP/137, read-only.
- `rdns` — line 278 — Best-effort device name: unicast rDNS → mDNS → NetBIOS → generated label.
- `default_gateway` — line 297 — Default-gateway IP via system route table (no packets). Returns '' when unknown.
- `run_discovery` — line 309 — Ping-sweep a PRIVATE subnet, merge arp MACs, post neighbours.
- `_wifi_scan_corewlan_helper` — line 384 — Modern macOS (airport CLI removed): run the CoreWLAN scan via the
- `wifi_scan` — line 411 — Return nearby Wi-Fi metadata using the host OS native read-only scanner.
- `wifi_current` — line 452 — Best-effort current SSID; no credentials or password material.
- `run_sensor` — line 472 — Endpoint/sensor function `run_sensor`: gathers or transforms local security telemetry before sending it to VEYRA.
- `Handler` — line 474 — Endpoint/sensor function `Handler`: gathers or transforms local security telemetry before sending it to VEYRA.
- `_json` — line 475 — Endpoint/sensor function `_json`: gathers or transforms local security telemetry before sending it to VEYRA.
- `do_OPTIONS` — line 477 — Endpoint/sensor function `do_OPTIONS`: gathers or transforms local security telemetry before sending it to VEYRA.
- `do_GET` — line 478 — Endpoint/sensor function `do_GET`: gathers or transforms local security telemetry before sending it to VEYRA.
- `log_message` — line 483 — Endpoint/sensor function `log_message`: gathers or transforms local security telemetry before sending it to VEYRA.

### `collectors/wifi-scan-jit.swift`

macOS Wi-Fi helper used by the local read-only sensor.

### `collectors/wifi-scan-macos`

Project support/resource file.

### `collectors/wifi-scan-macos.swift`

macOS Wi-Fi helper used by the local read-only sensor.

### `collectors/wifi-sensor-app.swift`

macOS Wi-Fi helper used by the local read-only sensor.

### `docker-compose.yml`

Local orchestration for PostgreSQL, FastAPI backend, and React frontend. Production should replace default credentials, expose services through TLS, and use a secrets manager.

### `docs/ADMIN_ETHICAL_HACKING.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/AI_AGENT_SECURITY_CONTROL_PLANE.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/AI_GATEWAY_RUNTIME.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/AI_LATEST_2026.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/AI_SECURITY_ARCHITECTURE.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/AUTONOMOUS_SOC_V21.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/CODEBASE_GUIDE_V27.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/COMPLETE_TOOL_EDUCATION_GUIDE_V25.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/DETECTION_RESPONSE_MESH_V22.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/FORENSICS_GUIDE.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/HELP.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/IDENTITY_PERMISSIONS_V25.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/INCIDENT_REVERSE_ENGINEERING.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/INTEL_FUSION_V23.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/LAB_GUIDE.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/NETWORK_VISIBILITY_GUIDE.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/PENTEST_AGENTS_V24.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/POC_ROADMAP.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/PRODUCTION_GUIDE.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/SECURITY_FABRIC_V20.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/TOOLING_MATRIX.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/TOOL_ACCESS_MATRIX_V24.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/TOOL_ECOSYSTEM_V27.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/TOOL_HELP_CATALOG_V27.md`

Product documentation. See the document heading for the specific control-plane area.

### `docs/TOOL_RUNNER_V26.md`

Product documentation. See the document heading for the specific control-plane area.

### `examples/local_agent_gateway.py`

Python implementation file in the VEYRA backend/collector/lab layers.

### `frontend/Dockerfile`

Container build definition.

### `frontend/index.html`

Vite HTML entry document containing the root element used by React.

### `frontend/package-lock.json`

JSON/package configuration used by the application or frontend build.

### `frontend/package.json`

Frontend scripts and dependency manifest. `npm run dev` starts Vite; `npm run build` creates the production bundle.

### `frontend/src/main.jsx`

Main React application: navigation, views, Tool Runner, Marketplace, Tool Academy, network panels, and API calls.

**Detected components/helpers:**
- `sevHelp` — around line 38 — Frontend symbol `sevHelp`: renders or supports a React console capability. Backend authorization remains authoritative.
- `whyFinding` — around line 40 — Frontend symbol `whyFinding`: renders or supports a React console capability. Backend authorization remains authoritative.
- `whyIdentity` — around line 50 — Frontend symbol `whyIdentity`: renders or supports a React console capability. Backend authorization remains authoritative.
- `whyCloud` — around line 57 — Frontend symbol `whyCloud`: renders or supports a React console capability. Backend authorization remains authoritative.
- `whyPort` — around line 63 — Frontend symbol `whyPort`: renders or supports a React console capability. Backend authorization remains authoritative.
- `whyFlow` — around line 66 — Frontend symbol `whyFlow`: renders or supports a React console capability. Backend authorization remains authoritative.
- `whySession` — around line 70 — Frontend symbol `whySession`: renders or supports a React console capability. Backend authorization remains authoritative.
- `AdminEthicalHacking` — around line 77 — Frontend symbol `AdminEthicalHacking`: renders or supports a React console capability. Backend authorization remains authoritative.
- `headers` — around line 81 — Frontend symbol `headers`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 82 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `unlock` — around line 84 — Frontend symbol `unlock`: renders or supports a React console capability. Backend authorization remains authoritative.
- `clear` — around line 85 — Frontend symbol `clear`: renders or supports a React console capability. Backend authorization remains authoritative.
- `stage` — around line 86 — Frontend symbol `stage`: renders or supports a React console capability. Backend authorization remains authoritative.
- `action` — around line 87 — Frontend symbol `action`: renders or supports a React console capability. Backend authorization remains authoritative.
- `SecurityFabricView` — around line 113 — Frontend symbol `SecurityFabricView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `DetectionMeshView` — around line 119 — Frontend symbol `DetectionMeshView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `h` — around line 122 — Frontend symbol `h`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 123 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `send` — around line 125 — Frontend symbol `send`: renders or supports a React console capability. Backend authorization remains authoritative.
- `AutonomousSOCView` — around line 129 — Frontend symbol `AutonomousSOCView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `headers` — around line 131 — Frontend symbol `headers`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 132 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `investigate` — around line 134 — Frontend symbol `investigate`: renders or supports a React console capability. Backend authorization remains authoritative.
- `approve` — around line 135 — Frontend symbol `approve`: renders or supports a React console capability. Backend authorization remains authoritative.
- `PentestAgentsView` — around line 139 — Frontend symbol `PentestAgentsView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `h` — around line 141 — Frontend symbol `h`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 142 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `create` — around line 144 — Frontend symbol `create`: renders or supports a React console capability. Backend authorization remains authoritative.
- `LoginView` — around line 148 — Frontend symbol `LoginView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `login` — around line 150 — Frontend symbol `login`: renders or supports a React console capability. Backend authorization remains authoritative.
- `PasswordView` — around line 154 — Frontend symbol `PasswordView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `save` — around line 156 — Frontend symbol `save`: renders or supports a React console capability. Backend authorization remains authoritative.
- `UserPermissionsView` — around line 160 — Frontend symbol `UserPermissionsView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `auth` — around line 162 — Frontend symbol `auth`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 163 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `blank` — around line 165 — Frontend symbol `blank`: renders or supports a React console capability. Backend authorization remains authoritative.
- `create` — around line 167 — Frontend symbol `create`: renders or supports a React console capability. Backend authorization remains authoritative.
- `update` — around line 168 — Frontend symbol `update`: renders or supports a React console capability. Backend authorization remains authoritative.
- `setLevel` — around line 169 — Frontend symbol `setLevel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `selGrants` — around line 170 — Frontend symbol `selGrants`: renders or supports a React console capability. Backend authorization remains authoritative.
- `tools` — around line 172 — Frontend symbol `tools`: renders or supports a React console capability. Backend authorization remains authoritative.
- `level` — around line 173 — Frontend symbol `level`: renders or supports a React console capability. Backend authorization remains authoritative.
- `ToolAcademyView` — around line 177 — Frontend symbol `ToolAcademyView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `ToolRunnerView` — around line 184 — Frontend symbol `ToolRunnerView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `auth` — around line 185 — Frontend symbol `auth`: renders or supports a React console capability. Backend authorization remains authoritative.
- `eff` — around line 195 — Frontend symbol `eff`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 196 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `open` — around line 207 — Frontend symbol `open`: renders or supports a React console capability. Backend authorization remains authoritative.
- `setV` — around line 212 — Frontend symbol `setV`: renders or supports a React console capability. Backend authorization remains authoritative.
- `run` — around line 213 — Frontend symbol `run`: renders or supports a React console capability. Backend authorization remains authoritative.
- `endpoint` — around line 219 — Frontend symbol `endpoint`: renders or supports a React console capability. Backend authorization remains authoritative.
- `ask` — around line 226 — Frontend symbol `ask`: renders or supports a React console capability. Backend authorization remains authoritative.
- `decide` — around line 234 — Frontend symbol `decide`: renders or supports a React console capability. Backend authorization remains authoritative.
- `field` — around line 242 — Frontend symbol `field`: renders or supports a React console capability. Backend authorization remains authoritative.
- `lvlBadge` — around line 251 — Frontend symbol `lvlBadge`: renders or supports a React console capability. Backend authorization remains authoritative.
- `App` — around line 273 — Frontend symbol `App`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 288 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `investigate` — around line 290 — Frontend symbol `investigate`: renders or supports a React console capability. Backend authorization remains authoritative.
- `go` — around line 291 — Frontend symbol `go`: renders or supports a React console capability. Backend authorization remains authoritative.
- `logout` — around line 292 — Frontend symbol `logout`: renders or supports a React console capability. Backend authorization remains authoritative.
- `ToolMarketplace` — around line 302 — Frontend symbol `ToolMarketplace`: renders or supports a React console capability. Backend authorization remains authoritative.
- `auth` — around line 304 — Frontend symbol `auth`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 305 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `install` — around line 307 — Frontend symbol `install`: renders or supports a React console capability. Backend authorization remains authoritative.
- `IntelFusionView` — around line 319 — Frontend symbol `IntelFusionView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 321 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `Overview` — around line 326 — Frontend symbol `Overview`: renders or supports a React console capability. Backend authorization remains authoritative.
- `Card` — around line 342 — Frontend symbol `Card`: renders or supports a React console capability. Backend authorization remains authoritative.
- `Panel` — around line 343 — Frontend symbol `Panel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `DrillModal` — around line 346 — Frontend symbol `DrillModal`: renders or supports a React console capability. Backend authorization remains authoritative.
- `DetailModal` — around line 360 — Frontend symbol `DetailModal`: renders or supports a React console capability. Backend authorization remains authoritative.
- `NetworkView` — around line 385 — Frontend symbol `NetworkView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `Ops` — around line 386 — Frontend symbol `Ops`: renders or supports a React console capability. Backend authorization remains authoritative.
- `IdentityView` — around line 387 — Frontend symbol `IdentityView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `CloudView` — around line 388 — Frontend symbol `CloudView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `AIGatewayPanel` — around line 389 — Frontend symbol `AIGatewayPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `evaluate` — around line 391 — Frontend symbol `evaluate`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 392 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `AgentSecurityPanel` — around line 397 — Frontend symbol `AgentSecurityPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `assess` — around line 400 — Frontend symbol `assess`: renders or supports a React console capability. Backend authorization remains authoritative.
- `AIView` — around line 404 — Frontend symbol `AIView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `EndpointView` — around line 405 — Frontend symbol `EndpointView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `DataView` — around line 406 — Frontend symbol `DataView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `GovView` — around line 407 — Frontend symbol `GovView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `Placeholder` — around line 408 — Frontend symbol `Placeholder`: renders or supports a React console capability. Backend authorization remains authoritative.
- `GraphView` — around line 409 — Frontend symbol `GraphView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `OffensiveView` — around line 410 — Frontend symbol `OffensiveView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `run` — around line 410 — Frontend symbol `run`: renders or supports a React console capability. Backend authorization remains authoritative.
- `ForensicsView` — around line 411 — Frontend symbol `ForensicsView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `up` — around line 411 — Frontend symbol `up`: renders or supports a React console capability. Backend authorization remains authoritative.
- `SevPlay` — around line 412 — Frontend symbol `SevPlay`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 412 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `RedTeamView` — around line 413 — Frontend symbol `RedTeamView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `BlueTeamView` — around line 414 — Frontend symbol `BlueTeamView`: renders or supports a React console capability. Backend authorization remains authoritative.
- `run` — around line 414 — Frontend symbol `run`: renders or supports a React console capability. Backend authorization remains authoritative.
- `ThreatPanels` — around line 415 — Frontend symbol `ThreatPanels`: renders or supports a React console capability. Backend authorization remains authoritative.
- `refresh` — around line 415 — Frontend symbol `refresh`: renders or supports a React console capability. Backend authorization remains authoritative.
- `CloudOpsPanel` — around line 416 — Frontend symbol `CloudOpsPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `imp` — around line 416 — Frontend symbol `imp`: renders or supports a React console capability. Backend authorization remains authoritative.
- `scan` — around line 416 — Frontend symbol `scan`: renders or supports a React console capability. Backend authorization remains authoritative.
- `AiOpsPanel` — around line 417 — Frontend symbol `AiOpsPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `audit` — around line 417 — Frontend symbol `audit`: renders or supports a React console capability. Backend authorization remains authoritative.
- `run` — around line 417 — Frontend symbol `run`: renders or supports a React console capability. Backend authorization remains authoritative.
- `UsbDlpPanel` — around line 418 — Frontend symbol `UsbDlpPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `SoarPanel` — around line 419 — Frontend symbol `SoarPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `approve` — around line 419 — Frontend symbol `approve`: renders or supports a React console capability. Backend authorization remains authoritative.
- `load` — around line 419 — Frontend symbol `load`: renders or supports a React console capability. Backend authorization remains authoritative.
- `start` — around line 419 — Frontend symbol `start`: renders or supports a React console capability. Backend authorization remains authoritative.
- `WifiPanel` — around line 420 — Frontend symbol `WifiPanel`: renders or supports a React console capability. Backend authorization remains authoritative.
- `loadLan` — around line 426 — Frontend symbol `loadLan`: renders or supports a React console capability. Backend authorization remains authoritative.
- `scan` — around line 427 — Frontend symbol `scan`: renders or supports a React console capability. Backend authorization remains authoritative.
- `trust` — around line 428 — Frontend symbol `trust`: renders or supports a React console capability. Backend authorization remains authoritative.
- `modeSsid` — around line 431 — Frontend symbol `modeSsid`: renders or supports a React console capability. Backend authorization remains authoritative.

### `frontend/src/styles.css`

Global console styling.

### `installers/VEYRA WiFi Sensor.app/Contents/Info.plist`

Project support/resource file.

### `installers/VEYRA WiFi Sensor.app/Contents/MacOS/VEYRA WiFi Sensor`

Project support/resource file.

### `installers/VEYRA WiFi Sensor.app/Contents/MacOS/wifi-scan-macos`

Project support/resource file.

### `installers/VEYRA WiFi Sensor.app/Contents/_CodeSignature/CodeResources`

Project support/resource file.

### `installers/README_WIFI_SENSOR.md`

Markdown documentation.

### `installers/com.aegisx.wifi-sensor.plist`

Project support/resource file.

### `lab/collector.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `arp_table` — line 33 — Lab/demo function `arp_table`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `ping_sweep` — line 52 — Lab/demo function `ping_sweep`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `post` — line 76 — Lab/demo function `post`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.

### `lab/red_blue_demo.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `call` — line 11 — Lab/demo function `call`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.

### `lab/vulnerable-web/Dockerfile`

Container build definition.

### `lab/vulnerable-web/app.py`

Python implementation file in the VEYRA backend/collector/lab layers.

**Symbols:**
- `index` — line 17 — Lab/demo function `index`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `admin` — line 26 — Lab/demo function `admin`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `robots` — line 31 — Lab/demo function `robots`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `users` — line 35 — Lab/demo function `users`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `ai_chat` — line 41 — Lab/demo function `ai_chat`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.
- `banner` — line 51 — Lab/demo function `banner`: supports isolated demonstration or test data generation; keep lab assets separate from customer systems.

### `lab/vulnerable-web/requirements.txt`

Project support/resource file.

### `package-lock.json`

JSON/package configuration used by the application or frontend build.

## Feature-to-code map

| Feature | Backend route/service | Data model | Frontend | Primary docs |
|---|---|---|---|---|
| Identity / Sudo / password | `routes.py` + `auth.py` | `UserAccount`, `UserSession`, `UserToolPermission` | `UserPermissionsView`, `LoginView`, `PasswordView` | `IDENTITY_PERMISSIONS_V25.md` |
| Tool registry | `admin_tools.py` + `extended_catalog.py` | tool metadata is registry-backed | `ToolAcademyView`, `ToolRunnerView`, `ToolMarketplace` | `TOOL_ECOSYSTEM_V27.md`, `TOOLING_MATRIX.md` |
| Tool Runner | `execution_plane.py`, `tool_forms.py`, `routes.py` | `SecurityToolJob`, `SecurityEvidence` | `ToolRunnerView` | `TOOL_RUNNER_V26.md` |
| Wi-Fi / LAN | `discovery.py`, collector | `WifiNetwork`, `DiscoveredHost` | `WifiPanel`, `NetworkView` | `NETWORK_VISIBILITY_GUIDE.md` |
| AI gateway | `ai_gateway.py` | `AgentPolicy`, `AgentRuntimeEvent` | `AIGatewayPanel` | `AI_GATEWAY_RUNTIME.md` |
| AI security | `ai_security.py`, `ai_red.py`, `vectordb.py` | `AIAsset`, `RetrievalEvent` | `AIView`, security panels | `AI_SECURITY_ARCHITECTURE.md` |
| SOC | `autonomous_soc.py`, `response_mesh.py`, `soar.py` | investigation/detection/response models | `AutonomousSOCView`, `DetectionMeshView`, `SoarPanel` | corresponding v2.x docs |
| Threat intel | `threatintel.py`, `intel_fusion.py`, `mitre.py` | `CveRecord`, `ThreatIntel`, `IntelEnrichment`, `AttributionHypothesis` | `ThreatPanels`, `IntelFusionView` | `INTEL_FUSION_V23.md` |
| Security Graph | `graph.py`, `fabric.py` | `UnifiedSecurityEvent` + asset relationships | `GraphView` | `SECURITY_FABRIC_V20.md` |
| Cloud | `cloud_adapters.py` | `CloudResource` | `CloudView`, `CloudOpsPanel` | `PRODUCTION_GUIDE.md`, `TOOL_ECOSYSTEM_V27.md` |
| Forensics | `forensics.py` | findings/evidence models | `ForensicsView` | `FORENSICS_GUIDE.md` |

## Security-tool change checklist

- Add or update registry metadata.
- Set the correct access tier (`admin` or `privileged_admin`).
- Set an execution profile and worker requirement.
- Add a guided form with named profiles rather than raw shell flags.
- Add Tool Academy help and safe operational guidance.
- Add installation metadata and provenance requirements.
- Add evidence normalization/parsing if the tool emits structured results.
- Add authorization/approval tests.
- Update `TOOLING_MATRIX.md`, `TOOL_ACCESS_MATRIX_V24.md` (or successor), and `TOOL_ECOSYSTEM_V27.md`.
- Update `README.md`, `TERMINAL_RUNBOOK.md`, and `TODO.md` when user-facing behavior changes.

## Important boundary

VEYRA is a control plane. The SaaS API should not become an unrestricted shell. High-impact security tools execute only on an explicitly registered, isolated, authorized worker after backend policy, scope, role, approval, and provenance checks. This keeps the UI powerful while preserving tenant isolation and auditability.

## v2.8 additions

### `backend/app/services/ai_ecosystem.py`

Contains the 111-entry AI security ecosystem catalog. It is metadata only and does not execute tools. `registry()` returns normalized AI tool cards; `overview()` returns category counts.

### `WorkerNode` and `WorkerToolInstall`

These models separate the global catalog from the actual state of tools on a managed worker. This prevents the UI from implying that a cataloged tool is necessarily installed or healthy.

### Worker APIs

The worker API family is in `backend/app/api/routes.py` under the v2.8 section. The POC currently uses authenticated console/admin access for registration and reporting. Production should replace this with short-lived workload identity and signed worker messages.

### Frontend `AIEcosystemView`

Searches and filters the 111 AI security integration candidates. It is deliberately read/catalog oriented; it does not expose arbitrary AI-tool command lines.

### Frontend `SecurityWorkersView`

Shows managed worker registration, platform, capabilities and online state. It is the beginning of the v2.8 worker control plane.
