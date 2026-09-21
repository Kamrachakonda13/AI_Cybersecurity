# VEYRA v3.9 — Autonomous Exposure Validation Fabric

## Purpose

VEYRA v3.9 turns the security lifecycle into a continuous exposure-validation loop across **Windows, macOS, Linux, Kubernetes, Cloud and AI agents**.

**Discover → Fingerprint → Correlate → Validate → Investigate → Contain (approval) → Remediate → Independently Prove → Revalidate**

The service is deliberately plan-first. Deterministic endpoint, identity, network, cloud, Kubernetes and agent telemetry remains authoritative; AI can prioritize and explain hypotheses but cannot author policy or execute remediation.

## AI Security Research Lab

The Research Lab is inspired by the agentic vulnerability-discovery direction demonstrated by Microsoft's MDASH, but VEYRA applies stricter tenant and execution boundaries.

It is designed to:

1. fingerprint managed assets and AI agents;
2. correlate vendor advisories/CVEs/KEV with observed versions and builds;
3. compare agent identity, tool calls, operations and policy decisions;
4. detect anomalous or unregistered agents;
5. correlate endpoint findings with identities, network activity and Security Graph relationships;
6. reconstruct an evidence-backed timeline;
7. generate a containment/remediation plan;
8. require human approval for response;
9. independently validate remediation and preserve proof.

## Rogue-agent investigation

VEYRA should answer five questions without guessing:

- **Who?** Agent identity, provider/model, user/service identity and endpoint.
- **When?** First seen, last seen and event-level timestamps.
- **Where?** Endpoint, source IP, cloud/Kubernetes workload, service and destination.
- **How?** Policy mismatch, credential anomaly, vulnerable endpoint, unexpected tool use, lateral movement or external communication where evidence supports it.
- **Why/root cause?** The earliest supported control failure, not an AI-generated narrative.

### Detection signals

High-value signals include:

- agent identity absent from registry;
- tool outside allowlist;
- denied/blocked policy actions followed by continued activity;
- unusually high-risk operations;
- abnormal user/session behavior;
- privileged identity anomalies;
- vulnerable endpoint correlated with agent activity;
- unexpected egress/network flows;
- multi-agent coordination patterns;
- sudden changes in timing, tools or providers.

A single signal is not proof of a rogue agent. VEYRA should score multiple independent signals and preserve their evidence references.

## Containment playbook

1. Preserve telemetry and hash evidence.
2. Stage agent identity/session/API-key revocation.
3. Stage endpoint quarantine/isolation.
4. Remove unauthorized MCP/A2A/tool trust.
5. Patch confirmed OS/application exposure.
6. Hunt for the same identity, credential, trace, IP, artifact and tool fingerprints.
7. Revalidate controls independently.
8. Close only when fresh evidence proves the condition is remediated.

No SaaS workflow should provide arbitrary shell access, credential theft, persistence, destructive actions, exploit delivery or hack-back.

## Windows / macOS / Linux / Kubernetes / Cloud

The product must distinguish **inventory** from **exposure**. A platform label is not evidence of a vulnerability.

Exposure determination should require:

- exact OS/build/package/image version;
- installed software and security update state;
- vendor advisory/CVE mapping;
- exploitability/KEV context where applicable;
- asset criticality and exposure;
- identity reachability;
- network and cloud/Kubernetes relationships;
- fresh validation evidence.

## Evidence model

Every material finding should be capable of producing:

- source;
- timestamp;
- actor/identity;
- target;
- trace ID;
- evidence receipt;
- SHA-256;
- before/after posture snapshot;
- validation result;
- reviewer/approval reference.

## Research boundary

VEYRA may perform authorized security research against explicitly enrolled assets through isolated workers and approved contracts. The Research Lab itself is an analysis and validation planner; it does not create unrestricted offensive capability.
