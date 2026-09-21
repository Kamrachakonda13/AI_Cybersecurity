# VEYRA v3.1 — Sudo Security Arsenal

## Design
The Sudo Security Arsenal is the privileged security-tool control plane. It brings Kali-style breadth into VEYRA without turning the SaaS into an unrestricted attack console. Kali itself groups tools into metapackages such as 802.11, Bluetooth, RFID, SDR, web, exploitation, forensics, reverse engineering and wireless; VEYRA mirrors those operational domains while adding cloud, Kubernetes, AI, governance and evidence controls. citeturn0search0turn0search1

## Security gate

```text
User → Role → Tool Permission → Sudo → Scope → Approval → Signed Job → Managed Worker → Evidence → Audit
```

High-impact tooling uses a stronger gate:

```text
Sudo + MFA + Justification + Target Scope + Approval + Time-Limited Capability + Isolated Worker + Evidence
```

## Tool classes
- Network and attack-surface discovery
- Web/API and application security
- Wireless / Wi-Fi / Bluetooth / RFID / SDR
- Identity and directory security
- Credential auditing
- Cloud and Kubernetes
- AppSec / IaC / supply chain
- Endpoint / NDR / WIDS
- DFIR / malware / reverse engineering
- Threat intelligence / detection engineering
- AI / LLM / agent / MCP / RAG security

## UI contract
Every tool must expose:
- purpose
- access tier
- execution profile
- approved scope fields
- expected evidence
- safe workflow
- common mistakes
- remediation/verification next step
- terminal start/help command

## Installation
Third-party tools are not bundled into the SaaS image. Installation is represented as a worker-side manifest with source provenance, version pinning, signature/hash verification and SBOM. Kali documents `kali-linux-everything` as the broadest metapackage; VEYRA intentionally keeps the SaaS image separate from that worker environment. citeturn0search1

## Why this matters
The platform must be capable enough for serious red/blue/purple-team work while remaining auditable. Tool breadth comes from the managed worker catalog; control comes from scope, approvals, isolation and evidence.

## v3.1.1 documentation rule

The authoritative team-facing help is `TOOL_USAGE_CATALOG_V31.md`. It contains an entry for **every current catalog tool/integration (577 after de-duplication)** and is regenerated from the same registry used by the Sudo Arsenal API.

For AI security specialists, also use `AI_CUTTING_EDGE_2026_TEAM_GUIDE.md` and `AI_LATEST_2026.md`.
