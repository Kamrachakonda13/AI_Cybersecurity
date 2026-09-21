# VEYRA v2.7 — Security Tool Ecosystem & Managed Worker Model

## What changed

The current catalog contains **477 registered entries**, and every entry now carries a machine-readable help card consumed by the Tool Academy/Marketplace. The human-readable export is [`TOOL_HELP_CATALOG_V27.md`](TOOL_HELP_CATALOG_V27.md).

VEYRA now exposes a single governed catalog for the base security tools plus an
extended catalog derived from the current Kali Linux 2026.3.2 `kali-linux-everything`
inventory, with additional enterprise cloud, AppSec, DFIR, identity, network and
AI-security integrations.

The catalog is **metadata, policy and UI control-plane integration**. It does not
bundle third-party binaries into the SaaS container and it does not expose an
arbitrary browser shell.

## Tool lifecycle

```text
Discover
  ↓
Catalog + purpose + risk tier
  ↓
Customer selects a managed worker
  ↓
Signed package/provenance manifest
  ↓
Sudo / Security Admin approval where required
  ↓
Worker-side installation
  ↓
Version + SBOM + hash verification
  ↓
Tool Runner guided form
  ↓
Scoped job contract
  ↓
Isolated worker
  ↓
Evidence + provenance + audit
```

## Access tiers

- **Standard admin** — defensive, read-only, analysis and approved assessment tooling.
- **Privileged admin** — high-impact offensive, credential-audit, wireless, identity
  attack-surface and remote-access tooling. Requires the stronger privileged gate.
- **Sudo** — the sole VEYRA super-administrator and final approval authority.
- Customer roles continue to use `view`, `plan`, and `execute_request` entitlements.
  The API remains authoritative even when the UI grants a button.

## UI surfaces

### Tool Runner
Kali-style guided forms. Users select a tool and named capability profile instead
of entering arbitrary shell flags. Sudo jobs can be queued directly to the managed
worker; other users can submit a request for approval.

### Tool Marketplace
Search and filter the complete catalog and request installation on a managed worker.
The SaaS API does not run `apt`, `pip`, PowerShell or shell commands.

### Tool Academy
Every tool has category-level education: purpose, safe operating boundary, evidence
to expect and how the result should feed the Security Graph/SOC.

## Installation model

A customer-owned or VEYRA-managed security worker is the correct place for Kali
binaries. The worker should:

1. authenticate with a short-lived worker identity;
2. accept only signed VEYRA installation manifests;
3. allow only approved package identifiers;
4. pin versions;
5. verify package signatures and hashes;
6. generate an SBOM;
7. report installed version and health;
8. quarantine or roll back failed installations.

Do not put a generic `apt install <user input>` endpoint in the SaaS API.

## Coverage

The extended catalog includes Kali categories such as:

- information gathering / OSINT
- vulnerability analysis
- web/API
- database
- passwords
- wireless / 802.11 / Bluetooth / RFID / SDR
- exploitation and exploit validation
- post-exploitation
- sniffing/spoofing
- reverse engineering
- forensics
- reporting and detection
- Windows/identity resources

It also adds enterprise-oriented capabilities for:

- AWS/Azure/GCP and Kubernetes security
- SBOM and software supply chain
- SAST/SCA/IaC
- DFIR and detection engineering
- identity/AD security
- network exposure and NSM
- LLM/agent red evaluation and runtime security
- MCP/A2A/agent governance
- model and dataset supply-chain security

Kali's current `kali-linux-everything` metapackage is the reference for the Kali
catalog; it is intentionally treated as a moving inventory rather than a hard-coded
claim that every future package will always be present.

## Safety and customer operation

VEYRA can support red team, blue team, purple team, DFIR and AI-security workflows,
but high-impact activity must remain explicitly scoped and governed. The platform
does not provide hack-back, persistence, unrestricted payload delivery, credential
attacks against arbitrary accounts, or an unrestricted web shell.

Educational help text should explain **what the tool does, when to use it, expected
evidence, prerequisites and defensive interpretation**. It should not become a
step-by-step attack recipe.

## Current AI-security alignment

VEYRA should map AI tooling and findings to:

- OWASP GenAI LLM Top 10 2026
- OWASP Top 10 for Agentic Applications 2026
- OWASP Agent Control Standard
- MITRE ATLAS
- NIST AI RMF / GenAI Profile
- OpenTelemetry GenAI traces
- software/model/dataset provenance and SBOM/AIBOM

The 2026 OWASP material explicitly emphasizes agent identity/privilege, tool misuse,
agentic supply chain, unexpected code execution and memory/context risks. These are
first-class VEYRA control domains.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
