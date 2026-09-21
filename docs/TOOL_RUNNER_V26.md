# Tool Runner — governed tool runs, Marketplace and managed workers (v2.6+)

## Policy

- **Sudo** runs every registered tool (the registered catalog, privileged included) with one
  click from **Tool Runner**. Approval is implicit in the sudo role: the job
  goes stage → approved → queued for the isolated worker in a single call.
  No tickets, no second token, no waiting.
- **Everyone else is read-only by default.** A tool shows View/Plan/Run only
  when explicitly granted; otherwise the console shows the catalog entry plus
  **Ask sudo admin for approval**.
- Grants are **time-boxed**: 2h / 5h / 24h presets or any custom window
  (15 min–30 days). Expiry is enforced server-side
  (`services/auth.get_tool_level`); expired grants read as `none`.
- Every request, approval, denial, run and expiry-relevant event is
  audit-logged, and every approval email is mirrored to the sudo inbox.

## Approval flow (non-sudo)

1. Open a read-only tool → pick level (View/Plan/Request execution) +
   window + business reason → **Ask sudo admin for approval**.
2. Backend creates a `pending` request, emails the pre-configured sudo inbox
   (`VEYRA_ADMIN_EMAIL` + `SMTP_*`; without SMTP it lands in
   **Tool Runner → Approval inbox** and the backend log) and stores an
   `AdminNotification` copy either way.
3. Sudo approves with 2h/5h/24h/custom (or denies) in the Approval inbox or
   **User & Permissions** (per-tool window picker). Approval mints a grant
   with `expires_at`; the requester sees it under My access requests.
4. `execute_request` runs still need sudo approval per job
   (run degrades to staged `pending_approval`); `plan` stages plans.

## Runner forms

`GET /api/admin/ethical-hacking/tools/{id}/form` returns the guided schema
(`services/tool_forms.py`): flagship tools (Nmap, Metasploit, Hydra, SQLMap,
Burp, ZAP, Wireshark, BloodHound, OpenVAS, Garak, YARA, …) get tailored
fields; every other tool falls back to its category schema. Schemas use
**named profiles, never raw shell flags**; `build_contract_fields` folds
values into the job contract and rejects policy violations (e.g. only
`auxiliary/scanner/*` Metasploit modules are stageable from the console).

## Safety boundary (unchanged)

The API never executes tool commands. Runs create signed job contracts
consumed by a separately authenticated isolated worker
(`VEYRA_WORKER_TOKEN`, contract HMAC). Exploit replay, credential attacks,
payload delivery, persistence, C2 and hack-back remain outside the
browser/API by design — see `docs/TOOLING_MATRIX.md`.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
