# VEYRA v3.4 — Security Intelligence & Continuous Validation

## Purpose
v3.4 turns VEYRA inventory, telemetry, documentation and control metadata into a repeatable defensive validation program.

## UI
Open **Continuous Validation** from the left navigation. Review priority signals, then review the validation plan and evidence requirements. Execution is not performed directly by this page.

## Validation lifecycle
1. Define authorised scope.
2. Select a control test.
3. Confirm Sudo/role entitlement.
4. Obtain approval when required.
5. Dispatch a signed job to an isolated managed worker.
6. Collect normalized evidence and hashes.
7. Review results and remediate.
8. Re-run the validation and record recovery/closure evidence.

## Control domains
Identity, scope, worker integrity, evidence/provenance, AI runtime, AI data, software/model supply chain, detection/response, resilience and documentation.

## AI-specific validation
The AI control set should continuously check agent identity, tool allowlists, high-impact actions, prompt/context integrity, RAG provenance, memory boundaries, MCP/A2A interactions, model/artifact provenance and traceability.

## Terminal
The control plane itself is queried through the API. Tool-specific terminal commands remain in `docs/tools/*.md` and are executed only on an enrolled, authorised worker. Start with the tool's `--help`/version or health command, then use the VEYRA-approved command profile for the explicitly authorised scope.

## Safety boundary
Continuous validation is not unrestricted exploitation. VEYRA must not use this subsystem for retaliation, hack-back, persistence, destructive actions or arbitrary remote shell execution.
