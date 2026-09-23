# Portfolio Narrative — How the Phases Fit Together

**Purpose:** This file explains the *shape* of the project. The roadmap
(`docs/ROADMAP.md`) says *what* to build; this file says *why it matters*
and *how the pieces relate*.

## The one-line summary

A measurable, secured, observable RAG system that reasons over enterprise
content, respects permissions, refuses when uncertain, ingests from 12
sources, and defends itself — plus three security projects that reuse,
protect, or complement it.

## The shape of what exists (Phases 1-7)

Phases 1-7 are one product:

> A measurable, secured, observable RAG system that reasons over
. enterprise content, respects permissions, refuses when uncertain,
. ingests from 12 sources, and gives operators a console.

That is the **AI track**. It's a complete vertical slice:
retrieval → security → relationships → agency → confidence →
ingestion → observability.

## What the remaining phases add (Phases 8-10)

Phases 8, 9, and 10 are NOT more layers on the same RAG stack. They are
three independent security projects that share infrastructure to varying
degrees.

| Phase | What it is | Relationship to Phases 1-7 |
|-------|-----------|------------------------------|
| **8 — SIEM Triage** | A different application of the same AI stack | **Reuses** the RAG engine, agent loop, confidence gate, audit, dashboard. New domain (SOC alerts). |
| **9 — Injection Firewall** | A defensive control for AI systems | **Protects** the stack — the production version of Phase 2's inline guardrail. |
| **10 — Malware GNN** | A pure-ML security project | **Shares nothing** with the RAG stack. Different tech, different domain. |

## The mental model

```
AI TRACK (Phases 1-7)              SECURITY TRACK (Phases 8-10)
├─ 1. Vector RAG                   ├─ 8. SIEM Triage      ← reuses AI stack
├─ 2. Hybrid + RBAC                ├─ 9. Injection Firewall ← protects AI stack
├─ 3. Graph RAG                    └─ 10. Malware GNN     ← independent ML
├─ 4. Agentic RAG
├─ 5. Security RAG
├─ 6. Ingestion Fabric
└─ 7. Operations Console
```

The AI track is one long story. The security track is three separate
stories that reinforce "this person also thinks like a defender."

## Phase 8 — SIEM Triage (the closest connection)

Phase 8 is the only remaining phase that reuses the existing engine
directly. Reuse map:

| Phase 1-7 component | What Phase 8 uses it for |
|----------------------|------------------------------|
| `src/hybrid_retrieve.py` | Retrieve relevant runbooks/playbooks per alert |
| `src/rerank.py` | Rank candidate responses to an alert |
| `src/confidence.py` | Decide "escalate or suppress" via terminal threshold |
| `src/agent.py` | ReAct loop: pull alert → correlate → retrieve → reason → decide |
| `src/audit.py` | Log every triage decision with reasoning |
| `src/metrics.py` | Feed `/metrics` on the Triage dashboard page |
| `src/dashboard/` | Add "Triage" as a 10th page in the console |
| `src/acl.py` | Enforce "analyst sees only their tenant's alerts" |
| `src/guardrail.py` | Reject injection in alert fields (attacker-controlled text) |

Phase 8 is the same codebase wearing a different hat. That is why it is
high-value: it demonstrates that the RAG architecture generalizes.

**Narrative:** *"The same retrieval + confidence + audit engine that
answers enterprise questions also triages SIEM alerts. Same primitives,
different domain."*

## Phase 9 — Injection Firewall (the defender's complement)

Phase 9 is the inverse of the existing guardrail.

**Today (Phase 2):** `src/guardrail.py` does a regex + keyword check
inline in the `/ask` path. Naive, but present.

**Phase 9:** Promote that to a standalone classifier service with:

- A real corpus (200+ injections, 200+ benign)
- A trained model (embedding similarity, or DistilBERT)
- Measurable detection + false-positive rates
- A documented evasion analysis

It protects the same stack it was born from.

**Narrative:** *"The guardrail introduced in Phase 2 was a placeholder.
Phase 9 replaces it with a trained classifier evaluated on a 500-prompt
adversarial corpus, achieving X% detection at Y% false positive rate."*

## Phase 10 — Malware GNN (the independent one)

Phase 10 is where the connection breaks, deliberately.

It is a completely different stack:

-
Not RAG — graph neural networks
-
Not text — binaries
-
Not an LLM — PyTorch Geometric
-
Different data pipeline, different evaluation, different domain

**Why include it?**

Because the portfolio is "AI + Cybersecurity for C-Level Roles." The
committee wants to see:

1. **Breadth:** NLR/RAG — graph ML — security engineering
2. **Depth in security:** CFGs, evasion, family classification
3. **Judgment:** pick the right architecture for the problem
   (GNN for structure, LLM for language)

**Narrative:** *"A GNN-based variant classifier that catches what hash
and signature detection miss. Standalone — shares no code with the RAG
track, by design."

## The full picture

```
                        ┌───────────────────────────────────────┐
                        ‒  AI TRACK (Phases 1-7)             ‒
                        │                                        │
                        ‒  Retrieval → Security → Graph →    ‒
                        │  Agency → confidence → Fabric →    │
                        │  Observability                     │
                        ‒                                        │
                        │  One long story, one codebase      │
                        ├───────────────────────────────────────└
                                         ‒
                          ‌──────────────────────────────────────────────────────────┐
                          │              │              │
                          ▼              ▼              ▼
                    ┌─────────┐   ├─────────┐   ├─────────┐
                    │ Phase 8  ‒   ‒ Phase 9  │   │ Phase 10 │
                    │ SIEM     ‒   ‒ Injection│   │ Malware │
                    │ Triage    ‒   ‒ Firewall │   │ GNN      │
                    │          ‒   ‒          │   │          │
                    │ REUSES   ‒   ‒ PROTECTS │   │ STANDALONE│
                    ‒ the AI   │   │ the AI   │   │ ML project│
                    │ stack    │   │ stack   │   │           │
                    └──────────┘   └──────────┘   └──────────┘
```

## The portfolio narrative in three acts

**Act 1 — "Here's a serious AI system" (Phases 1-7)**

Measurable retrieval, enterprise security, graph reasoning, agency,
refusal, federation, observability. This alone is a strong AO
engineering portfolio.

**Act 2 — "The same engine solves a different problem" (Phase 8)**

SIEM triage. Proof that the architecture generalizes. The strongest
argument for "I built a platform, not a demo."

**Act 3 — "I also think like a defender" (Phases 9, 10)**

Injection firewall (AI security) + malware GNN (classic security ML).
Breadth. Depth. Judgment.

Together: *"This person builds AT systems, secures them, and
understands the security domain they operate in."

## If forced to cut one

Order of value:

1. **Phase 8 (SIEM Triage)** — highest, because it reuses and amplifies
   everything.
2. **Phase 9 (Injection Firewall)** — fast win, obvious enterprise need.
3. **Phase 10 (Malware GNN)** — highest craft, but independent. Only do
   it if you want the ML depth story.

Stopping after Phase 8 still yields: a full AI stack + one strong
cross-domain application. That is already a C-level-worthy portfolio.

## Related documents

- `docs/ROADMAP.md` — what to build, in order, with deliverables
- `eval/results_phaseN.md` — the numbers for each phase
- `README.md` — the public-facing summary
