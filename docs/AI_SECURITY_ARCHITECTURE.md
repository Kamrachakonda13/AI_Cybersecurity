# VEYRA AI Security Architecture

## Why the AI layer needs to evolve

VEYRA already has AI red-team probes and vector-store tenant enforcement.
The next step is to secure the complete AI application lifecycle, not just the
model.

OWASP's current GenAI work now separates traditional LLM risks from agentic
risks. The 2026 GenAI Security Project also introduced an Agent Control
Standard. VEYRA should map these controls into inventory, policy, runtime
telemetry and evidence.

## AI control-plane model

```text
AI System
 ├── Model / provider / version
 ├── Prompt / policy
 ├── Agent identity
 ├── Skills
 ├── MCP servers/tools
 ├── A2A peers
 ├── Memory
 ├── RAG retrievers
 ├── Vector stores
 ├── Data sources
 ├── External APIs
 └── Actions / side effects
```

## Required capabilities

### 1. AI inventory / SBOM

Track model, provider, endpoint, version, owner, environment, data class,
system prompt reference, tools, skills, MCP servers, A2A peers, vector stores,
memory stores and deployment artifact.

### 2. AI observability

Emit OpenTelemetry-compatible traces for:

- user request
- model invocation
- retrieved documents
- tool calls
- MCP requests
- A2A messages
- memory reads/writes
- policy decisions
- approvals
- external side effects
- token/cost metrics

### 3. Agent Control Plane

Each agent gets a capability document:

```text
identity
allowed_tools[]
allowed_data_scopes[]
allowed_network_destinations[]
max_action_risk
approval_required_above
time_budget
token_budget
transaction_budget
tenant
```

The model cannot modify this document.

### 4. Secure RAG

Use:

```text
query
  ↓
tenant / ABAC authorization
  ↓
lexical retrieval + vector retrieval
  ↓
reranking
  ↓
Security Graph enrichment
  ↓
evidence bundle
  ↓
LLM
  ↓
answer + citations + confidence
  ↓
audit
```

Never retrieve first and authorize later.

### 5. Graph RAG

Combine the security graph with document evidence. Example:

> "Show the shortest path from this internet-facing service to customer data
> and cite the vulnerability, identity and architecture evidence."

The graph provides relationships; RAG provides supporting documents.

### 6. Memory security

Track memory writes as security events. Detect:

- poisoned memories
- unexpected instruction persistence
- cross-tenant memory access
- stale high-risk instructions
- memory deletion/tampering

Provide versioning and rollback.

### 7. MCP / A2A security

Treat tools and agent peers as supply-chain dependencies.

Inventory:
- server identity
- tool capabilities
- schemas
- permissions
- trust level
- signing/provenance
- version
- owner

Validate messages and tool arguments at runtime.

### 8. Evaluation

Create regression suites for:

- prompt injection
- data leakage
- tool misuse
- refusal/policy compliance
- hallucination/grounding
- retrieval authorization
- cross-tenant leakage
- unsafe code/tool requests
- agent-to-agent trust
- memory poisoning

Every release gets a security score and diff against the previous model/prompt/
tool version.

## RAG technology recommendation

Do not make the vector database the system of record.

Recommended separation:

- PostgreSQL: identity, policy, assets, incidents, metadata
- OpenSearch: high-volume security events and lexical search
- Qdrant or equivalent: embeddings/vector retrieval
- Neo4j or PostgreSQL graph model: relationship/attack-path analysis
- Object storage: immutable evidence/artifacts
- Redis: queues/cache, not durable evidence

## AI decision boundary

LLMs may:
- summarize
- correlate
- retrieve
- classify with evidence
- propose hypotheses
- recommend remediation
- generate analyst reports

LLMs should not independently:
- grant privileges
- disable controls
- delete evidence
- execute destructive actions
- determine final incident severity without deterministic policy
- bypass tenant boundaries

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
