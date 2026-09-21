# VEYRA v2.3 — Autonomous Investigation & Threat Intelligence Fusion

v2.3 connects the Detection & Response Mesh to deterministic threat-intelligence enrichment, DFIR evidence provenance, ATT&CK/ATLAS behavior mapping and evidence-backed attribution hypotheses.

## Investigation flow

```text
Detection Mesh
  → Investigation Case
  → Evidence Preservation
  → Local Threat-Intel Correlation
  → ATT&CK / ATLAS Mapping
  → DFIR Evidence References
  → Attribution Hypotheses
  → Risk + Confidence
  → Human Approval
  → Governed Response
  → Verification
```

### Guardrails
- Attribution is **hypothesis-only** and never asserts an actor identity.
- Intelligence correlation is deterministic and local to the ingested corpus.
- AI can summarize the bundle but cannot authorize response or change evidence.
- Raw evidence remains outside the model prompt unless explicitly collected through governed connectors.
- No hack-back, exploitation, persistence, credential attacks or unrestricted execution are added.

## Current framework alignment
VEYRA maps agentic investigation controls to the OWASP Top 10 for Agentic Applications 2026 and NIST AI RMF / GenAI Profile. The design specifically treats tool misuse, identity/privilege abuse and supply-chain risks as control-plane concerns rather than relying on the model alone.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
