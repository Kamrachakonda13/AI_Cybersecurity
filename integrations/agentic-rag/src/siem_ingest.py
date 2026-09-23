"""
Phase 8.2 — SIEM alert ingest + normalization.

Reads data/siem/alerts.jsonl, validates each record, and returns a
list of normalized Alert dataclasses. The rest of the pipeline works
against this typed interface, not the raw JSONL.

Design:
  - Validation is strict: a malformed record is skipped with a warning
    (never silently accepted).
  - The dataclass preserves labels.ground_truth — used only by the
    eval harness, never by the triage pipeline.
  - Filters are exposed so the dashboard and the eval can slice the
    feed by source / severity / time window.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_FEED = Path("data/siem/alerts.jsonl")

REQUIRED_FIELDS = ("alert_id", "timestamp", "source", "rule_id", "rule_name", "severity")
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_SOURCES = {"edr", "firewall", "idp", "cloud"}


class AlertValidationError(ValueError):
    pass


@dataclass
class Alert:
    alert_id: str
    timestamp: datetime
    source: str
    rule_id: str
    rule_name: str
    severity: str
    entity: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)
    ground_truth: Optional[str] = None   # eval-only; never read by triage

    @property
    def host(self) -> Optional[str]:
        return self.entity.get("host")

    @property
    def user(self) -> Optional[str]:
        return self.entity.get("user")

    @property
    def src_ip(self) -> Optional[str]:
        return self.entity.get("src_ip")

    def as_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "entity": self.entity,
            "raw": self.raw,
        }


def _parse_alert(obj: dict) -> Alert:
    for f in REQUIRED_FIELDS:
        if f not in obj:
            raise AlertValidationError(f"missing field: {f}")

    if obj["severity"] not in VALID_SEVERITIES:
        raise AlertValidationError(f"invalid severity: {obj['severity']}")
    if obj["source"] not in VALID_SOURCES:
        raise AlertValidationError(f"invalid source: {obj['source']}")

    ts_raw = obj["timestamp"].replace("Z", "+00:00")
    try:
        ts = datetime.fromisoformat(ts_raw)
    except ValueError as e:
        raise AlertValidationError(f"invalid timestamp: {obj['timestamp']} ({e})")

    labels = obj.get("labels") or {}

    return Alert(
        alert_id=obj["alert_id"],
        timestamp=ts,
        source=obj["source"],
        rule_id=obj["rule_id"],
        rule_name=obj["rule_name"],
        severity=obj["severity"],
        entity=obj.get("entity") or {},
        raw=obj.get("raw") or {},
        ground_truth=labels.get("ground_truth"),
    )


def load_alerts(path: Path = DEFAULT_FEED, *, strict: bool = False) -> list[Alert]:
    """
    Load and validate alerts from JSONL.

    Args:
        path: path to alerts.jsonl
        strict: if True, raise on the first invalid record.
                if False, skip invalid records and count them.

    Returns:
        List of Alert dataclasses, sorted by timestamp.
    """
    if not path.exists():
        raise FileNotFoundError(f"feed not found: {path}")

    alerts: list[Alert] = []
    skipped = 0

    with path.open() as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                alerts.append(_parse_alert(obj))
            except (json.JSONDecodeError, AlertValidationError) as e:
                if strict:
                    raise AlertValidationError(f"line {lineno}: {e}") from e
                skipped += 1
                print(f"[warn] skipped line {lineno}: {e}")

    alerts.sort(key=lambda a: a.timestamp)

    if skipped:
        print(f"[warn] {skipped} record(s) skipped out of {len(alerts) + skipped}")

    return alerts


def filter_alerts(
    alerts: Iterable[Alert],
    *,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    host: Optional[str] = None,
    user: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> list[Alert]:
    """Filter alerts by any combination of criteria."""
    out = []
    for a in alerts:
        if source and a.source != source:
            continue
        if severity and a.severity != severity:
            continue
        if host and a.host != host:
            continue
        if user and a.user != user:
            continue
        if since and a.timestamp < since:
            continue
        if until and a.timestamp > until:
            continue
        out.append(a)
    return out


if __name__ == "__main__":
    alerts = load_alerts()
    print(f"Loaded {len(alerts)} alerts")
    print(f"Time range: {alerts[0].timestamp.isoformat()} → {alerts[-1].timestamp.isoformat()}")

    from collections import Counter
    print("\nBy source:   ", dict(Counter(a.source for a in alerts)))
    print("By severity: ", dict(Counter(a.severity for a in alerts)))
    print("By label:    ", dict(Counter(a.ground_truth for a in alerts)))

    print("\nSample alert:")
    print(json.dumps(alerts[0].as_dict(), indent=2))
