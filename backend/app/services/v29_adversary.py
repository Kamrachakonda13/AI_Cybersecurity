"""AegisX v2.9 adversary-intelligence and wireless-defense composition layer.

This layer intentionally composes existing telemetry into investigation views.
It does not execute wireless attacks, hack back, deploy persistence, or expose
arbitrary shell commands. Attribution is evidence-backed hypothesis only.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import Asset, Service, NetworkFlow, SessionEvent, Identity, WifiNetwork, DiscoveredHost, ThreatIntel, Incident, AuditEvent

def _iso(v): return v.isoformat() if hasattr(v, 'isoformat') else v

def overview(db: Session):
    return {
        "version":"2.9",
        "mission":"Adversary reconstruction + wireless defense + evidence preservation",
        "attribution_mode":"hypothesis_only",
        "wireless": {
            "access_points": db.query(WifiNetwork).count(),
            "lan_devices": db.query(DiscoveredHost).count(),
            "unknown_devices": db.query(DiscoveredHost).filter(DiscoveredHost.trusted == False).count(),
        },
        "telemetry": {
            "assets": db.query(Asset).count(),
            "services": db.query(Service).count(),
            "flows": db.query(NetworkFlow).count(),
            "sessions": db.query(SessionEvent).count(),
            "identities": db.query(Identity).count(),
        },
        "investigation": {
            "open_incidents": db.query(Incident).filter(Incident.status == "open").count(),
            "intel_records": db.query(ThreatIntel).count(),
            "audit_events": db.query(AuditEvent).count(),
        },
        "pipeline":["observe","preserve","correlate","reconstruct","enrich","hypothesize","verify","contain","recover"],
    }

def wireless(db: Session):
    aps = db.query(WifiNetwork).order_by(WifiNetwork.id.desc()).limit(200).all()
    hosts = db.query(DiscoveredHost).order_by(DiscoveredHost.id.desc()).limit(200).all()
    return {
        "access_points":[{"id":x.id,"ssid":x.ssid,"bssid":x.bssid,"signal_dbm":x.signal_dbm,"band":x.band,"channel":x.channel,"security":x.security} for x in aps],
        "clients":[{"id":x.id,"hostname":x.hostname,"ip_address":x.ip_address,"mac":x.mac,"vendor":x.vendor,"trusted":x.trusted,"last_seen":_iso(x.last_seen)} for x in hosts],
        "rogue_candidates":[
            {"type":"unknown_lan_device","id":x.id,"subject":x.mac or x.ip_address,"reason":"Device is outside the current trusted baseline; verify against DHCP/router inventory."}
            for x in hosts if not x.trusted
        ],
        "controls":["baseline SSID/BSSID","rogue AP correlation","unknown client review","DHCP/association correlation","evidence preservation","authorized wireless assessment"],
        "execution_boundary":"metadata and evidence workflows only; no credential capture, deauthentication, persistence, or disruption",
    }

def timeline(db: Session):
    events=[]
    for x in db.query(NetworkFlow).order_by(NetworkFlow.id.desc()).limit(50):
        events.append({"time":_iso(x.observed_at),"type":"network_flow","severity":"HIGH" if x.risk_score>=60 else "MEDIUM","actor":x.src_ip,"target":f"{x.dst_ip}:{x.dst_port}","risk":x.risk_score,"detail":f"{x.protocol} · {x.bytes_out} bytes · {x.action}"})
    for x in db.query(SessionEvent).order_by(SessionEvent.id.desc()).limit(50):
        events.append({"time":_iso(x.started_at),"type":"session","severity":"HIGH" if x.anomaly_score>=0.7 else "LOW","actor":x.username,"target":x.application,"risk":round(x.anomaly_score*100),"detail":f"{x.source_ip} · {x.auth_method} · {'privileged' if x.privileged else 'standard'}"})
    for x in db.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(50):
        events.append({"time":_iso(x.created_at),"type":"audit","severity":"INFO","actor":x.actor,"target":x.target,"risk":0,"detail":f"{x.action} · {x.outcome}"})
    events.sort(key=lambda x: x.get("time") or "", reverse=True)
    return events[:100]

def infrastructure(db: Session):
    return {
        "services":[{"host":s.asset_id,"port":s.port,"protocol":s.protocol,"service":s.service,"process":s.process,"pid":s.pid,"user":s.user,"expected":s.expected} for s in db.query(Service).limit(200)],
        "flows":[{"src":x.src_ip,"dst":x.dst_ip,"port":x.dst_port,"risk":x.risk_score,"action":x.action,"bytes_out":x.bytes_out} for x in db.query(NetworkFlow).order_by(NetworkFlow.risk_score.desc()).limit(100)],
        "identities":[{"username":x.username,"type":x.identity_type,"privilege":x.privilege,"mfa":x.mfa_enabled,"status":x.status} for x in db.query(Identity).order_by(Identity.privilege.desc()).limit(100)],
    }

def attribution(db: Session):
    unknown=[x for x in db.query(DiscoveredHost).limit(100) if not x.trusted]
    highflows=db.query(NetworkFlow).filter(NetworkFlow.risk_score>=70).order_by(NetworkFlow.risk_score.desc()).limit(20).all()
    hypotheses=[]
    if unknown:
        hypotheses.append({"id":"hyp-wireless-baseline","label":"Unauthorized device or unregistered asset","confidence":min(0.55+0.05*len(unknown),0.9),"supporting":[f"{len(unknown)} device(s) outside trusted baseline"],"contradicting":["Unknown status is not proof of compromise"],"next":"Validate against router/DHCP inventory and preserve association evidence."})
    if highflows:
        hypotheses.append({"id":"hyp-network-anomaly","label":"Potential lateral movement or unusual egress","confidence":0.62,"supporting":[f"{len(highflows)} high-risk flow(s)"],"contradicting":["Flow risk is heuristic and needs endpoint/process context"],"next":"Correlate flow with process, user, session and DNS telemetry."})
    if not hypotheses:
        hypotheses.append({"id":"hyp-none","label":"No active attribution hypothesis","confidence":0.0,"supporting":[],"contradicting":[],"next":"Continue collecting telemetry and maintain baselines."})
    return {"hypotheses":hypotheses,"disclaimer":"These are investigation hypotheses, not actor identification. External attribution requires corroborated evidence and appropriate legal/incident-response processes."}

def evidence_bundle(db: Session):
    return {
        "bundle_id":f"AX29-{int(datetime.now(timezone.utc).timestamp())}",
        "created_at":datetime.now(timezone.utc).isoformat(),
        "sources":["network_flows","sessions","services","identities","wifi_networks","discovered_hosts","threat_intel","audit_events"],
        "integrity":"Each evidence artifact should be hashed at collection time; immutable storage is recommended in production.",
        "chain_of_custody":["collection identity","timestamp","source","scope","SHA-256","storage location","access log"],
    }
