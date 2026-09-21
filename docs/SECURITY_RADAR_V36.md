# VEYRA v3.6 — Security Radar

VEYRA now treats the security-tool ecosystem as a continuously scouted supply chain. Radar items are separated into **recommended** and **experimental** maturity so emerging projects are visible without being silently promoted into production execution.

## Latest recommendations

- **OWASP Agent Control Standard (ACS):** use as a reference architecture for inspectable, traceable, instrumentable agents and runtime middleware enforcement.
- **OWASP GenAI Security Industry Framework Crosswalk:** use to map AI findings to established governance/security frameworks.
- **Kyverno:** Kubernetes policy and governance; current 2026 guidance highlights safer HTTP policy execution and newer policy types.
- **Inspektor Gadget:** eBPF-based Kubernetes/Linux runtime inspection; its 2026 security audit and patches make it useful for runtime evidence.
- **Prempti:** experimental Falco-ecosystem work for AI-agent tool-call lifecycle visibility.
- **MCP Shield Runtime / Pipelock / Adrian / SINT Protocol:** experimental community candidates for MCP/agent runtime authorization, egress, intervention and signed evidence.
- **OpenSSF Scorecard / TUF / GUAC:** strengthen repository risk, update trust and supply-chain evidence correlation.

## Promotion lifecycle

`Scout → Verify provenance → Review security → Review license → Pin version → Generate SBOM → Test on isolated worker → Document → Pilot → Measure → Promote or retire`

## Safety boundary

Radar entries do not grant execution rights. High-impact or experimental capabilities remain behind VEYRA RBAC/Sudo, explicit scope, approval, isolated workers and evidence capture.

## v3.7 integration notes

The radar recommendations are now connected conceptually to Graph Intelligence. Mature candidates should become graph-visible controls, evidence sources or worker capabilities only after provenance, version, licensing, SBOM and worker validation. OWASP ACS is especially relevant to agent runtime nodes and policy relationships; Kyverno to Kubernetes policy relationships; TUF/Scorecard to worker and repository provenance; and Inspektor Gadget to runtime telemetry.
