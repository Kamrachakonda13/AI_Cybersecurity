# Phase 7 Results — Operations Console

**Date:** 2026-09-20
**Deliverable:** Server-rendered admin dashboard over the Phase 1–6 retrieval stack
**Pages:** 9 (Overview, Sources, Chunks, Permissions, Users, Duplicates, Pipeline, Metrics, Architecture)
**Auth model:** Session cookie wrapping the same JWT issued for `/ask`
**Stack:** FastAPI · Jinja2 · Tailwind (CDN) · Chart.js · Alpine.js

## Why a console

A retrieval system is only as trustworthy as its observability. Phase 6
made the fabric federated; Phase 7 makes it *inspectable*. Every layer
that the earlier phases added — connectors, ACLs, dedup groups, sync
state, confidence gates, token meter, audit log — now has a page an
operator can open, read, and screenshot.

This is also the answer to "how do you know it works?" A C-level
reviewer does not read code. They open a dashboard and look.

## What was built

### The eight operational pages

| Page | Data source | What it answers |
|------|-------------|-----------------|
| Overview | `_gather_stats()` | How many sources, documents, chunks are indexed? |
| Sources | `src/connectors/*`, sync state | Which connectors are live? When did they last run? |
| Chunks | pgvector + unified doc model | What content is retrievable, by whom, from where? |
| Permissions | ACL model | What can each user see, and why? |
| Users | Phase 6 ACL + tenant model | Who has which clearance, tenant, team? |
| Duplicates | Phase 6 fingerprint + dedup | Where is the same content in two sources? |
| Pipeline | `data/pipeline_runs.jsonl` | When did ingestion run, what changed? |
| Metrics | Audit log + token meter | What has this system been doing? |

### The Metrics page (7.20)

Four summary cards sourced from the audit log:

- Total requests: **104**
- Total tokens: **266,287** (234,270 prompt + 32,017 completion)
- Average latency: **11,955 ms** (max 105,405 ms)
- Estimated cost: **$0.0394**

Two Chart.js visualizations:

- Calls by route — bar chart (`agent`, `blocked`)
- Latency distribution — histogram across latency buckets

Recent-requests table — last 20 audit log entries with timestamps,
users, routes, queries, tokens, and latency per request.

### The Architecture page (7.21)

A single-page, visual summary of the six-phase stack:

- Phase cards with one metric per phase (Hit Rate, cross-silo rate, etc.)
- Request-flow strip: Router → Hybrid retrieval → Rerank → Confidence gate → LLM → Audit
- Component map: pgvector, Neo4j, Groq, MiniLM, MinIO, FastAPI, Docker
- Design trade-offs table: five decisions and their alternatives

No external state. Renders in one request. Designed to be the page a
reviewer lands on and understands the system in 20 seconds.

### Admin auth (7.22)

The dashboard is gated behind a session cookie.

**Design:** The same JWT issued by `/token` for API calls, delivered
to the browser as an `HttpOnly` cookie instead of an `Authorization`
header. One auth module (`src/auth.py`), two delivery mechanisms.

Why a cookie: browsers cannot send `Authorization: Bearer` headers on
plain `<a href>` navigation. The dashboard has to work with hyperlinks,
so the token has to travel in a cookie.

**The gate:**

- `public_router` — `/dashboard/login`, `/dashboard/logout` (ungated)
- `router` — everything else, with `dependencies=[Depends(require_dashboard_user)]`
- The dependency reads the cookie, decodes the JWT via `src/auth.py`,
  and checks `role == "admin"`. On any failure: `307` redirect to login.

**Test matrix:**

| Scenario | Response |
|----------|----------|
| No cookie → `/dashboard` | 307 → `/dashboard/login` |
| No cookie → `/dashboard/metrics` | 307 → `/dashboard/login` |
| No cookie → `/dashboard/architecture` | 307 → `/dashboard/login` |
| Valid cookie → `/dashboard` | 200 |
| Valid cookie → `/dashboard/metrics` | 200 |
| Logout → cookie removed | `Set-Cookie: rag_session=""; Max-Age=0` |
| After logout → `/dashboard/metrics` | 307 → `/dashboard/login` |
| `/health`, `/ask`, `/token` | Unchanged, ungated |

### Logout and the back-button problem

The subtle part of session auth on server-rendered HTML is what happens
when the user presses the browser back button after logging out. The
browser is happy to repaint the previous page from its in-memory
snapshot, even though the server would 307 the real request.

Two defenses, both required:

1. **`Cache-Control: no-store`** on every `/dashboard/*` response.
   Prevents the browser from storing gated HTML in the first place.

2. **`Clear-Site-Data: "cookies"`** on the logout response.
   Forces the browser to purge the session cookie immediately.
   (We chose `"cookies"` over `"cache"` — the latter walks the
   entire HTTP cache and makes logout take seconds. With `no-store`
   in place, purging the HTTP cache is redundant.)

3. **A `pageshow` bfcache guard** in `base.html`. If a page is
   restored from the browser's back-forward cache, the guard forces
   a real reload. The server 307s; the browser lands on login.

Verified: after logout, back/forward/reload all land on the login page.

## Two bugs found and fixed during the build

### Infinite chart growth

Chart.js with `responsive: true` and no fixed-height parent will
resize the canvas to fill an ever-growing flex container. The canvas
grows, the container grows, Chart.js observes the resize, and the loop
continues indefinitely. The page grew vertically without bound and
the bars stretched beyond the viewport.

**Fix, three parts:**

1. Add `min-h-0` to the `<main>` flex child and `overflow-hidden` to
   the flex parent — this lets the flex child actually scroll instead
   of pushing its own height up.
2. Wrap each `<canvas>` in a `relative h-56` container — this gives
   Chart.js a fixed height to fit into.
3. Set `maintainAspectRatio: false` in every chart config — this tells
   Chart.js to respect the parent height rather than enforce a ratio.

### Duplicate `options` block from a bad patch

A patcher script injected `options: { ... }` into a Chart.js config
that already had an `options:` key. The result was syntactically valid
JavaScript but semantically wrong — the second `options` shadowed the
first. Fixed by removing the duplicate block; the working version
keeps the original `options` and merges the useful keys.

Lesson documented: patch scripts that inject config should detect
existing keys, not assume absence.

## Known limitations

1. **Env-based credentials.** `DASHBOARD_USERS` is a plaintext
   `user:pass:role:tenant` list. Fine for demo; production needs
   hashed passwords (bcrypt / argon2) and a user store.

2. **No CSRF token on the login form.** `SameSite=Lax` + `HttpOnly`
   mitigates but does not eliminate. A production build would add a
   CSRF token tied to the session.

3. **No rate limiting on login.** An attacker can brute-force. Real
   deployments need a lockout after N failed attempts.

4. **No server-side session revocation.** The cookie carries a JWT
   with a fixed 60-minute expiry. Logout clears the cookie but the
   token itself remains valid until expiry if captured. A production
   build would add a revocation list or short-lived tokens + refresh.

5. **No role granularity beyond `admin`.** The dashboard currently
   requires `role == "admin"`. An operator with `role == "manager"`
   cannot log in. A future phase would allow read-only console access
   at lower clearances.

6. **The Phase 5 corpus still contains duplicate chunks.** Approximately
   2,297 rows with `source_system IS NULL` remain in pgvector. They
   do not affect the dashboard, but they distort the Chunks page counts
   and would need cleanup before any "number of indexed chunks" claim
   is published.

7. **RAGAS integration deferred.** The quality-scoring harness
   (`eval/run_ragas.py`) is written but not executed. Free-tier Groq
   quota was the constraint. Running it would produce a
   faithfulness / answer-relevancy / context-precision scorecard to
   sit alongside the Hit Rate and MRR numbers from Phase 1.

## What Phase 7 demonstrates for the portfolio

- **Observability is a first-class deliverable**, not an afterthought.
  The dashboard exists, is legible, and is protected.
- **Server-rendered HTML + Tailwind + Chart.js is a valid stack** for
  an internal tool when the operator is not a frontend engineer. No
  build step, no bundler, no framework lock-in.
- **Auth for HTML surfaces is different from auth for APIs.** The
  bearer-token flow that works for `/ask` cannot be used for pages.
  The cookie wrapper is the correct pattern, and it reuses the same
  JWT — no duplicate auth code.
- **The back-button problem is real** and it is not solved by
  `Cache-Control: no-store` alone. The combination of no-store +
  Clear-Site-Data + bfcache guard is the minimum viable defense.
- **Charts are easy to get wrong.** The infinite-growth bug is a
  known trap; documenting it here prevents it from being rediscovered
  in every future phase that adds a chart.