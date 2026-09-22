"""VEYRA live sensor ingest — normalizer (P6-B).

Token-gated at the API layer; this module is pure normalization + hashing.
Every event gets: event_id, event_sha256, observed_at, provenance.

Governance: no deauth, no injection, no credential capture. Read-only.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Literal

SensorType = Literal["wifi", "ethernet", "device", "drop", "traffic"]
EventSeverity = Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

VALID_SENSORS = {"wifi", "ethernet", "device", "drop", "traffic"}
VALID_SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _utc() -> datetime:
    return datetime.now(timezone.utc)


def _sha(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def normalize_event(
    sensor_type: str,
    event_type: str,
    payload: dict | None = None,
    sensor_id: str = "unknown",
    severity: str = "INFO",
    provenance: str = "",
    trace_id: str = "",
) -> dict:
    """Normalize a raw sensor event. Raises ValueError on bad input."""
    if sensor_type not in VALID_SENSORS:
        raise ValueError(f"Unknown sensor_type: {sensor_type}")
    if not event_type or not event_type.strip():
        raise ValueError("event_type is required")
    if severity not in VALID_SEVERITIES:
        raise ValueError(f"Unknown severity: {severity}")
    payload = dict(payload or {})
    event_id = "evt_" + uuid.uuid4().hex[:16]
    observed_at = _utc().isoformat()
    base = {
        "event_id": event_id,
        "sensor_type": sensor_type,
        "sensor_id": sensor_id,
        "event_type": event_type.strip(),
        "severity": severity,
        "payload": payload,
        "provenance": provenance or f"sensor:{sensor_type}:{sensor_id}",
        "trace_id": trace_id,
        "observed_at": observed_at,
    }
    base["event_sha256"] = _sha({k: base[k] for k in ("sensor_type", "event_type", "payload", "observed_at")})
    return base


def persist_event(db, normalized: dict) -> object:
    """Persist a normalized event to live_sensor_events."""
    from app.models import LiveSensorEvent

    row = LiveSensorEvent(
        event_id=normalized["event_id"],
        sensor_type=normalized["sensor_type"],
        sensor_id=normalized["sensor_id"],
        event_type=normalized["event_type"],
        severity=normalized["severity"],
        payload_json=json.dumps(normalized["payload"], sort_keys=True),
        provenance=normalized["provenance"],
        event_sha256=normalized["event_sha256"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
