"""VEYRA alerts — chip degradation + drop event notifications (P6-G).

Best-effort webhook/Slack/email via notify.py + AdminNotification inbox.
Never fails the caller; all sends are audit-logged as fire-and-forget.
"""
from __future__ import annotations

import os
import json
import logging
from datetime import datetime, timezone

log = logging.getLogger("veyra.alerts")


def _should_alert_chip(chip: str) -> bool:
    return chip in ("semi_red", "red")


def _targets() -> list[str]:
    # comma-separated webhook URLs or Slack webhook
    raw = os.getenv("VEYRA_ALERT_WEBHOOKS", "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _send(to: str, subject: str, body: str) -> None:
    # Try email via notify, then HTTP webhook if configured
    try:
        from app.services.notify import admin_email, send_access_request_email  # reuse plumbing

        # Mirror to admin inbox always
        from app.db import SessionLocal
        from app.models import AdminNotification

        db = SessionLocal()
        try:
            db.add(AdminNotification(to_role="sudo", to_email=to[:255], subject=subject[:255], body=body[:4000], channel="alert", status="queued", related_id=subject[:64]))
            db.commit()
        finally:
            db.close()
    except Exception as e:  # noqa
        log.warning("alert inbox mirror failed: %s", e)

    for url in _targets():
        try:
            import httpx

            httpx.post(url, json={"text": f"{subject}\n{body}"}, timeout=5)
        except Exception as e:  # noqa
            log.warning("webhook alert failed %s: %s", url, e)

    # optional email if SMTP configured
    try:
        from app.services.notify import send_access_request_email

        cfg_to = os.getenv("VEYRA_ADMIN_EMAIL", "").strip() or to
        if cfg_to and os.getenv("SMTP_HOST"):
            send_access_request_email(cfg_to, "veyra-alerts", subject, "alert", 0, body, "alert")
    except Exception:
        pass


def notify_checklist_run(checklist_id: str, run_id: str, tier: str, evidence: dict | None) -> None:
    # Only alert on essential tier with evidence indicating degradation
    # For now, alert when evidence contains chip=red/semi_red or explicit alert flag
    if not evidence:
        return
    chip = str(evidence.get("chip", "")).lower()
    if _should_alert_chip(chip) or evidence.get("alert"):
        _send(
            os.getenv("VEYRA_ADMIN_EMAIL", "sudo"),
            f"[VEYRA] Checklist {checklist_id} degradation → {chip or 'alert'}",
            f"Run {run_id} (tier {tier}) reported {json.dumps(evidence)[:500]} at {datetime.now(timezone.utc).isoformat()}",
        )


def notify_sensor_event(normalized: dict) -> None:
    _send(
        os.getenv("VEYRA_ADMIN_EMAIL", "sudo"),
        f"[VEYRA] Sensor {normalized['sensor_type']} {normalized['event_type']} {normalized['severity']}",
        f"Event {normalized['event_id']} provenance {normalized['provenance']} payload {json.dumps(normalized['payload'])[:500]}",
    )


def notify_drop(link_id: str, hypotheses: list) -> None:
    top = hypotheses[0]["cause"] if hypotheses else "unknown"
    _send(
        os.getenv("VEYRA_ADMIN_EMAIL", "sudo"),
        f"[VEYRA] Drop {link_id} — {top}",
        f"Hypotheses: {json.dumps(hypotheses)[:800]}",
    )
