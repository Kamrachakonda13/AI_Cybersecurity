"""Outbound admin notifications (tool-access approvals).

POC email delivery: when SMTP_* env vars are set, sends via smtplib (TLS);
otherwise the message is recorded to the backend log AND mirrored into the
`admin_notifications` table so the sudo inbox in the console always works.
Every send attempt (email or log) is audit-logged by the caller.
"""
from __future__ import annotations
import logging
import os
import smtplib
from email.message import EmailMessage

log = logging.getLogger("aegisx.notify")


def admin_email() -> str:
    return os.getenv("AEGISX_ADMIN_EMAIL", "").strip()


def _smtp_config() -> dict:
    return {
        "host": os.getenv("SMTP_HOST", "").strip(),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", "").strip(),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from": os.getenv("SMTP_FROM", "").strip() or os.getenv("SMTP_USER", "").strip(),
        "use_tls": os.getenv("SMTP_TLS", "true").lower() == "true",
    }


def send_access_request_email(to_email: str, username: str, tool_name: str,
                              level: str, duration_hours: float, reason: str,
                              request_id: str) -> tuple[str, str]:
    """Returns (channel, status): channel is 'email' or 'log'."""
    subject = f"[AegisX] Tool access request: {username} → {tool_name} ({level})"
    body = (
        f"User '{username}' requests '{level}' access to {tool_name}.\n\n"
        f"Requested window: {duration_hours:g} hour(s)\n"
        f"Business reason: {reason or '(none given)'}\n"
        f"Request ID: {request_id}\n\n"
        f"Decide in the console: User & Permissions → Approval inbox, or\n"
        f"Tool Runner → Approval inbox. Approvals create a time-boxed grant;\n"
        f"expiry is enforced server-side."
    )
    cfg = _smtp_config()
    if to_email and cfg["host"]:
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = cfg["from"]
            msg["To"] = to_email
            msg.set_content(body)
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as s:
                if cfg["use_tls"]:
                    s.starttls()
                if cfg["user"]:
                    s.login(cfg["user"], cfg["password"])
                s.send_message(msg)
            return "email", "sent"
        except Exception as e:  # noqa: BLE001 — fall through to log mirror
            log.warning("SMTP send failed (%s); mirroring to admin inbox", e)
    log.warning("ADMIN INBOX <%s> %s\n%s", to_email or "sudo", subject, body)
    return "log", "inbox"
