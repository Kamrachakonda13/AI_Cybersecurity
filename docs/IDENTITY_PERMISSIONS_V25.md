# VEYRA Identity, Sudo & Click-to-Select Permissions (v2.5+)

VEYRA v2.5 adds a web-managed identity layer so operators do not need terminal commands to create users or grant tool access.

## Roles
- **Sudo** — exactly one account. Can create users, change roles, grant/revoke tool permissions, disable users, and manage privileged security-tool access.
- **Security Admin** — security administration without the sole sudo entitlement.
- **Security Operator** — day-to-day governed security operations.
- **Analyst** — investigation, evidence and permitted planning.
- **Viewer** — read-only access.

## Per-tool levels
- **No access** — unavailable to the user.
- **View** — catalog/help/evidence only.
- **Plan** — create a governed plan; approval is still required.
- **Request execution** — submit a governed execution request; this does not bypass approvals or the isolated worker boundary.

High-impact tools remain classified as `privileged_admin` in the tool registry. A user's `execute_request` permission never removes the global privileged-tool governance requirement.

## Passwords
Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes in this POC. Password change requires the current password and a new password of at least 12 characters. Production should use OIDC/SAML, MFA/WebAuthn and enterprise password policy.

## Single-sudo rule
The backend rejects creation or promotion of a second sudo account and prevents disabling the sole sudo account. This rule is enforced server-side, not only by the UI.

## Bootstrap
Set `VEYRA_SUDO_USERNAME` and `VEYRA_SUDO_PASSWORD` for first startup. After the account is created, remove bootstrap credentials from deployment configuration and manage the account through the identity UI.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
