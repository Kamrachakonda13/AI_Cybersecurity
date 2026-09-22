"""VEYRA drop diagnosis — root-cause hypotheses for link drops (P6-B).

Pure logic, no enforcement. Hypotheses are advisory only.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Literal

LinkType = Literal["wifi", "ethernet", "unknown"]


def _utc() -> datetime:
    return datetime.now(timezone.utc)


def diagnose(
    link_type: str,
    signal_dbm: float | None = None,
    dhcp_state: str = "unknown",
    dns_state: str = "unknown",
    ap_assoc_state: str = "unknown",
    recent_flaps: int = 0,
) -> list[dict]:
    """Return ordered hypotheses (highest confidence first)."""
    hyps: list[dict] = []
    if link_type == "wifi":
        if signal_dbm is not None and signal_dbm < -75:
            hyps.append({"cause": "weak_signal", "confidence": 0.85, "evidence": f"RSSI {signal_dbm} dBm"})
        if ap_assoc_state == "disassociated":
            hyps.append({"cause": "ap_disassociation", "confidence": 0.8, "evidence": "AP disassociated"})
        if dhcp_state == "failed":
            hyps.append({"cause": "dhcp_failure", "confidence": 0.7, "evidence": "DHCP failed"})
        if dns_state == "failed":
            hyps.append({"cause": "dns_failure", "confidence": 0.6, "evidence": "DNS failed"})
        if not hyps:
            hyps.append({"cause": "unknown_wireless", "confidence": 0.3, "evidence": "no strong signal"})
    elif link_type == "ethernet":
        if recent_flaps >= 3:
            hyps.append({"cause": "flapping_cable", "confidence": 0.8, "evidence": f"{recent_flaps} flaps"})
        if dhcp_state == "failed":
            hyps.append({"cause": "dhcp_failure", "confidence": 0.7, "evidence": "DHCP failed"})
        if not hyps:
            hyps.append({"cause": "unknown_wired", "confidence": 0.3, "evidence": "no strong signal"})
    else:
        hyps.append({"cause": "unknown_link", "confidence": 0.2, "evidence": "unknown link_type"})
    return sorted(hyps, key=lambda h: h["confidence"], reverse=True)


def persist_drop(
    db,
    link_id: str,
    link_type: str = "wifi",
    signal_dbm: float | None = None,
    dhcp_state: str = "unknown",
    dns_state: str = "unknown",
    ap_assoc_state: str = "unknown",
    recent_flaps: int = 0,
) -> object:
    from app.models import DropEvent

    hyps = diagnose(link_type, signal_dbm, dhcp_state, dns_state, ap_assoc_state, recent_flaps)
    diagnosis = {"link_type": link_type, "signal_dbm": signal_dbm, "dhcp_state": dhcp_state, "dns_state": dns_state, "ap_assoc_state": ap_assoc_state, "recent_flaps": recent_flaps}
    row = DropEvent(
        drop_id="drop_" + uuid.uuid4().hex[:16],
        link_id=link_id,
        link_type=link_type,
        diagnosis_json=json.dumps(diagnosis, sort_keys=True),
        hypotheses_json=json.dumps(hyps, sort_keys=True),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
