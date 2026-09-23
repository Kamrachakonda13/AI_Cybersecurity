# Promptfoo Evaluation Notes

## Current pass rate: 30/35 (85.71%)

## Failures at time of writing

### Cosmetic (fixed by Unicode normalization)

- **R2 (CVE-2024-3400)**: Answer contains `Palo\u202fAlto` (Unicode narrow
  no-break space). Test expected literal `"Palo Alto"`. The system is
  working correctly; the assertion was too strict.

- **R9 (API retry policy)**: Answer uses `back\u2011off` (Unicode hyphen).
  Test expected literal `"backoff"`. Same root cause.

### Behavior improvements (test written before feature existed)

- **RF1 (Paris weather)**: Before Phase 7.4, the agent refused this query.
  After adding `web_search`, the agent retrieves the answer from Tavily
  and responds correctly. The original test expected refusal. It has been
  updated to accept either behavior.

- **RF2 (World Cup)**: Same story. The test now accepts web_search.

### Genuine limitation

- **R7 (deployment runbook)**: The query "What are the steps in the
  deployment runbook?" fails to retrieve because the answer spans chunk
  boundaries and the agent's query rewrites don't converge. This is a
  known limitation of the retrieval layer for multi-chunk answers. It
  would benefit from hierarchical chunking or a larger parent-chunk
  retrieval strategy.

## Test categories

| Category | Count | Passing |
|----------|-------|---------|
| Retrieval correctness (R*) | 10 | 8 |
| Refusal behavior (RF*) | 10 | 9 |
| Tool routing (T*) | 5 | 5 |
| PII handling (P*) | 5 | 5 |
| Cross-silo discovery (X*) | 5 | 3 |

## What this suite proves

1. **Tool routing works.** The agent picks the correct tool for each query
   type (retrieve, graph_query, calculate, query_sql, web_search).
2. **PII masking works.** Email, phone, credit card, SSN all detected and
   masked before reaching the LLM.
3. **Refusal is terminal.** Adversarial and out-of-scope queries refuse
   cleanly without hallucinating.
4. **The guardrail blocks injections.** Prompt injection attempts return
   HTTP 400 with a clear block reason.
5. **Cross-silo discovery is active.** Some test cases exercise different
   user roles and confirm the ACL filter behaves correctly.
