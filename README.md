# Vector RAG Foundation — Phase 1

A measurable, production-reasoned Vector RAG baseline. This is Phase 1 of a multi-phase enterprise AI portfolio demonstrating retrieval quality, then security, then relationship reasoning, then autonomy.

## Problem

Most "RAG projects" are demos. This project establishes a **measurable retrieval baseline** before adding complexity. The key claim is that RAG quality is determined by retrieval quality, not by the generation model.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Markdown     │────▶│ Chunker          │────▶│ Embedder    │
│ documents    │     │ 400 char / 50 ov │     │ MiniLM-L6   │
└──────────────┘     └──────────────────┘     └──────┬──────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │ pgvector     │
                                              │ HNSW index   │
                                              └──────┬───────┘
                                                     │
                          ┌──────────────────────────┘
                          ▼
                   ┌─────────────┐    ┌──────────────┐    ┌───────────┐
                   │ Retriever   │───▶│ Groq LLM     │───▶│ /ask API  │
                   │ top-k=5     │    │ grounded     │    │ FastAPI   │
                   └─────────────┘    └──────────────┘    └───────────┘
```

## Design Decisions

| Decision | Choice | Alternative considered | Reason |
|----------|--------|------------------------|--------|
| Chunk size | 400 chars, 50 overlap | Sentence-level; document-level | Balances context preservation with embedding focus |
| Embedding model | all-MiniLM-L6-v2 (384-dim, local) | OpenAI text-embedding-3-small | Zero cost, no API dependency for a baseline |
| Vector store | pgvector + HNSW | FAISS | Persistence and SQL filtering; simpler ops |
| LLM | Groq `openai/gpt-oss-20b` | OpenAI GPT-4o-mini | Free tier; fast; adequate for grounded generation |
| Grounding | Explicit refusal prompt | Implicit citation instructions | Forces "I don't know" instead of hallucination |

## Evaluation Results

Benchmark: 12 hand-labeled questions covering all 5 source documents.

| Metric | Value |
|--------|-------|
| Hit Rate @ 1 | **83.33%** |
| Hit Rate @ 3 | **91.67%** |
| Hit Rate @ 5 | **100.00%** |
| MRR | **0.892** |

Full results in [`eval/results.md`](eval/results.md).

## Project Layout

```
vector-rag/
├── data/
│   ├── raw/              # Source Markdown
│   ├── clean/            # Cleaned Markdown
│   └── chunks.json       # Chunked corpus
├── eval/
│   ├── questions.json    # Hand-labeled benchmark
│   ├── run_eval.py       # Evaluation harness
│   └── results.md        # Recorded metrics
├── src/
│   ├── clean.py          # Cleaning script
│   ├── chunk.py          # Chunking script
│   ├── embed.py          # Embedding + insertion
│   ├── retrieve.py       # Vector search
│   ├── generate.py       # Grounded LLM call
│   ├── main.py           # FastAPI endpoint
│   └── schema.sql        # Database schema
├── docker-compose.yml    # pgvector container
├── requirements.txt
└── README.md
```

## How to Run

### 1. Start the database

```bash
docker compose up -d
```

### 2. Apply the schema

```bash
docker exec -i rag_postgres psql -U raguser -d ragdb < src/schema.sql
```

### 3. Prepare the corpus

```bash
python src/clean.py
python src/chunk.py
python src/embed.py
```

### 4. Configure secrets

Create `.env`:

```
DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb
GROQ_API_KEY=gsk_your_key_here
```

Get a free Groq key at https://console.groq.com/keys.

### 5. Run the API

```bash
python -m uvicorn src.main:app --reload --port 8000
```

### 6. Query the API

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many failed login attempts trigger a lockout?"}'
```

### 7. Run the evaluation

```bash
python eval/run_eval.py
```

## Known Limitations

These are documented as requirements for Phase 2:

1. **No keyword search.** Entity-heavy queries (acronyms, proper nouns) rely on semantic similarity alone.
2. **No reranking.** Top-5 results come from cosine similarity ordering only.
3. **No access control.** Any caller sees all chunks regardless of role.
4. **No confidence thresholding.** The LLM attempts an answer even when retrieval is weak.

## Next Phase

**Phase 2 — Hybrid RAG with RBAC** adds:
- BM25 keyword search alongside vector search
- Reciprocal Rank Fusion (RRF) to merge results
- Cross-encoder reranking
- Clearance-level access control enforced at the vector query layer
- JWT authentication and audit logging
- Re-evaluation against the same benchmark to measure improvement


## Phase 2 Results

Phase 2 extended the pipeline with Hybrid retrieval (vector + BM25 via RRF),
cross-encoder reranking, RBAC at the SQL query layer, JWT authentication,
prompt injection guardrail, and audit logging.

| Metric | Phase 1 | Phase 2 | Delta |
|--------|---------|---------|-------|
| Hit Rate @ 1 | 83.33% | 100.00% | +16.67 pp |
| Hit Rate @ 3 | 91.67% | 100.00% | +8.33 pp |
| Hit Rate @ 5 | 100.00% | 100.00% | — |
| MRR | 0.892 | 1.000 | +0.108 |

Full results in [`eval/results_phase2.md`](eval/results_phase2.md).

### RBAC Demonstration

Two users with different clearances query the same sensitive question:

- **Junior user (PUBLIC clearance)** retrieves only PUBLIC chunks; the LLM
  correctly refuses to answer from weakly-relevant context.
- **Csuite user (CONFIDENTIAL clearance)** retrieves CONFIDENTIAL chunks
  and receives the correct answer.

The clearance filter is enforced in the SQL `WHERE` clause of the vector
search, not as a post-retrieval step. Unauthorized content is never loaded
into the application process.

## Phase 3 Results

Phase 3 added Graph RAG: entity extraction via LLM, Neo4j storage, Cypher traversal,
and a query router that dispatches relationship queries to the graph and semantic
queries to Hybrid RAG.

### Architecture
Query
│
▼
┌───────────────┐
│ Router │ entity match + relationship keyword detection
└──┬─────────┬──┘
│ │
graph hybrid
│ │
▼ ▼
Neo4j Phase 2 pipeline
traverse (vector + BM25 + rerank)
│ │
└────┬────┘
▼
Groq LLM


### Graph stats

- **12 nodes** across 4 types: Service, Database, Store, Component, Policy
- **14 relationships**: DEPENDS_ON, USES_POLICY
- Extracted from `sample_006.md` (service architecture document)
- Loaded to Neo4j 5.24 via the Python driver

### Router behavior (validated)

| Query | Route | Reason |
|-------|-------|--------|
| "What does billing-service depend on?" | graph | entity + relationship phrasing |
| "What services connect to auth-service?" | graph | entity + relationship phrasing |
| "Tell me about billing-service" | hybrid | entity but no relationship phrasing |
| "How many failed login attempts trigger a lockout?" | hybrid | no entity match |

### Multi-hop demonstration

Query: *"What does analytics-service transitively depend on?"*

Route: **graph**. The pipeline traverses 2 hops from `analytics-service`:


LLM answer: *"analytics-service transitively depends on: billing-service, auth-service, Ledger Database, and internal Warehouse."*

No single chunk contains this answer. It only exists when the graph is traversed.

### Known limitations (requirements for Phase 4+)

1. **Relationship-only extraction.** The LLM extracts edges only from `sample_006.md`.
   Extending extraction to all documents would create a richer graph.
2. **Noisy graph citations.** 2-hop traversal returns all reachable edges, not just
   the ones on the primary path from the queried entity.
3. **No confidence threshold.** Same issue as Phase 2 — the LLM answers from whatever
   context is provided, even when retrieval is weak.
4. **No agentic tool use.** The system cannot invoke calculators, SQL, or external APIs.



What you've built across four phases
Phase	Architecture	Deliverable
1	Vector RAG	91.67% Hit Rate @ 3
2	Hybrid + RBAC + JWT + guardrail + audit	100% Hit Rate @ 3, enterprise security
3	Graph RAG + router	Multi-hop relationship queries
4	Agentic loop + 5 tools + metering + traces + Docker	5/5 tool routing, observable, containerized
Reply "Proceed with Phase 5" when you're ready for Security RAG with confidence thresholding — the final AI phase. Phase 5 will:

Add a confidence threshold that refuses when the top retrieval score is below a cutoff

Build a corpus from CISA KEV + MITRE ATT&CK

Add an adversarial evaluation set that tests refusal behavior


Last Phase 5

vector-rag/
├── data/
│   ├── security/
│   │   ├── kev.json                 (NEW — CISA KEV raw)
│   │   └── attack.json              (NEW — MITRE ATT&CK raw)
│   ├── chunks.json                  (unchanged — will be replaced by security corpus)
│   └── traces.jsonl                 (continues to accumulate)
├── src/
│   ├── confidence.py                (NEW — threshold logic)
│   ├── agent.py                     (UPDATED — confidence-aware loop)
│   ├── main.py                      (UPDATED — expose confidence in response)
│   └── security_ingest.py           (NEW — build security corpus)
├── eval/
│   ├── security_questions.json      (NEW — 20 legitimate + 10 adversarial)
│   ├── run_eval_security.py         (NEW — Phase 5 evaluator)
│   └── results_phase5.md            (NEW — comparison report)
└── .env                             (UPDATED — confidence threshold setting)

## Phase 4 Results — Agentic RAG with Observability

Phase 4 turned the retrieval stack into a reasoning system: a ReAct loop
with five tools, token metering, per-tool timeouts, and a containerized
observability surface. The agent selects tools against a hand-labeled
set and can compute, parse dates, query SQL, and search — not just
retrieve.

| Metric | Value |
|--------|-------|
| Tool routing accuracy | 5/5 |
| Max reasoning steps | 5 |
| Per-tool timeout | 10s |
| Cumulative requests (dev period) | 104 |
| Cumulative tokens | 266,287 |
| Average latency | 11,955 ms |
| Estimated cost | $0.0394 |

The loop is bounded and observable: every LLM call records tokens,
cost, and latency; the `/metrics` endpoint exposes the totals; Docker
Compose ships the whole stack as four services. The design principle
from the roadmap — *"RAG is a component in a larger decision system"* —
is why the agent has explicit bounds rather than open-ended autonomy.

Full results in [`eval/results_phase4.md`](eval/results_phase4.md).

## Phase 5 Results — Security RAG with Confidence Thresholding

Phase 5 applied the pipeline to a high-stakes domain where a confident wrong answer is worse than no answer. The corpus was swapped to CISA KEV + MITRE ATT&CK, and the agent was made confidence-aware.

### Corpus

| Source | Chunks | Clearance |
|--------|--------|-----------|
| CISA KEV (Known Exploited Vulnerabilities) | 900 | INTERNAL |
| MITRE ATT&CK Enterprise techniques | 697 | CONFIDENTIAL |
| **Total** | **1597** | — |

### Confidence thresholding

The agent now evaluates retrieval confidence before continuing. Two checks must pass:

1. **Score threshold:** top rerank score must exceed `CONFIDENCE_THRESHOLD` (default `0.0`)
2. **Query coverage:** for entity queries (CVE IDs, ATT&CK IDs), the hard tokens must appear verbatim in the retrieved chunks

When either check fails, the agent refuses immediately — the reasoning loop terminates.

### Benchmark results

| Category | Count | Result |
|----------|-------|--------|
| Legitimate queries (real CVEs, real ATT&CK techniques) | 20 | 20/20 answered |
| Adversarial queries (out-of-scope, invented IDs, offensive guidance) | 10 | 10/10 refused |

**Sensitivity: 100%**
**Specificity: 100%**

### Key improvement over Phase 4

On the query "What is the weather in Paris today?":

| Phase | Behavior |
|-------|----------|
| Phase 4 | 5 tool calls, then refusal |
| Phase 5 | 1 tool call, immediate refusal, no hallucination |

The confidence gate is terminal. Refusal stops the loop.

### Deployment

Same Docker Compose stack. Repopulate the corpus from inside the container:

```bash
docker exec -it rag_api python src/security_ingest.py
docker exec -it rag_api python src/chunk.py
docker exec -it rag_api python src/embed.py
## Phase 6 Results — Enterprise Ingestion Fabric

Phase 6 turned the retrieval engine into a full ingestion fabric: 12
connectors, a unified document model, cross-source deduplication,
incremental sync, an admin API, and federated search with full ACL
enforcement.

### The connector inventory

| Connector | Type | Documents |
|-----------|------|-----------|
| local_fs | Real | 7 |
| s3 (MinIO) | Real | 3 |
| ms_graph | Real (Azure OAuth) | 4 |
| google_drive | Fixture | 3 |
| sharepoint | Fixture | 4 |
| m365 | Fixture | 3 |
| powerbi | Fixture | 3 |
| tableau | Fixture | 3 |
| confluence | Fixture | 3 |
| jira | Fixture | 3 |
| slack | Fixture | 3 |
| notion | Fixture | 3 |

### Pipeline

The ingestion pipeline is a single command:

    python -m src.ingest_pipeline

Idempotent: the second run completes in ~0.2 seconds.

### Deduplication

The fingerprinting system identifies content that appears in multiple
sources. Demonstration pair:
- test_corpus/platform/deployment_runbook.md (local_fs, team=platform)
- test_corpus/sharepoint/sre_deployment_runbook.md (sharepoint, team=sre)

Same content, different sources, different owners. The dedup engine
selects the local_fs copy as canonical and attaches the SharePoint copy
as an alternate source. One indexed document. Two sources cited.

### Cross-silo discovery benchmark

| User | Role | Hit rate | Cross-silo rate |
|------|------|----------|-----------------|
| alice | csuite | 100% | 100% |
| bob | manager/platform | 82% | 51% |
| carol | junior/product | 18% | 100% |
| Overall | | 67% | 81% |

The one-stop shop: the csuite user sees 100% cross-silo results.

### Admin API

Six endpoints mounted at /admin/*:

| Endpoint | Purpose |
|----------|---------|
| GET /admin/connectors | List all 12 connectors with status |
| GET /admin/connectors/{name} | Detail for one connector |
| POST /admin/ingest | Trigger a pipeline run |
| GET /admin/sync-state | What's indexed |
| GET /admin/duplicates | Current duplicate groups |
| GET /admin/sources/{name} | Documents from a source with ACLs |

### Federated search

src/federated_search.py provides a single query surface across all
sources, enforcing:
- Clearance hierarchy (PUBLIC to INTERNAL to CONFIDENTIAL to RESTRICTED)
- Tenant isolation
- Owner-team matching
- Share-scope matching (org / team list / explicit ACL grants)
- Soft-delete filtering

Full results in eval/results_phase6.md.

## Phase 7 Results — Operations Console

Phase 7 made the system inspectable. Every layer the earlier phases
added — connectors, ACLs, dedup groups, sync state, confidence gates,
token meter, audit log — now has a page an operator can open, read,
and screenshot. Nine pages: Overview, Sources, Chunks, Permissions,
Users, Duplicates, Pipeline, Metrics, Architecture.

The console is gated behind a session cookie carrying the same JWT
issued for `/ask`. One auth module (`src/auth.py`), two delivery
mechanisms — Bearer for the API, `HttpOnly` cookie for HTML pages.
Logout combines `Cache-Control: no-store`, `Clear-Site-Data: "cookies"`,
and a `pageshow` bfcache guard so the browser back button cannot
repaint a gated page after logout.

| Scenario | Response |
|----------|----------|
| No cookie → `/dashboard` | 307 → `/dashboard/login` |
| No cookie → `/dashboard/metrics` | 307 → `/dashboard/login` |
| Valid cookie → any gated page | 200 |
| Logout → cookie cleared | `Max-Age=0` |
| `/health`, `/ask`, `/token` | Unchanged, ungated |

Two bugs found and fixed during the build: an infinite chart-growth
loop (Chart.js + flexbox, resolved with `min-h-0`, a fixed-height
wrapper, and `maintainAspectRatio: false`), and a duplicate `options`
key injected by a patcher script that assumed absence.

Full results in [`eval/results_phase7.md`](eval/results_phase7.md).

## Phase 8 Results — AI-Powered SIEM Alert Triage

Phase 8 applies the retrieval + confidence + audit engine from Phases 1–7
to a different domain: SOC alert triage. The problem is measurable —
analysts drown in false positives. The goal is to reduce escalations
without missing real threats.

### The pipeline

SIEM feed ──▶ Ingest ──▶ Correlate ──▶ Triage LLM ──▶ Severity floor ──▶ Queue
(typed) (by entity) (ESCALATE/ (hard rules)
SUPPRESS)


- **Ingest** (`src/siem_ingest.py`) — typed `Alert` dataclass, strict validation
- **Correlate** (`src/siem_correlate.py`) — groups alerts sharing an entity within a 10-minute sliding window into "incidents"
- **Triage** (`src/siem_triage.py`) — one LLM call per incident; grounded prompt; deterministic JSON output
- **Severity floor** — CRITICAL never suppresses; HIGH requires ≥0.90 confidence to suppress; MEDIUM ≥0.75

### Results

Benchmark: stratified 30-incident subset of the 122 correlated incidents
(full run is rate-limited by Groq's free tier; subset covers high/critical
singletons, multi-alert clusters, and low/medium singletons).

| Metric | Baseline | Phase 8 |
|--------|----------|---------|
| Recall (TPs escalated) | 100% | **94.4%** |
| False positive reduction | 0% | **58.3%** |
| Escalations removed | 0 | **8 of 30** |
| Precision | 60.0% | **77.3%** |
| False negative rate | 0% | **5.6%** |

One true-positive incident was suppressed (i-0020, size=1, MEDIUM: an
unsigned binary write to system32 with no corroborating high-severity
alerts). The severity floor caught two other near-misses — the LLM
wanted to suppress two MEDIUM alerts at confidence 0.70, below the
0.75 floor, so they were escalated.

### Why correlation matters

Triage runs on **incidents**, not raw alerts. 200 alerts become 122 units
of work. The severity floor ensures that a lone CRITICAL alert is
escalated regardless of LLM confidence — matching how a real SOC treats
high-severity signals.

### Design decisions

| Decision | Choice | Alternative | Reason |
|----------|--------|-------------|--------|
| Unit of triage | Correlated incident | Raw alert | Analysts reason about incidents, not alerts |
| Prompt shape | Top-3 alerts in full, rest summarized | All alerts verbatim | Bounds token cost; keeps headroom for large clusters |
| Grounding | Rule names + raw fields | Full runbook RAG | Runbook corpus is Phase 8.5 follow-on |
| Failure mode | Escalate at 0.0 confidence | Suppress on error | In SOC, a missed TP is worse than a false alarm |
| Severity floor | CRITICAL never suppressed | Confidence-only | The cost of a missed critical is asymmetric |

### Known limitations

1. **Synthetic feed.** The 200-alert corpus is generated, not captured from a real SOC.
2. **Ground truth is generator-authored.** Not human-labeled; inter-annotator variance untested.
3. **Correlation is entity-only.** No temporal chains across >10-minute windows.
4. **No runbook grounding yet.** The prompt sees rule names and raw fields, not remediation playbooks (a natural Phase 8.5 extension).
5. **Throttled to 30 s/call** due to free-tier Groq quota; benchmark uses a stratified 30-incident subset.
6. **Single model.** All triage runs through `openai/gpt-oss-20b`; no fallback.

Full results in [`eval/results_phase8.md`](eval/results_phase8.md).


## Phase 9 Results — LLM Prompt Injection Firewall

Phase 9 replaced Phase 2's 20-line regex guardrail with a two-tier
classifier and a measured benchmark. Tier 1 is a normalized regex pass
(NFKC, zero-width stripping) that catches literal attack signatures.
Tier 2 is a 1-NN embedding comparison (MiniLM-L6-v2) against a
hand-crafted attack corpus — this is what catches paraphrase.

| Classifier | Detection rate | FPR | Precision |
|------------|----------------|-----|-----------|
| Baseline regex only | 61.1% (11/18) | 1.3% | 78.6% |
| + Embedding (1-NN) | 83.3% (15/18) | 0.0% | 100.0% |
| + Targeted corpus expansion | **100.0%** (18/18) | **0.0%** | **100.0%** |

Per-category detection on the final classifier: direct override 4/4,
system prompt extraction 4/4, indirect injection 1/1, role-play 6/6,
encoded 1/1, jailbreak framing 2/2.

Six evasion vectors are documented but not defended: multi-turn
delayed injection, cross-lingual payloads, steganographic encoding
(base64), semantic near-misses below threshold, very long prompts
beyond the model's 512-token window, and adversarial suffix attacks.

The corpus (78 train / 18 test injections, 239 benign) is hand-crafted,
network-independent, and version-controlled in `data/security/`.

Full results in [`eval/results_phase9.md`](eval/results_phase9.md).
