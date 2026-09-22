# 📋 VEYRA P2 Roadmap + Frontend Audit — Final Handoff Document

**Save this as `NEXT_STEPS.md` in your project root.** Copy from here, paste into a file, commit.

---

# VEYRA v5.0 — P2 Roadmap & Session Handoff

**Project:** VEYRA v5.0 Autonomous Security Control Plane
**Repo:** `/Users/kam/Claude projects/VEYRA_v5_0_Autonomous_Security_Control_Plane`
**Status:** P0 ✅ closed • P1 ✅ closed • **P2 not started**
**Branch:** `main` (clean working tree)
**HEAD:** `969bc3b`
**Tests:** 104/104 passing
**Docs:** 587/587 complete, 0 orphans
**Session date:** Sep 21, 2026

---

## 📚 Context for the Next Chat

### What happened in the last session

**P0 — Foundational safety** (commits `b17e0de` → `a0dde6d`)
- Initialized git (wasn't a repo)
- Rebranded `AegisX` → `VEYRA` across 62+ files
- Renamed env vars `AEGISX_*` → `VEYRA_*` across 15 files + frontend sessionStorage
- Fixed test isolation bug in `test_discovery.py`
- Removed 3 orphan docs + 1 registry duplicate
- Fixed validator's wrong brand check
- Added `slugify()` module, renamed 5 malformed doc IDs
- Made v42 verifier fail-closed (was a security bug)
- Added 3 regression tests for v42
- Fixed CI action versions (`@v6` → `@v5`, `@v5` → `@v4`)
- Added gitleaks secret-scanning workflow

**P1 — Contract integrity & governance** (commits `9b26847` → `969bc3b`)
- Implemented v5.0 verifier (was a stub) with full contract + 7 tests
- Deprecated v4.1/v4.2 workers with `DeprecationWarning`
- Moved `ligolo-mp`, `ligolo-ng`, `ligolo-ng-common-binaries` to `isolated_lab_only`
- Reworded security boundary to tiered "Governed security operations" across 3 source strings + 576 docs
- Fixed duplicate `Subfinder` in base registry; split into `subfinder` (Kali wrapper) and `subfinder-feature` (passive discovery)

### Known deferred items from P0/P1

- `DEPRECATION.md` (repo root) — drafted, not created
- `backend/tests/test_v4x_deprecated.py` — deliberately skipped
- Historical snapshot notes on `TOOL_*_V27/V31/V32/V35/V36.md`
- One-shot migration scripts left in `scripts/` — decide whether to archive
- **Full frontend↔backend contract audit** — new, detailed below

---

# 🎯 P2 Work Queue

## 🔴 P2-0 — Frontend ↔ Backend Contract Audit (NEW — do this FIRST)

**Why first:** We made substantive backend changes in P0/P1 without verifying the frontend. Every change below could have broken UI behavior silently.

### The specific backend changes to check

| # | Backend change | Frontend risk |
|---|---|---|
| 1 | Env var rename `AEGISX_*` → `VEYRA_*` in code + `docker-compose.yml` + `.env.example` | Frontend reads `sessionStorage.getItem('veyra_user_token')` — already renamed during P0. Verify all reads/writes use the new key. |
| 2 | `/v1/policy/decide` endpoint in `examples/local_agent_gateway.py` | Not frontend-facing — check only if the UI has an agent chat panel |
| 3 | v5.0 verifier contract (`contract_version: "5.0"`, `checks: {...}`, `overall_status`) | If the UI displays verification receipts, it must parse the new schema. v4.2's top-level `verification` object is gone. |
| 4 | v4.1/v4.2 deprecation warnings | Not visible to frontend unless the UI triggers worker CLI runs and captures stderr |
| 5 | Security boundary reword (576 docs + 3 source strings) | If the UI displays `help_boundary` text anywhere, verify it renders the new tiered text |
| 6 | Ligolo → `isolated_lab_only` | If the UI groups tools by `execution_profile`, verify `isolated_lab_only` is a recognized value |
| 7 | `subfinder` registry split (`subfinder` + `subfinder-feature`) | If the UI caches a tool list, both should now appear. Verify no tool picker hardcodes `subfinder` to one meaning. |
| 8 | `slugify()` refactor — some tool IDs may have changed | UI that links to `/tools/<id>` must use the new IDs. Any malformed historical IDs may now 404. |
| 9 | Registry count: 588 → 587 | If the UI displays a tool count badge, verify it reads from API, not a hardcoded constant |

### Audit procedure

**Step 1 — Map frontend ↔ backend API surface**

```bash
grep -rn 'fetch(\|axios\|api\.' frontend/src/ --include='*.jsx' --include='*.js' --include='*.ts' --include='*.tsx' | head -40
```

Build a list of every backend endpoint the frontend calls.

**Step 2 — Verify each endpoint response shape**

For each endpoint found:
- Find the backend route (`backend/app/api/routes.py` and sub-routers)
- Find the response Pydantic model or dict shape
- Compare with what the frontend code destructures

**Step 3 — Search for stale references**

```bash
grep -rn 'aegisx\|AEGISX\|AegisX' frontend/src/ 2>/dev/null
grep -rn 'subfinder-2' frontend/src/ 2>/dev/null
grep -rn 'isolated_worker' frontend/src/ 2>/dev/null
grep -rn 'verification_required' frontend/src/ 2>/dev/null
grep -rn 'contract_version.*4\.[12]' frontend/src/ 2>/dev/null
```

Any hit → investigate.

**Step 4 — Check sessionStorage keys**

```bash
grep -rn 'sessionStorage\|localStorage' frontend/src/ --include='*.jsx' | head -30
```

Every `aegisx_*` should be `veyra_*` (verified during P0 but re-verify).

**Step 5 — Verify tool picker / catalog UI**

If the frontend lists tools:
- Confirm it reads from the live registry (API), not a static array
- Confirm `subfinder-feature` appears (new tool)
- Confirm deprecated/isolated tools render the correct badge

**Step 6 — Verify verification receipt rendering**

If the frontend displays worker output:
- Find where receipts are parsed
- Check it handles `contract_version: "5.0"` with `checks: {...}` and `overall_status`
- Check it handles v4.x receipts gracefully (or explicitly drops them)

**Step 7 — Verify security-boundary display**

If the UI shows `help_boundary`:
- Confirm the 3-source-string change flows through
- Confirm the new multi-sentence tiered text renders (may need CSS adjustment)

**Step 8 — Smoke test**

```bash
cd frontend && npm run build
```

Watch for:
- Build errors (missing exports, broken imports)
- Warnings about unused variables

**Step 9 — Manual smoke test**

If the frontend runs against the backend:
```bash
cd frontend && npm run dev
```
- Login flow (sessionStorage key)
- Tool catalog page (587 tools, both subfinders)
- Tool detail page for a specific tool (help_boundary text)
- Any worker/verification display panel

**Step 10 — Document findings**

For each issue found, open a fix. Small ones go in as P2-0-fix-N commits alongside the audit.

### Deliverable

- `docs/FRONTEND_BACKEND_CONTRACT_AUDIT.md` — a table of every endpoint, its backend shape, and whether the frontend matches
- Any fixes as code changes + commits
- A checklist file `docs/FRONTEND_VERIFICATION.md` for future regression checks

**Effort:** 45-90 min (depends on frontend surface area)
**Risk:** Medium — depends on how much UI exists
**Priority:** 🔴 **DO FIRST** — every other P2 item builds on top of a verified frontend

---

## 🔴 P2-1 — Restore the docs generator (HIGH VALUE)

**Problem:** 587 tool docs under `docs/tools/` are **manually maintained** with no generator in the repo. Every catalog change requires a manual doc sweep (we proved this 3 times last session).

**What to build:**

Create `scripts/generate_tool_docs.py` that:
- Imports the three registries (`extended_registry()`, `ai_cutting_edge_2026.registry()`, `ai_ecosystem.registry()`)
- For each tool, renders markdown using the current template structure
- Writes to `docs/tools/<slug>.md` using `app.services.slug.slugify()`
- Has `--check` mode: exit 1 if any doc would change (for CI drift detection)
- Also generates `docs/tools/README.md` — a category-grouped index

**Sections required (must match existing):**
`## What is it?`, `## Why VEYRA includes it`, `## When should the team use it?`, `## VEYRA UI workflow`, `## Terminal starting point`, `## Safe workflow`, `## Evidence to collect`, `## How to interpret results`, `## Remediation and verification`, `## Common mistakes`, `## Team teaching summary`, `## Security boundary`

**Then add to `.github/workflows/ci.yml`:**

```yaml
  docs-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install -r backend/requirements.txt
      - run: PYTHONPATH=backend python scripts/generate_tool_docs.py --check
```

**Approach:**
1. Generate to `docs/tools/_generated/` first
2. `diff -r docs/tools docs/tools/_generated` — iterate on template until minimal diff
3. Once output matches, switch to in-place regeneration
4. Commit the generator + regenerated docs

**Effort:** 30-45 min
**Risk:** Medium — template must exactly match or the diff is huge

---

## 🟠 P2-2 — Validator cross-checks doc values against catalog

**Problem:** `scripts/validate_tool_documentation.py` only checks that section headings exist. It doesn't verify that **values** match (e.g., `**Execution boundary:** isolated_lab_only` should match the catalog).

**What to build:** Extend the validator to parse and compare:
- `**Category:**` ↔ catalog `category`
- `**Purpose:**` ↔ catalog `purpose`
- `**VEYRA access:**` ↔ catalog `access_tier`
- `**Execution boundary:**` ↔ catalog `execution_profile`

Report mismatches as errors.

**Effort:** ~30 min
**Risk:** Low
**Note:** Do **after** P2-1 — the generator makes this trivially green.

---

## 🟠 P2-3 — JSON schema validation for v5.0 contract

**Problem:** `worker/v50/veyra_trust_verifier.py` implements a contract described in `CONTRACT.md`, but there's no machine-readable schema or CI check.

**What to build:**
- `worker/v50/schema/request.schema.json`
- `worker/v50/schema/response.schema.json`
- Add `jsonschema` to `backend/requirements.txt`
- Test in `backend/tests/test_v50_worker.py`: every response validates against the schema
- `CONTRACT.md` references the schemas as authoritative

**Effort:** ~30 min
**Risk:** Low

---

## 🟡 P2-4 — Historical-snapshot notes in dated catalogs

**Files:**
- `docs/TOOL_HELP_CATALOG_V27.md`
- `docs/TOOL_USAGE_CATALOG_V31.md`
- `docs/TOOL_HELP_INDEX_V32.md`
- `docs/TOOL_HELP_INDEX_V35.md`
- `docs/TOOL_HELP_INDEX_V36.md`

**Fix:** Add note at top of each:
```markdown
> **Note:** This is a historical snapshot from VEYRA vX.Y. For current tool documentation, see [`docs/tools/`](tools/).
```

**Effort:** ~15 min
**Risk:** Zero

---

## 🟡 P2-5 — `docs/tools/README.md` index

Folded into **P2-1** — the generator produces the index.

---

## 🟡 P2-6 — `DEPRECATION.md`

Deferred from P1-1. Content:
- Policy statement (deprecated for ≥1 major version, warn on import, remove in next major)
- v4.1 entry — why deprecated (fail-open hardcoded checks), migration example
- v4.2 entry — why deprecated (single-verifier only), migration example
- Timeline table (deprecated in 5.0, removed in 6.0)
- What does *not* get deprecated (v5.0, backend services)

**Effort:** ~10 min
**Risk:** Zero

Refer to the P2-7 in the bottom

## 🎯 Recommended Order

### Session 1 (next chat) — Highest impact
1. **P2-0** — Frontend ↔ Backend Contract Audit (must be first)
2. **P2-1** — Docs generator + CI drift check
3. **P2-2** — Validator value cross-check
4. **P2-5** — README index (folded into P2-1)

### Session 2 — Formalization
5. **P2-3** — JSON schema for v5.0 contract
6. **P2-4** — Historical notes
7. **P2-6** — `DEPRECATION.md`

### Optional
8. ~~**P2-7** — Deprecation tests~~ (not planned; see P2-7 section below)

---

# 🖥️ Frontend Audit — Detailed Plan

## Endpoints the frontend likely calls

From the earlier `frontend/src/main.jsx` inspection:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/login` | POST | Returns `{ token, user }` |
| `/api/auth/me` | GET | Returns user object |
| `/api/auth/password` | POST | Change password |
| `/api/ingest/discovery` | POST | Discovery ingest |
| `/api/discovery/hosts` | GET | Host list |
| `/api/discovery/summary` | GET | Aggregate stats |
| `/api/fabric/overview` | GET | Fabric dashboard |
| `/api/fabric/ai-attack-paths` | GET | AI attack path view |
| `/api/fabric/events?limit=N` | GET | Event feed |
| `/api/admin/ethical-hacking/jobs` | GET | Admin jobs |
| `/api/admin/ethical-hacking/tools` | GET | Admin tool list |
| `/api/ai-ecosystem/overview` | GET | AI ecosystem summary |
| `/api/ai-ecosystem/tools` | GET | AI tool list |
| `/api/workers` | GET | Worker list |
| `/api/workers/<id>/tools` | GET | Per-worker tool list |
| `/api/v35/lifecycle/overview` | GET | Lifecycle view |
| `/api/v35/lifecycle/plan?focus=X` | GET | Lifecycle plan |
| `/api/autonomous-soc/investigate` | POST | SOC case creation |

**For each endpoint, verify:**
1. Backend response shape matches what frontend destructures
2. Auth header name matches (`X-VEYRA-Admin-Token`, `X-VEYRA-Privileged-Admin-Token`)
3. Any enums (tool categories, boundaries, statuses) used by the UI match backend values

## Files to inspect

```bash
find frontend/src -name '*.jsx' -o -name '*.tsx' -o -name '*.js' | sort
```

Key ones (based on earlier snapshot):
- `frontend/src/main.jsx` — main app shell, auth flow
- `frontend/src/v3.jsx`, `v29.jsx`, `v31.jsx`, `v32.jsx`, `v33.jsx`, `v34.jsx`, `v35.jsx`, `v36.jsx`, `v37.jsx`, `v38.jsx`, `v39.jsx`, `v40.jsx`, `v42.jsx`, `v50.jsx`, `v50_ai_apps.jsx` — version-specific views

## Search patterns for the audit

```bash
# Stale branding
grep -rn 'aegisx\|AegisX\|AEGISX' frontend/src/ 2>/dev/null

# Stale storage keys
grep -rn "sessionStorage\|localStorage" frontend/src/ --include='*.jsx' | grep -i aegisx

# Stale tool IDs
grep -rn 'subfinder-2' frontend/src/ 2>/dev/null

# Stale boundary values
grep -rn 'isolated_worker\b' frontend/src/ 2>/dev/null

# Stale contract versions
grep -rn 'contract_version\|receipt_version' frontend/src/ 2>/dev/null

# Stale header names
grep -rn 'X-AEGISX\|X-VEYRA' frontend/src/ 2>/dev/null

# Tool count hardcodes
grep -rn '58[0-9]' frontend/src/ --include='*.jsx' | grep -i tool
```

## Deliverable: `docs/FRONTEND_BACKEND_CONTRACT_AUDIT.md`

Structure:
```markdown
# Frontend ↔ Backend Contract Audit

**Audit date:** <date>
**Backend HEAD:** <commit>
**Auditor:** <name>

## Endpoint matrix

| Endpoint | Method | Backend shape | Frontend usage | Status |
|---|---|---|---|---|
| /api/auth/login | POST | `{token, user}` | `main.jsx:165` destructures `{token, user}` | ✅ |
| /api/fabric/events | GET | `[{id, type, ts, ...}]` | `main.jsx:130` reads `.id`, `.type` | ✅ |
| ... | ... | ... | ... | ... |

## Findings

### F-1 — <title>
- **Backend:** <what it returns>
- **Frontend:** <what it expects>
- **Impact:** <what breaks>
- **Fix:** <what to change>

## SessionStorage / LocalStorage keys

| Key | Old | New | Verified |
|---|---|---|---|
| user token | `aegisx_user_token` | `veyra_user_token` | ✅ |
| admin token | `aegisx_admin_token` | `veyra_admin_token` | ✅ |
| privileged admin token | `aegisx_privileged_admin_token` | `veyra_privileged_admin_token` | ✅ |

## Verdict

- X endpoints verified
- Y findings (Z critical, W minor)
- Follow-up commits: <list>
```

---

# 🧠 Environment Notes for the Next Chat

**Terminal quirks we hit repeatedly:**

1. **`code <file>` opens VS Code, but you must `Cmd+S` to write to disk.** Every "file doesn't exist" issue was because paste happened but save didn't. **Always verify with `ls -la <file>` or `wc -c <file>` after creating.**

2. **Never paste multi-line Python into zsh.** The shell mangles `!`, `$(...)`, `{...}`, `#` comments. Always `code` a file, paste, save.

3. **`cd backend && ... && cd ..` — remember the second `cd`.** Multiple times we ended up in `backend/` and subsequent commands using `backend/...` paths failed.

4. **Git commit pattern:** Commits often succeed silently. Re-running `git add && git commit` says "nothing to commit, working tree clean" — that's the **signal** the commit worked. Verify with `git log --oneline -3`.

5. **`\b` word boundaries hide matches.** `\bAEGISX\b` doesn't match `AEGISX_TOKEN`. That's why env-var rebranding needed a separate script.

6. **The validator's slug function is stricter than the catalog's.** Fixed by adding `slugify()` in P0.

7. **`zsh` treats `#` at line start as a command.** Use `setopt interactivecomments` in `.zshrc` or avoid comments in pasted blocks.

---

# 🎯 How to Restart the Chat

Paste this into the next chat:

```
Continuing work on VEYRA v5.0 Autonomous Security Control Plane.

Repo: /Users/kam/Claude projects/VEYRA_v5_0_Autonomous_Security_Control_Plane
Status: P0 ✅ and P1 ✅ closed. HEAD=969bc3b. 104/104 tests passing. 587/587 docs complete.
Next: P2 roadmap (see NEXT_STEPS.md in repo root).

Attached: NEXT_STEPS.md (the handoff document)

Please run `git log --oneline | head -15` and `git status`, then let's start with P2-0 (frontend ↔ backend contract audit).
```

Also paste:
- Output of `git log --oneline | head -15`
- Output of `git status`
- Output of `ls frontend/src/` (so the next chat knows the UI structure)

---

# 📌 Quick Reference — Key Files

| Path | Purpose |
|---|---|
| `backend/app/services/extended_catalog.py` | Tool registry + help builder |
| `backend/app/services/admin_tools.py` | Base `TOOL_REGISTRY` |
| `backend/app/services/ai_cutting_edge_2026.py` | Cutting-edge AI tool registry |
| `backend/app/services/ai_ecosystem.py` | AI ecosystem connectors |
| `backend/app/services/slug.py` | Canonical `slugify()` |
| `backend/app/services/sudo_arsenal.py` | Sudo/privileged tool views |
| `backend/app/api/routes.py` | Main API routes |
| `backend/app/main.py` | FastAPI app |
| `worker/v50/veyra_trust_verifier.py` | Current worker |
| `worker/v50/CONTRACT.md` | v5.0 spec |
| `frontend/src/main.jsx` | Main UI shell |
| `frontend/src/v*.jsx` | Versioned views |
| `scripts/validate_tool_documentation.py` | Doc validator (heading-only) |
| `docs/tools/*.md` | 587 tool docs |
| `.github/workflows/*.yml` | CI |

---

# 🎯 Success Criteria for P2

- ✅ Frontend verified against all backend changes (P2-0)
- ✅ `scripts/generate_tool_docs.py --check` passes in CI
- ✅ Validator catches catalog↔doc value drift
- ✅ v5.0 contract has machine-readable JSON schemas
- ✅ `docs/tools/README.md` index exists and is current
- ✅ All historical catalogs marked
- ✅ `DEPRECATION.md` exists
- ✅ `docs/FRONTEND_BACKEND_CONTRACT_AUDIT.md` exists
- ✅ Total commits: ~18-20 (5-7 more than current)

---

# 📌 Open Questions / Decisions Deferred

- **Should one-off migration scripts** (`rename_env_vars.py`, `rebrand_aegisx_to_veyra.py`, `update_security_boundary.py`) be kept, moved to `scripts/migrations/`, or archived?
- **Should historical catalogs** (`TOOL_*_V27/V31/V32/V35/V36.md`) be moved to `docs/history/`?
- **JSON schema location** — `worker/v50/schema/` or top-level `schemas/`? (Recommend worker-local.)
- **Should `docs/tools/` be split** into `manual/` and `generated/`? (Recommend no — keep flat.)
- **Frontend build pipeline** — is `npm run build` currently passing on `main`?

---

# 📌 To Save This Document

```bash
code NEXT_STEPS.md
```

Paste this entire message content. **`Cmd+S`.**

Verify:
```bash
wc -l NEXT_STEPS.md
```

Should show **~400 lines**.

Commit:
```bash
git add NEXT_STEPS.md
git commit -m "docs: add P2 roadmap, frontend audit plan, and session handoff notes"
git log --oneline -3
```

---

**End of handoff document.**

**Summary of what this covers:**
- Full P0/P1 recap for context
- **P2-0 frontend audit** as the first task (with detailed 10-step procedure, endpoint matrix, search patterns, and deliverable format)
- P2-1 through P2-6 with effort/risk (P2-7 not planned)
- Environment quirks learned last session
- Restart instructions for the next chat
- Quick-reference file map
- Open questions to resolve

**Save it, commit it, and the next chat can pick up exactly where we left off.**

### ⚫ P2-7 — Deprecation tests (NOT PLANNED)

**Status:** Not planned. Deprecated code doesn't need test coverage.

**Rationale:**
- We manually verified (via `python -W always::DeprecationWarning worker/v41/... --help`) that the warnings fire correctly.
- The warning is **informational**, not a contract — no downstream code depends on it firing.
- Testing deprecated code creates a maintenance obligation: when v6.0 removes v4.x, the tests must be removed too.
- Adding tests to deprecated code **encourages** keeping it around longer. We want the opposite.

If the deprecation warning ever becomes a strict contract, revisit this decision.

---

## ✅ P2 Session Recap (2026-09-22)

**P2 was completed in a single working session.** All items except P2-7 (not planned) were delivered.

| Item | Commit(s) | Summary |
|---|---|---|
| **P2-0** Frontend audit | `8730a57`, `23cec73` | Found and fixed extra `))` in `main.jsx` nav array (blocking build). Synced `package-lock.json` to 5.0.0. Frontend build now passes: 1863 modules, 431 kB. |
| **P2-1** Docs generator | `d153edc`, `1e98819` | Wrote `scripts/generate_tool_docs.py`. Regenerated 297 stale docs. Added `docs-drift` CI job. |
| **P2-2** Validator cross-check | `86d35a6` | Validator now compares 4 header fields (Category, Purpose, VEYRA access, Execution boundary) against the catalog. 0 drift across 587 tools. |
| **P2-3** v5.0 JSON schema | `9b1f775` | Created `worker/v50/schema/{request,response}.schema.json`. Added 6 tests. Schema validation caught a real bug (missing `worker_id`/`release_id` in error responses). |
| **P2-4** Historical notes | `eb80cc5` | Marked 5 dated catalog files as historical. Wrote idempotent `scripts/add_historical_notes.py`. |
| **P2-5** docs/tools/README.md index | `c1d9d14` | Generator now emits a 777-line browsable index (587 tools, 61 categories). |
| **P2-6** DEPRECATION.md | `beb74d5` | 118-line migration guide for v4.1/v4.2 workers. |
| **P2-7** Deprecation tests | — | Not planned (see rationale in P2-7 section). |

**Session outcome:**
- Tests: 104 → **110** (6 new schema validation tests)
- Commits: 18 → **28**
- CI: all 4 jobs green (backend, docs, docs-drift, frontend)
- Tool docs: 587 generated + verified, 0 drift
- Frontend: build green

**Next phase:** P3 (not yet scoped). Candidates:
- Restore `docs/FRONTEND_BACKEND_CONTRACT_AUDIT.md` as a permanent artifact.
- Investigate the untested `v50_trust_control_plane.py` service.
- Review `backend/app/services/` for other untested modules.
- Evaluate frontend test coverage.