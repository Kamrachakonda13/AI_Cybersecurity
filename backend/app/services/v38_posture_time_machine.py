"""VEYRA v3.8 — Security Posture Time Machine + AI/Endpoint Exposure Intelligence.

Design law: deterministic telemetry and evidence are authoritative. AI may rank,
summarize and propose hypotheses, but never writes policy or executes remediation.
"""
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from uuid import uuid4
from ..models import Asset, Device, Finding, Identity, CloudResource, AIAsset, PostureSnapshot, PostureChange, CveRecord, AgentRuntimeEvent

AI_PROVIDER_RADAR = [
 {"id":"openai-gpt6-astra","provider":"OpenAI","release":"GPT-6 Astra","status":"current","security_signal":"Critical cyber capability threshold; requires sandboxing, scoped permissions, monitoring and human review.","maps_to":["agent runtime","cyber capability","evaluation","sandbox"]},
 {"id":"anthropic-fable-mythos-51","provider":"Anthropic","release":"Claude Fable 5.1 / Mythos 5.1","status":"current","security_signal":"Frontier coding/knowledge-work models plus documented cyber evaluation incidents make runtime isolation and trace review first-class controls.","maps_to":["agent runtime","alignment","trajectory monitoring","cyber evaluation"]},
 {"id":"google-gemini-35","provider":"Google","release":"Gemini 3.5","status":"current","security_signal":"Agentic action and multimodal workflows increase tool, data and identity boundary requirements.","maps_to":["agentic AI","multimodal","tool authorization"]},
 {"id":"apple-foundation-models","provider":"Apple","release":"Apple Foundation Models / macOS 27","status":"current-rc","security_signal":"On-device Foundation Models, Vision/OCR tools, Dynamic Profiles and Private Cloud Compute require local model inventory, model/tool provenance and privacy-boundary telemetry.","maps_to":["on-device AI","macOS","privacy","tool invocation"]},
 {"id":"microsoft-agent365","provider":"Microsoft","release":"Agent 365","status":"current","security_signal":"Agent registry, observability, identity and real-time protection should be correlated with Entra identities and Windows/macOS endpoint posture.","maps_to":["agent registry","identity","observability","endpoint"]},
 {"id":"aws-agentcore","provider":"AWS","release":"Bedrock AgentCore","status":"current","security_signal":"Identity consent and multi-framework evaluations create a useful control point for agent authorization and evidence.","maps_to":["agent identity","consent","evaluation","AWS"]},
 {"id":"linux-aaif","provider":"Linux Foundation","release":"AAIF / A2A / agentgateway / DNS-AID / ANS","status":"emerging","security_signal":"Open agent interoperability makes identity, discovery, gateway policy and signed provenance cross-vendor control points.","maps_to":["A2A","MCP","agent identity","gateway","discovery"]},
]

ENDPOINT_RELEASES = [
 {"platform":"Windows","release":"Windows 11 v26H1/v25H2/v24H2/v23H2","status":"security-update-current","source":"Microsoft September 2026 Security Update","signal":"September 8, 2026 update includes Critical RCE exposure in supported Windows families; continuously verify patch/build state."},
 {"platform":"macOS","release":"macOS 27.0 RC","status":"release-candidate","source":"Apple Developer releases, Sep 9 2026","signal":"Apple-silicon-only direction and new Foundation Models/AI stack require endpoint inventory, architecture, model/tool and software provenance checks."},
 {"platform":"Linux","release":"Ubuntu 26.04 / 24.04 LTS and supported variants","status":"security-advisories-active","source":"Ubuntu Security Notices","signal":"September advisories include kernel, glibc, Flatpak, FFmpeg, curl and other package vulnerabilities; map installed package state to advisories and KEV where applicable."},
]

CONTROL_SIGNALS = [
 ("agent-runtime","Agent runtime","OWASP Agent Control Standard / NIST CSF Govern+Detect"),
 ("endpoint-patch","Endpoint patch posture","NIST CSF ID/PR/DE; vendor security advisories"),
 ("ai-provider","AI provider governance","OWASP GenAI / AI RMF / provider safety controls"),
 ("agent-identity","Agent identity","Microsoft Agent 365 / Linux Foundation ANS concepts / least privilege"),
 ("model-provenance","Model and tool provenance","SLSA / Sigstore / TUF / SBOM-AIBOM"),
]

def _counts(db):
 return {"assets":db.query(Asset).count(),"devices":db.query(Device).count(),"findings":db.query(Finding).count(),"identities":db.query(Identity).count(),"cloud":db.query(CloudResource).count(),"ai_assets":db.query(AIAsset).count(),"cves":db.query(CveRecord).count(),"agent_events":db.query(AgentRuntimeEvent).count()}

def _posture_score(db):
 f=db.query(Finding).all(); total=max(1,len(f)); risk=sum(float(x.risk_score or 0) for x in f)/total
 critical=sum(1 for x in f if str(x.severity).upper()=="CRITICAL" or x.kev)
 return max(0,round(100-min(100,risk*0.72+critical*7),1)), round(min(100,risk),1)

def _inventory(db):
 return {"counts":_counts(db),"platforms":ENDPOINT_RELEASES,"ai_provider_radar":AI_PROVIDER_RADAR}

def _hash(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,default=str).encode()).hexdigest()

def create_snapshot(db, scope="tenant"):
 posture,risk=_posture_score(db); inv=_inventory(db); sid="ps_"+uuid4().hex[:20]
 digest=_hash({"scope":scope,"posture":posture,"risk":risk,"inventory":inv})
 row=PostureSnapshot(snapshot_id=sid,scope=scope,posture_score=posture,risk_score=risk,inventory_json=json.dumps(inv),hash_sha256=digest)
 db.add(row); db.commit(); db.refresh(row)
 return {"snapshot_id":sid,"posture_score":posture,"risk_score":risk,"hash_sha256":digest,"captured_at":row.captured_at.isoformat()}

def current(db):
 row=db.query(PostureSnapshot).order_by(PostureSnapshot.captured_at.desc()).first()
 posture,risk=_posture_score(db)
 return {"release":"3.8","generated_at":datetime.now(timezone.utc).isoformat(),"current":{"posture_score":posture,"risk_score":risk,"latest_snapshot":row.snapshot_id if row else None},"inventory":_inventory(db),"controls":[{"id":i,"name":n,"reference":r} for i,n,r in CONTROL_SIGNALS]}

def history(db, limit=30):
 rows=db.query(PostureSnapshot).order_by(PostureSnapshot.captured_at.desc()).limit(min(max(limit,1),100)).all()
 return {"snapshots":[{"snapshot_id":r.snapshot_id,"posture_score":r.posture_score,"risk_score":r.risk_score,"hash_sha256":r.hash_sha256,"captured_at":r.captured_at.isoformat()} for r in rows]}

def changes(db, before=None, after=None):
 rows=db.query(PostureChange).order_by(PostureChange.created_at.desc()).limit(100).all()
 return {"changes":[{"change_id":r.change_id,"before":r.snapshot_before,"after":r.snapshot_after,"category":r.category,"target":r.target,"change_type":r.change_type,"severity":r.severity,"summary":r.summary,"evidence":json.loads(r.evidence_json or "[]"),"created_at":r.created_at.isoformat()} for r in rows]}

def compare_latest(db):
 rows=db.query(PostureSnapshot).order_by(PostureSnapshot.captured_at.desc()).limit(2).all()
 if len(rows)<2: return {"status":"insufficient_history","message":"Capture at least two posture snapshots to compute deterministic before/after changes.","changes":[]}
 a,b=rows[1],rows[0]; ai=json.loads(a.inventory_json or "{}"); bi=json.loads(b.inventory_json or "{}"); out=[]
 for k in ("counts",):
  for field in set(ai.get(k,{}))|set(bi.get(k,{})):
   av=ai.get(k,{}).get(field,0); bv=bi.get(k,{}).get(field,0)
   if av!=bv: out.append({"category":"inventory","target":field,"change_type":"increased" if bv>av else "decreased","severity":"MEDIUM","summary":f"{field}: {av} → {bv}","evidence":[a.snapshot_id,b.snapshot_id]})
 if a.posture_score!=b.posture_score: out.append({"category":"posture","target":"tenant","change_type":"improved" if b.posture_score>a.posture_score else "degraded","severity":"HIGH" if b.posture_score<a.posture_score else "INFO","summary":f"Posture score: {a.posture_score} → {b.posture_score}","evidence":[a.hash_sha256,b.hash_sha256]})
 for x in out:
  cid="pc_"+uuid4().hex[:20]
  db.add(PostureChange(change_id=cid,snapshot_before=a.snapshot_id,snapshot_after=b.snapshot_id,category=x["category"],target=x["target"],change_type=x["change_type"],severity=x["severity"],summary=x["summary"],evidence_json=json.dumps(x["evidence"])))
 db.commit()
 return {"status":"ok","before":a.snapshot_id,"after":b.snapshot_id,"changes":out}

def remediation_proof(db):
 findings=db.query(Finding).order_by(Finding.risk_score.desc()).limit(100).all(); return {"proofs":[{"finding_id":f.id,"title":f.title,"status":f.status,"risk_score":f.risk_score,"proof_state":"verified_closed" if str(f.status).lower() in ("closed","resolved","remediated") else "verification_required","verification_basis":"Finding lifecycle state; pair with worker evidence receipt for production proof."} for f in findings]}

def drift(db):
 c=compare_latest(db); return {"release":"3.8","drift":c}
