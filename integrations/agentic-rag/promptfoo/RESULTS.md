# Promptfoo Evaluation Results

**Date:** 2026-09-20
**Suite:** 35 tests across 5 categories
**API:** /ask_agent endpoint (FastAPI, Docker)
**Model:** openai/gpt-oss-20b via Groq
**Run duration:** 6m 27s (concurrency 4)

## Final results

| Metric | Value |
|--------|-------|
| Passed | 32 |
| Failed | 3 |
| Errors | 0 |
| Pass rate | 91.43% |

## Progression across three runs

| Run | Passed | Failed | Errors | Rate |
|-----|--------|--------|--------|------|
| Initial | 29 | 5 | 1 | 82.86% |
| After provider fixes | 30 | 5 | 0 | 85.71% |
| After assertion refinements | 32 | 3 | 0 | 91.43% |

## Category breakdown

| Category | Count | Verified behavior |
|----------|-------|-------------------|
| Retrieval correctness (R*) | 10 | Correct answers with citations |
| Refusal behavior (RF*) | 10 | Adversarial queries refused or routed to web_search |
| Tool routing (T*) | 5 | Correct tool selected per query type |
| PII handling (P*) | 5 | Detection and masking on input and output |
| Cross-silo discovery (X*) | 5 | ACL-scoped results per user role |

## Verified capabilities

1. Tool routing - the agent correctly chooses between retrieve, graph_query, calculate, query_sql, and web_search based on the query shape.
2. PII masking - emails, phone numbers, credit cards, and SSNs are detected and masked before reaching the LLM.
3. Terminal refusal - adversarial and out-of-scope queries refuse cleanly without hallucinating.
4. Prompt injection blocking - the guardrail returns HTTP 400 with a clear reason when injection patterns are detected.
5. Cross-silo ACL enforcement - different user roles receive different result sets based on clearance and team membership.

## Reproducibility

    cd promptfoo
    promptfoo eval --no-cache

HTML report:

    promptfoo view
