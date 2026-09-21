"""VEYRA v2.3 Threat Intelligence + DFIR fusion.

This service is evidence-first: it correlates normalized telemetry with the
locally ingested threat-intelligence corpus and deterministic ATT&CK/ATLAS
mappings. Attribution is represented only as hypotheses with supporting and
contradicting evidence; it never asserts actor identity or performs external
lookups/side effects.
"""
from datetime import datetime, timezone
import hashlib, json
from ..models import UnifiedSecurityEvent, ThreatIntel, InvestigationCase, InvestigationEvidence, AuditEvent, AttributionHypothesis, IntelEnrichment

EVENT_TECHNIQUES = {
    "login_anomaly": ["T1110", "T1078"],
    "privileged_session": ["T1078", "T1098"],
    "network_anomaly": ["T1041", "T1021"],
    "possible_exfiltration": ["T1041", "T1567"],
    "process_anomaly": ["T1059", "T1204"],
    "persistence_signal": ["T1547"],
    "cloud_anomaly": ["T1078.004", "T1098"],
    "privilege_change": ["T1098", "T1078"],
    "agent_tool_call": ["AML.T0051", "AML.T0054"],
    "ai_gateway_denial": ["AML.T0051"],
}

HYPOTHESES = {
    "identity-compromise": {"events": {"login_anomaly", "privileged_session", "privilege_change"}, "base": 0.35},
    "credential-abuse": {"events": {"login_anomaly", "privileged_session"}, "base": 0.30},
    "data-exfiltration": {"events": {"network_anomaly", "possible_exfiltration"}, "base": 0.35},
    "agent-tool-misuse": {"events": {"agent_tool_call", "ai_gateway_denial"}, "base": 0.35},
    "persistence": {"events": {"process_anomaly", "persistence_signal"}, "base": 0.25},
    "cloud-identity-abuse": {"events": {"cloud_anomaly", "privilege_change"}, "base": 0.25},
}

def _now(): return datetime.now(timezone.utc)
def _sha(v): return hashlib.sha256(json.dumps(v, sort_keys=True, default=str).encode()).hexdigest()

def _event_text(event):
    payload = json.loads(event.payload or "{}")
    return " ".join(str(x) for x in [event.actor,event.source,event.target,event.event_type,payload]).lower()

def _intel_matches(db, event):
    text = _event_text(event)
    matches=[]
    for ti in db.query(ThreatIntel).all():
        ind=(ti.indicator or "").strip().lower()
        if ind and ind in text:
            matches.append({"id":ti.id,"indicator":ti.indicator,"indicator_type":ti.indicator_type,
                            "title":ti.title,"source":ti.source,"severity":ti.severity,
                            "exploited":ti.exploited,"description":ti.description})
    return matches[:25]

def _hypotheses(event, intel, techniques):
    out=[]
    for name, spec in HYPOTHESES.items():
        score=spec["base"] if event.event_type in spec["events"] else 0.0
        supporting=[]; contradicting=[]
        if score:
            supporting.append(f"event_type={event.event_type}")
        if intel:
            score += min(0.35, 0.08*len(intel))
            supporting.append(f"{len(intel)} threat-intelligence correlation(s)")
        if techniques:
            score += min(0.20, 0.04*len(techniques))
            supporting.append("mapped ATT&CK/ATLAS behavior")
        if name == "data-exfiltration" and event.risk_score < 60:
            score -= 0.10; contradicting.append("risk score below exfiltration confidence threshold")
        if score > 0:
            out.append({"hypothesis":name,"confidence":round(max(0,min(0.95,score)),2),
                        "supporting_evidence":supporting,"contradicting_evidence":contradicting,
                        "assessment":"hypothesis_only"})
    return sorted(out,key=lambda x:x["confidence"],reverse=True)

def fuse_case(db, case_id: str):
    case=db.query(InvestigationCase).filter(InvestigationCase.case_id==case_id).first()
    if not case: raise ValueError("Unknown case")
    event=db.query(UnifiedSecurityEvent).filter(UnifiedSecurityEvent.event_id==case.trigger_event_id).first()
    if not event: raise ValueError("Trigger event unavailable")
    intel=_intel_matches(db,event)
    techniques=EVENT_TECHNIQUES.get(event.event_type,[])
    hypotheses=_hypotheses(event,intel,techniques)
    bundle={"case_id":case_id,"event_id":event.event_id,"intel_matches":intel,
            "techniques":[{"framework":"MITRE ATT&CK" if not t.startswith("AML.") else "MITRE ATLAS","technique":t} for t in techniques],
            "attribution_hypotheses":hypotheses,"generated_at":_now().isoformat(),
            "provenance":"deterministic-local-correlation"}
    # Add a compact, hashed evidence record rather than copying raw evidence.
    eid=f"fusion_{_sha(bundle)[:16]}"
    if not db.query(InvestigationEvidence).filter(InvestigationEvidence.evidence_id==eid).first():
        db.add(InvestigationEvidence(evidence_id=eid,case_id=case_id,source_type="intel_fusion",
            source_ref=event.event_id,sha256=_sha(bundle),summary="Threat-intelligence, ATT&CK/ATLAS and attribution-hypothesis fusion",supports=True))
        for i, h in enumerate(hypotheses):
            hid=f"hyp_{_sha({'case':case_id,'label':h['hypothesis']})[:16]}"
            if not db.query(AttributionHypothesis).filter(AttributionHypothesis.hypothesis_id==hid).first():
                db.add(AttributionHypothesis(hypothesis_id=hid,case_id=case_id,label=h['hypothesis'],confidence=h['confidence'],
                    supporting_json=json.dumps(h['supporting_evidence']),contradicting_json=json.dumps(h['contradicting_evidence']),assessment=h['assessment']))
        for t in techniques:
            framework="MITRE ATT&CK" if not t.startswith("AML.") else "MITRE ATLAS"
            eid2=f"enr_{_sha({'case':case_id,'framework':framework,'ref':t})[:16]}"
            if not db.query(IntelEnrichment).filter(IntelEnrichment.enrichment_id==eid2).first():
                db.add(IntelEnrichment(enrichment_id=eid2,case_id=case_id,framework=framework,reference=t,
                    summary=f"Behavior mapping for {event.event_type}",evidence_sha256=_sha({'event':event.event_id,'technique':t})))
        db.add(AuditEvent(actor="intel-fusion",action="case_fused",target=case_id,outcome="completed"))
        db.commit()
    return bundle

def list_fusion_cases(db, limit=50):
    cases=db.query(InvestigationCase).order_by(InvestigationCase.updated_at.desc()).limit(limit).all()
    out=[]
    for c in cases:
        try: out.append(fuse_case(db,c.case_id))
        except ValueError: pass
    return out
