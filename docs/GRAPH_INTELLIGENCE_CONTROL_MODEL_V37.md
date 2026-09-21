# VEYRA v3.7 — Graph Intelligence Control Model

## Data model

```text
Asset ── Service
  │        │
  ├── Identity / Session
  ├── Network Flow
  ├── Finding
  ├── Incident
  └── Evidence

Cloud Resource ── Finding / Evidence

AI Asset ── Agent Runtime / Tool / Retrieval / Evidence

Worker ── Tool Job ── Evidence Receipt

Control ── Finding ── Remediation ── Validation
```

## Design law

A relationship should be explainable from persisted telemetry. AI can rank, summarize and propose hypotheses; it must not silently invent authoritative graph edges.

## Latest ecosystem alignment

- OWASP Agent Control Standard: runtime inspection, traceability, instrumentation and policy enforcement. citeturn0search12
- NIST CSF 2.0: Govern, Identify, Protect, Detect, Respond, Recover. citeturn0search14
- MITRE ATLAS: AI adversary tactics/techniques and case studies. citeturn0search18
- Kyverno: policy-as-code and image verification for Kubernetes/cloud-native resources. citeturn1search1turn1search2
- TUF: resilient software update trust, including protection against repository or signing-key compromise. citeturn1search0turn1search4
- OpenSSF Scorecard: automated repository security-health checks. citeturn1search15
- Inspektor Gadget: eBPF-based Kubernetes/Linux inspection with a published 2026 security audit. citeturn0search7

## Production recommendation

The current v3.7 implementation is a deterministic read model. For production scale, move graph persistence to a dedicated graph store only after the relationship contract, provenance model and tenancy boundaries are stable. The existing PostgreSQL records remain authoritative until that migration is deliberately designed and tested.
