# Phase 9 Scope — LLM Prompt Injection Firewall

**Duration:** ~1 week · **Effort:** 2–3 hrs/day
**Priority:** 🟡 Medium — partly absorbed into Phase 2 guardrail; this formalizes it

## The problem

Phase 2's `src/guardrail.py` is a **regex + keyword blocklist** — 20 lines,
easily bypassed by any competent attacker. It catches the obvious cases
("ignore all previous instructions") and nothing else.

Real prompt injection attacks use:
- Unicode homoglyphs and encoding tricks
- Delayed instructions ("when the user asks about X, do Y")
- Instruction smuggling inside retrieved content (indirect injection)
- Role-play framing ("pretend you are a different assistant")
- Multi-turn setups ("remember this for later")

Phase 9 replaces the regex with a **classifier** and produces a
**measured detection rate** on a public + hand-crafted adversarial corpus.

## MVP scope

### Data
- **Injection corpus:** 200+ examples, sourced from public datasets
  (e.g. `deepset/prompt-injections`, `jackhhao/jailbreak-classification`)
  plus hand-crafted indirect-injection examples
- **Benign corpus:** 200+ normal queries (from the RAG domain and general use)

### Classifier (tiered, benchmarkable)
1. **Baseline** — regex + keyword heuristics (what exists today)
2. **Embedding similarity** — sentence-transformer embedding compared
   against known attack-vector centroids
3. **Optional fine-tune** — DistilBERT head on top of the embedding
   (only if time allows; documented as "explored" if not)

### Service
- FastAPI middleware that inspects request body before forwarding
- On detection: `403` with a reason code; log the attempt
- Configurable threshold; per-route policies (`/ask` vs `/admin`)

### Evaluation
- Held-out split of the corpus
- Report detection rate + false positive rate
- Document **evasion vectors** the classifier does NOT catch

## File plan

src/security/
├── injection_patterns.py # baseline regex + keyword rules
├── injection_classifier.py # embedding + optional fine-tune
├── injection_middleware.py # FastAPI middleware
└── init.py

data/security/
├── injections_train.jsonl
├── injections_test.jsonl
├── benign_test.jsonl
└── README.md # provenance of each corpus

eval/
├── run_eval_injection.py
└── results_phase9.md

docs/
└── PHASE9_SCOPE.md # this file



## Sub-steps

| # | Step | Deliverable |
|---|------|-------------|
| 9.1 | Download + normalize corpora | `data/security/*.jsonl` |
| 9.2 | Baseline regex classifier | `injection_patterns.py` |
| 9.3 | Embedding classifier | `injection_classifier.py` |
| 9.4 | Middleware integration | `injection_middleware.py` |
| 9.5 | Wire into `main.py` | request inspection on `/ask`, `/admin` |
| 9.6 | Eval harness | `run_eval_injection.py` |
| 9.7 | Evasion analysis | documented in `results_phase9.md` |
| 9.8 | Dashboard page | "Security" tab showing recent blocked attempts |
| 9.9 | README section | `## Phase 9 Results — Injection Firewall` |

## Metrics to report

| Metric | Target | Baseline (Phase 2 regex) |
|--------|--------|--------------------------|
| Detection rate (injections) | ≥ 85% | ~40% |
| False positive rate (benign) | ≤ 5% | < 1% |
| Latency added per request | < 20 ms | < 1 ms |
| Evasion vectors documented | ≥ 5 | 0 |
| Classification accuracy | ≥ 90% | ~60% |

## Design decisions to document

| Decision | Choice | Alternative | Reason |
|----------|--------|-------------|--------|
| Classifier type | Embedding similarity + centroid | Fine-tuned BERT | No GPU; embedding approach is 90% as good for this corpus size |
| Integration | FastAPI middleware | Decorator on each route | One place to enforce; new routes are protected by default |
| Failure mode | Fail-open, log + metric | Fail-closed, 500 | Availability > paranoia for internal tooling; documented |
| Location | Separate service OR in-process | Always in-process | In-process is 20× faster; a standalone service is a Phase 9.5 follow-on |
| Corpus | Public + hand-crafted | Public only | Public corpora miss indirect injection through retrieved chunks |

## Known limitations (to be documented in results)

1. Classifier trained on public corpus — novel attacks will evade
2. False positives on legitimate security research queries
3. Regex baseline is trivially bypassable with encoding (documented, not defended)
4. No defense against **output-side** injection (data exfiltration via the LLM response)
5. Indirect injection — attacks inside retrieved documents — is only partially covered
6. No multi-turn context tracking; injection is evaluated turn-by-turn

## Ethical notes

- Public corpora are used under their respective licenses (attribution in `data/security/README.md`)
- No live attack payloads; the corpus is text prompts only
- Evasion examples are documented for defense, not distribution

## Deliverable line for resume

> *"Built prompt injection detection firewall; reduced successful injection attempts by 85% across a 500-prompt test suite while keeping false positives under 5%; documented evasion vectors and residual risk."*

## What Phase 9 adds to the portfolio

- **Defense in depth for AI.** The RAG system now defends itself against
  the #1 AI security vulnerability.
- **Measured, not hand-waved.** Detection rate and FPR are reported, not
  asserted.
- **Evasion awareness.** Documenting what *doesn't* work is as important
  as what does.

  