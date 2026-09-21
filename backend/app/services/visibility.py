"""Detection helpers for own-network visibility.

- brute_force_candidates: groups FAILED logins by (source_ip) and (username);
  flags >= 5 fails as a candidate (tunable). Pure counts — no blocking action.
- browsing_summary: top domains by total hits + per-device top domain.
"""
from collections import Counter
from sqlalchemy import func


BRUTE_FORCE_THRESHOLD = 5

BRUTE_HELP = ("≥5 failed logins from one IP (or against one account) = brute-force / "
              "password-spray candidate. Verify: is the IP yours (lab) or external? "
              "Check Identity for MFA + privilege, then contain per IR process — never retaliate.")


def brute_force_candidates(db) -> dict:
    """Group FAILED logins by IP and username; flag ≥ `BRUTE_FORCE_THRESHOLD` (5) as candidates.

    Depends on: `LoginAttempt` rows from `POST /api/ingest/logins`. Read-only.
    Served by `GET /api/logins/summary`; consumed by Identity view + session triage.
    """
    from ..models import LoginAttempt
    fails = db.query(LoginAttempt).filter(LoginAttempt.success.is_(False)).all()
    by_ip = Counter(f.source_ip for f in fails)
    by_user = Counter(f.username for f in fails)
    total = db.query(func.count(LoginAttempt.id)).scalar() or 0
    return {
        "total_attempts": total,
        "failed": len(fails),
        "by_ip": [{"source_ip": ip, "failed": c,
                   "candidate": c >= BRUTE_FORCE_THRESHOLD} for ip, c in by_ip.most_common(20)],
        "by_user": [{"username": u, "failed": c,
                     "candidate": c >= BRUTE_FORCE_THRESHOLD} for u, c in by_user.most_common(20)],
        "threshold": BRUTE_FORCE_THRESHOLD,
        "help": BRUTE_HELP,
    }


def browsing_summary(db, limit: int = 25) -> dict:
    """Top domains by hits + per-device top domain from `DnsQuery` rows.

    Depends on: `POST /api/ingest/dns` data (DNS metadata only — never content).
    Served by `GET /api/dns/top`; consumed by the Endpoint view.
    """
    from ..models import DnsQuery
    rows = db.query(DnsQuery).all()
    dom = Counter()
    per_host: dict[str, Counter] = {}
    for r in rows:
        dom[r.domain] += r.hits
        per_host.setdefault(r.hostname or "unknown", Counter())[r.domain] += r.hits
    return {
        "top_domains": [{"domain": d, "hits": c} for d, c in dom.most_common(limit)],
        "per_device": [{"hostname": h, "top_domain": c.most_common(1)[0][0] if c else "—",
                        "queries": sum(c.values())} for h, c in per_host.items()],
        "note": "DNS metadata only (domains + counts) from your own network with notice. "
                "No page content is collected — that would require MITM and is out of scope.",
    }
