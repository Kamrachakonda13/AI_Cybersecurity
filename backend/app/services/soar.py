"""SOAR playbook engine (approval-gated, DB-safe actions only).

Help — design, dependencies, safety:
- `PLAYBOOKS`: isolate_host (revoke host sessions + HIGH incident), revoke_sessions
  (by username), block_ip (ThreatIntel block indicator + incident), collect_evidence
  (incident + triage note). Actions touch ONLY our DB rows — no firewall/API calls,
  no host commands. Real enforcement integrations are future work behind the same gate.
- `run_playbook(db, name, target, actor, approved)`: unapproved → creates a
  `pending_approval` `SoarRun` and returns it (nothing executes). Approved/new →
  executes steps, marks run `completed` with a result summary. Every step writes an
  `AuditEvent`. Unknown playbook → ValueError (route maps to 400).
- `approve_run(db, run_id, actor)`: executes a pending run. Served, with the above,
  by `POST /api/soar/runs`, `POST /api/soar/runs/{id}/approve`, `GET /api/soar/runs`,
  `GET /api/soar/playbooks`. Depends on: Asset, SessionEvent, Incident,
  ThreatIntel, SoarRun, AuditEvent models.
"""
PLAYBOOKS = [
    {"name": "isolate_host", "target": "hostname",
     "use": "Suspected-compromised host: revoke its sessions + open HIGH incident.",
     "steps": ["revoke host sessions", "open incident", "audit"]},
    {"name": "revoke_sessions", "target": "username",
     "use": "Compromised/leaving account: revoke all its sessions.",
     "steps": ["revoke user sessions", "audit"]},
    {"name": "block_ip", "target": "IP",
     "use": "Record attacker IP as block indicator + incident for perimeter import.",
     "steps": ["record indicator", "open incident", "audit"]},
    {"name": "collect_evidence", "target": "hostname or IP",
     "use": "Bundle triage pointers into an incident without changing state.",
     "steps": ["open incident", "audit"]},
]
_BY_NAME = {p["name"] for p in PLAYBOOKS}


def _audit(db, actor, action, target, outcome="success"):
    from ..models import AuditEvent
    db.add(AuditEvent(actor=actor, action=action, target=target, outcome=outcome))


def _revoke_sessions_q(db, actor, query, label: str) -> int:
    n = 0
    for s in query.all():
        if s.status != "revoked":
            s.status = "revoked"
            n += 1
    _audit(db, actor, "soar_revoke_sessions", f"{label}: {n} revoked")
    return n


def run_playbook(db, name: str, target: str, actor: str = "analyst", approved: bool = False) -> dict:
    """Create (unapproved) or execute (approved) a playbook run. Returns run summary dict."""
    from ..models import SoarRun
    if name not in _BY_NAME:
        raise ValueError(f"Unknown playbook '{name}'")
    if not target.strip():
        raise ValueError("Explicit target is required")
    run = SoarRun(playbook=name, target=target.strip(), actor=actor,
                  status="approved" if approved else "pending_approval")
    db.add(run)
    db.commit()
    if not approved:
        _audit(db, actor, "soar_run_pending", f"{name} on {target}", "pending-approval")
        db.commit()
        return {"id": run.id, "status": run.status,
                "message": "Awaiting approval — nothing executed. Approve to run."}
    return _execute(db, run, actor)


def approve_run(db, run_id: int, actor: str = "analyst") -> dict:
    """Approve + execute a pending run. Errors on missing/already-decided runs."""
    from ..models import SoarRun
    run = db.get(SoarRun, run_id)
    if run is None:
        raise ValueError(f"No run {run_id}")
    if run.status != "pending_approval":
        raise ValueError(f"Run {run_id} already {run.status}")
    run.status = "approved"
    db.commit()
    return _execute(db, run, actor)


def _execute(db, run, actor: str) -> dict:
    from ..models import Asset, SessionEvent, Incident, ThreatIntel
    actions: list[str] = []
    if run.playbook == "isolate_host":
        asset = db.query(Asset).filter(Asset.hostname == run.target).first()
        if asset is None:
            raise ValueError(f"Unknown host '{run.target}'")
        n = _revoke_sessions_q(db, actor, db.query(SessionEvent).filter(
            SessionEvent.asset_id == asset.id), run.target)
        actions.append(f"revoked {n} sessions on {run.target}")
        db.add(Incident(title=f"Host isolated (SOAR): {run.target}", severity="HIGH",
                        asset=run.target,
                        summary=f"Approved isolation: {n} sessions revoked. Verify clean, then re-enable."))
        actions.append("opened HIGH incident")
    elif run.playbook == "revoke_sessions":
        n = _revoke_sessions_q(db, actor, db.query(SessionEvent).filter(
            SessionEvent.username == run.target), run.target)
        actions.append(f"revoked {n} sessions for {run.target}")
    elif run.playbook == "block_ip":
        db.add(ThreatIntel(source="SOAR", indicator=run.target, indicator_type="IP",
                           title=f"Blocked attacker IP {run.target}", severity="HIGH",
                           exploited=False,
                           description="Approved block — import to perimeter/DNS firewall."))
        actions.append(f"recorded block indicator {run.target}")
        db.add(Incident(title=f"Block IP (SOAR): {run.target}", severity="HIGH",
                        asset="perimeter",
                        summary=f"Approved block for {run.target}; confirm on firewall."))
        actions.append("opened HIGH incident")
    elif run.playbook == "collect_evidence":
        db.add(Incident(title=f"Evidence bundle (SOAR): {run.target}", severity="MEDIUM",
                        asset=run.target,
                        summary="Triage pointers preserved: flows, logins, sessions, DNS. No state changed."))
        actions.append("opened MEDIUM evidence incident")
    run.status = "completed"
    run.result = "; ".join(actions)
    _audit(db, actor, "soar_run_completed", f"{run.playbook} on {run.target}: {run.result}")
    db.commit()
    return {"id": run.id, "status": run.status, "actions": actions}
