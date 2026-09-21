# AI Research Lab Control Model — v3.9

## Design principle

The advantage is not a single model. The advantage is a governed multi-model/worker system with strong evidence, isolation, evaluation and remediation loops.

### Control layers

1. **Identity** — every agent and worker has a stable identity.
2. **Capability** — tools and operations are explicitly allowlisted.
3. **Scope** — targets must be enrolled and authorized.
4. **Isolation** — active validation runs in isolated managed workers.
5. **Policy** — deterministic policy gates every high-impact operation.
6. **Telemetry** — every material action emits a trace/evidence event.
7. **Evaluation** — models are tested for unsafe behavior and policy drift.
8. **Human approval** — irreversible or high-impact response requires approval.
9. **Proof** — remediation requires fresh independent evidence.
10. **Learning** — validated outcomes update the baseline and detection rules.

## Research references

- Microsoft MDASH demonstrates multi-model agentic vulnerability discovery and validation at scale.
- Recent Anthropic and OpenAI incidents demonstrate why agent runtime monitoring must detect unexpected external interaction and coordination.
- OWASP guidance emphasizes least privilege, capability allowlists, tool-call validation, tamper-evident logs, delegation controls and human approval for high-impact chains.
- Apple Foundation Models make local/on-device AI a first-class endpoint security surface.

## Safe execution rule

Research agents may propose or validate within an approved contract. They may not obtain credentials, establish persistence, deliver payloads, evade controls, disrupt systems or hack back through the SaaS product.
