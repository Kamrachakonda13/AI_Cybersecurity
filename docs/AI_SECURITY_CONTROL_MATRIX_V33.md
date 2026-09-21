# VEYRA v3.3 — AI Security Control Matrix

| Area | VEYRA control | Evidence |
|---|---|---|
| Agent identity | Unique agent identity and owner | identity record, session trace |
| Excessive agency | Capability allowlist and approval for high-impact actions | policy decision, approval |
| Prompt injection | Input/context evaluation and policy decision | prompt trace, evaluation result |
| Memory/context poisoning | Provenance and trust classification for memory/context | source lineage, retrieval trace |
| Tool/MCP security | Tool registry, schema validation and allowlist | tool invocation trace |
| A2A trust | Agent identity, destination policy and trace correlation | A2A trace |
| RAG security | Retrieval provenance, source trust and output validation | retrieval evidence |
| Model supply chain | SBOM/AIBOM, artifact hashes and provenance | manifest, signature/hash |
| Runtime observability | Structured AI traces and policy events | trace ID, event log |
| Incident response | AI-specific timeline and containment workflow | incident bundle |
| Governance | Mapping to organizational policy and AI risk controls | control assessment |

This matrix is a defensive architecture reference. Specific vendor/tool mappings should be refreshed as the ecosystem changes.
