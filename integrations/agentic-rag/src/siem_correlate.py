"""
Phase 8.3 — SIEM alert correlation.

Groups raw alerts into "incidents" — units of work that a SOC analyst
would reason about as one thing. Two alerts land in the same incident
if they share a primary entity (host OR user) and fall within a sliding
time window.

Design:
  - Entity-first grouping: we pick the entity key that produces the
    tightest clusters, then union-find merge within the time window.
  - Sliding window: default 10 minutes. Alerts outside the window form
    a new incident even on the same host.
  - Deterministic incident IDs, ordered by earliest alert timestamp.
  - Severity of an incident = max severity of its alerts.
  - Every incident carries a `primary_entity` and a member alert list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, Optional

from src.siem_ingest import Alert

DEFAULT_WINDOW = timedelta(minutes=10)

SEVERITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


@dataclass
class Incident:
    incident_id: str
    primary_entity: dict          # {"host": ..., "user": ...} — the shared anchor
    alerts: list[Alert] = field(default_factory=list)
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None

    @property
    def severity(self) -> str:
        if not self.alerts:
            return "LOW"
        return max((a.severity for a in self.alerts), key=lambda s: SEVERITY_RANK[s])

    @property
    def sources(self) -> set[str]:
        return {a.source for a in self.alerts}

    @property
    def rule_ids(self) -> list[str]:
        seen = []
        for a in self.alerts:
            if a.rule_id not in seen:
                seen.append(a.rule_id)
        return seen

    @property
    def size(self) -> int:
        return len(self.alerts)

    def ground_truth_summary(self) -> Optional[str]:
        """For eval only. TRUE_POSITIVE if any member is a TP."""
        labels = [a.ground_truth for a in self.alerts if a.ground_truth]
        if not labels:
            return None
        return "TRUE_POSITIVE" if "TRUE_POSITIVE" in labels else "FALSE_POSITIVE"

    def as_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "primary_entity": self.primary_entity,
            "severity": self.severity,
            "size": self.size,
            "sources": sorted(self.sources),
            "rule_ids": self.rule_ids,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "window_end": self.window_end.isoformat() if self.window_end else None,
            "alert_ids": [a.alert_id for a in self.alerts],
        }


def _entity_key(alert: Alert, field_name: str) -> Optional[str]:
    """Return a stable key for a given entity dimension, or None."""
    v = alert.entity.get(field_name)
    return v if v else None


def _bucket_by_key(alerts: list[Alert], field_name: str, window: timedelta) -> list[list[Alert]]:
    """
    For one entity dimension, group alerts into time-windowed buckets.
    """
    by_key: dict[str, list[Alert]] = {}
    for a in alerts:
        k = _entity_key(a, field_name)
        if not k:
            continue
        by_key.setdefault(k, []).append(a)

    groups: list[list[Alert]] = []
    for k, bucket in by_key.items():
        bucket.sort(key=lambda a: a.timestamp)
        current: list[Alert] = []
        for a in bucket:
            if not current:
                current = [a]
                continue
            if a.timestamp - current[-1].timestamp <= window:
                current.append(a)
            else:
                groups.append(current)
                current = [a]
        if current:
            groups.append(current)
    return groups


def correlate(
    alerts: Iterable[Alert],
    window: timedelta = DEFAULT_WINDOW,
) -> list[Incident]:
    """
    Turn a stream of alerts into incidents.

    Approach:
      1. Bucket alerts by host within the sliding window.
      2. Bucket alerts by user within the sliding window.
      3. Merge overlapping buckets (an alert appearing in both host and
         user buckets merges those two groups into one incident).
      4. Anything left ungrouped becomes a singleton incident.
    """
    alerts = sorted(alerts, key=lambda a: a.timestamp)

    host_groups = _bucket_by_key(alerts, "host", window)
    user_groups = _bucket_by_key(alerts, "user", window)
    all_groups = host_groups + user_groups

    # --- Union-find merge on alert_id overlap ---
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a in alerts:
        parent[a.alert_id] = a.alert_id

    for group in all_groups:
        ids = [a.alert_id for a in group]
        for i in range(1, len(ids)):
            union(ids[0], ids[i])

    # --- Materialize merged incidents ---
    merged: dict[str, list[Alert]] = {}
    for a in alerts:
        root = find(a.alert_id)
        merged.setdefault(root, []).append(a)

    # --- Build Incident objects ---
    incidents: list[Incident] = []
    for i, members in enumerate(
        sorted(merged.values(), key=lambda g: min(a.timestamp for a in g)),
        start=1,
    ):
        members.sort(key=lambda a: a.timestamp)

        # Choose primary entity: prefer the (host, user) pair that
        # appears most frequently in the incident.
        host_counts: dict[str, int] = {}
        user_counts: dict[str, int] = {}
        for a in members:
            if a.host:
                host_counts[a.host] = host_counts.get(a.host, 0) + 1
            if a.user:
                user_counts[a.user] = user_counts.get(a.user, 0) + 1

        primary = {
            "host": max(host_counts, key=host_counts.get) if host_counts else None,
            "user": max(user_counts, key=user_counts.get) if user_counts else None,
        }

        incidents.append(
            Incident(
                incident_id=f"i-{i:04d}",
                primary_entity=primary,
                alerts=members,
                window_start=members[0].timestamp,
                window_end=members[-1].timestamp,
            )
        )

    return incidents


def incident_summary(incidents: list[Incident]) -> dict:
    """Quick stats for logging / the eval harness."""
    from collections import Counter
    sizes = Counter(i.size for i in incidents)
    return {
        "total_incidents": len(incidents),
        "total_alerts": sum(i.size for i in incidents),
        "size_distribution": dict(sorted(sizes.items())),
        "singletons": sum(1 for i in incidents if i.size == 1),
        "multi_alert": sum(1 for i in incidents if i.size > 1),
        "severity_distribution": dict(Counter(i.severity for i in incidents)),
    }


if __name__ == "__main__":
    from src.siem_ingest import load_alerts

    alerts = load_alerts()
    incidents = correlate(alerts)

    print(f"Correlated {len(alerts)} alerts → {len(incidents)} incidents")
    print()
    summary = incident_summary(incidents)
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nTop 5 largest incidents:")
    for inc in sorted(incidents, key=lambda i: -i.size)[:5]:
        print(f"  {inc.incident_id}  size={inc.size}  severity={inc.severity}  "
              f"host={inc.primary_entity['host']}  user={inc.primary_entity['user']}")
        print(f"    rules: {inc.rule_ids}")
        print(f"    ground_truth: {inc.ground_truth_summary()}")
