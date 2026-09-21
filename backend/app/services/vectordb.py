"""Vector-DB tenant-boundary enforcement + retrieval audit.

Help — design, dependencies:
- Policy (no new tables needed): each vector-database `AIAsset` is owned by one
  tenant (`AIAsset.owner`). `check_retrieval(db, agent, store, tenant, doc_class)`:
  DENY when the store exists, the doc is non-public, and the requesting tenant
  differs from the store owner. Public docs are always allowed; unknown stores
  are allowed but flagged for inventory (`known_store=False`).
- `log_retrieval(db, ...)`: persists a `RetrievalEvent`; on DENY also raises a
  HIGH `Finding` on the first asset + audit row (containment: fix scope, re-run).
- Served by `POST /api/ai/retrieval-audit` (log+enforce) and
  `GET /api/ai/retrieval-audit` (review). Read/write split keeps checks testable.
"""
RESTRICTED_CLASSES = {"restricted", "secret", "confidential"}


def check_retrieval(db, agent: str, store: str, tenant: str, doc_class: str) -> dict:
    """Evaluate one retrieval against tenant policy. Returns {allowed, reason, known_store}."""
    from ..models import AIAsset
    row = db.query(AIAsset).filter(AIAsset.name == store,
                                   AIAsset.asset_type == "vector database").first()
    if row is None:
        return {"allowed": True, "known_store": False,
                "reason": f"Store '{store}' not in inventory — allowed once, add it to AI assets."}
    if (doc_class or "").lower() in RESTRICTED_CLASSES and (tenant or "") != (row.owner or ""):
        return {"allowed": False, "known_store": True,
                "reason": f"Tenant '{tenant}' != owner '{row.owner}' for {doc_class} docs — cross-tenant read denied."}
    return {"allowed": True, "known_store": True,
            "reason": f"Tenant '{tenant}' matches owner '{row.owner}' or doc is public."}


def log_retrieval(db, agent: str, store: str, tenant: str, doc_class: str) -> dict:
    """Persist the event; on DENY raise HIGH finding + audit. Returns {event, allowed, reason}."""
    from ..models import RetrievalEvent, Finding, Asset, AuditEvent
    verdict = check_retrieval(db, agent, store, tenant, doc_class)
    ev = RetrievalEvent(agent=agent, vector_store=store, tenant=tenant,
                        doc_class=doc_class, allowed=verdict["allowed"])
    db.add(ev)
    if not verdict["allowed"]:
        asset = db.query(Asset).first()
        db.add(Finding(asset_id=asset.id if asset else 1,
                       title=f"Cross-tenant vector read denied: {agent} → {store}"[:255],
                       severity="HIGH", cvss=0, exposure=False, data_sensitivity=5,
                       risk_score=72,
                       description=f"{verdict['reason']} Scope the agent to tenant data."[:2000]))
        db.add(AuditEvent(actor="policy-engine", action="retrieval_denied",
                          target=f"{agent} → {store} [{tenant}]", outcome="denied"))
    db.commit()
    return {"allowed": verdict["allowed"], "reason": verdict["reason"],
            "event_id": ev.id}
