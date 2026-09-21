"""VEYRA v5.0 AI Applications Layer.

Six portfolio-grade, security-governed POC applications share deterministic
RAG, evidence, evaluation, graph and agent-control primitives. Demo adapters
are intentionally offline/curated; production connectors are explicit seams.
No arbitrary shell, offensive execution, credential attacks or destructive
response is exposed here.
"""
from __future__ import annotations
import hashlib, json, re, time, uuid
from typing import Any


def _sha(x: Any) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

CORPUS = [
 {"id":"soc-001","title":"Suspicious PowerShell execution","type":"incident","text":"Multiple failed logins were followed by a successful authentication and suspicious PowerShell execution. Investigate identity, endpoint and process telemetry; preserve evidence before containment.","tags":["siem","incident","powershell","identity"]},
 {"id":"soc-002","title":"MITRE ATT&CK Command and Scripting Interpreter","type":"mitre","text":"PowerShell activity maps to MITRE ATT&CK Command and Scripting Interpreter: PowerShell. Correlate parent process, user, host, command lineage and network destinations.","tags":["mitre","powershell","attack"]},
 {"id":"soc-003","title":"CISA KEV prioritization guidance","type":"threat-intel","text":"Known exploited vulnerabilities should receive accelerated remediation priority when applicable to an organization's exposed assets and software inventory.","tags":["kev","vulnerability","remediation"]},
 {"id":"vuln-001","title":"CVE-2025-0001 example asset finding","type":"cve","text":"Example vulnerability record for the demo corpus. Severity is high; exploitability, exposure, asset criticality and known exploitation should determine priority.","tags":["cve","cvss","risk"]},
 {"id":"vuln-002","title":"Internet-facing critical service","type":"asset","text":"Production payment service is internet-facing, business critical and contains sensitive data. A high-severity vulnerability on this asset has elevated business impact.","tags":["asset","criticality","exposure"]},
 {"id":"ent-001","title":"Quarterly customer churn","type":"business","text":"Demo metric: customer churn increased from 4.1% to 5.6% quarter over quarter. Product usage declined 8% among the affected cohort while support contacts increased 13%.","tags":["churn","metrics","customer"]},
 {"id":"ent-002","title":"Customer success analysis","type":"business","text":"The affected customer cohort has longer resolution times and lower feature adoption. The evidence suggests service friction and adoption gaps are correlated with the churn increase.","tags":["churn","support","adoption"]},
 {"id":"research-001","title":"Agent security research brief","type":"research","text":"Agent security increasingly emphasizes identity, delegated authority, tool governance, runtime observability, trajectory assurance and continuous validation.","tags":["agent","security","research"]},
]

SAMPLE_INCIDENT = [
 {"ts":"10:01","event":"failed_login","user":"alice","host":"WIN-042","src":"10.10.4.22"},
 {"ts":"10:03","event":"failed_login","user":"alice","host":"WIN-042","src":"10.10.4.22"},
 {"ts":"10:05","event":"successful_login","user":"alice","host":"WIN-042","src":"10.10.4.22"},
 {"ts":"10:07","event":"powershell","user":"alice","host":"WIN-042","process":"powershell.exe"},
 {"ts":"10:09","event":"network_connection","user":"alice","host":"WIN-042","dst":"203.0.113.20:443"},
]


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_./:-]{3,}", (s or "").lower()))


def hybrid_retrieve(query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]:
    q = _tokens(query); filters = filters or {}; scored=[]
    for d in CORPUS:
        if filters.get("type") and d["type"] != filters["type"]: continue
        dt = _tokens(d["text"] + " " + d["title"] + " " + " ".join(d["tags"]))
        lexical = len(q & dt) / max(1, len(q))
        tag = len(q & set(d["tags"])) / max(1, len(q))
        score = round(0.7*lexical + 0.3*tag, 4)
        if score: scored.append((score,d))
    scored.sort(key=lambda x:x[0], reverse=True)
    return [{"id":d["id"],"title":d["title"],"type":d["type"],"score":s,"text":d["text"],"citation":f"[{d['id']}]"} for s,d in scored[:top_k]]


def cybsoc_rag(query: str) -> dict:
    t=time.perf_counter(); hits=hybrid_retrieve(query,5)
    mitre=[h for h in hits if h["type"]=="mitre"]
    answer=(f"Investigation focuses on {query}. Evidence indicates correlation across identity, endpoint/process and network telemetry. "
            + ("PowerShell activity maps to MITRE ATT&CK Command and Scripting Interpreter. " if mitre else "")
            + "Preserve evidence, validate scope, assess blast radius and require approval before high-risk containment.")
    return {"application":"cybsoc_rag","answer":answer,"retrieval":hits,"citations":[h["citation"] for h in hits],"grounded":bool(hits),"latency_ms":round((time.perf_counter()-t)*1000,2)}


def vulnerability_rag(query: str = "Which vulnerabilities should we patch first and why?") -> dict:
    assets=[
      {"asset":"payment-api","cve":"CVE-2025-0001","cvss":9.1,"kev":True,"exposed":True,"criticality":5,"data":"restricted"},
      {"asset":"internal-worker","cve":"CVE-2025-0002","cvss":8.2,"kev":False,"exposed":False,"criticality":3,"data":"internal"},
      {"asset":"dev-host","cve":"CVE-2025-0003","cvss":7.5,"kev":False,"exposed":False,"criticality":2,"data":"internal"},
    ]
    for a in assets:
        a["risk_score"] = min(100, round(a["cvss"]*5 + (15 if a["exposed"] else 0) + (20 if a["kev"] else 0) + a["criticality"]*5 + (10 if a["data"]=="restricted" else 0),1))
        a["reason"] = "; ".join(filter(None,["CISA KEV" if a["kev"] else "","internet-facing" if a["exposed"] else "",f"CVSS {a['cvss']}",f"criticality P{a['criticality']}"]))
    assets.sort(key=lambda x:x["risk_score"], reverse=True)
    hits=hybrid_retrieve("vulnerability CVE asset KEV exposure remediation",5)
    return {"application":"vulnerability_intelligence_rag","query":query,"priority_queue":assets,"retrieval":hits,"citations":[h["citation"] for h in hits]}


def autonomous_research(query: str) -> dict:
    stages=["planner","search_agent","retrieval_agent","analyst","fact_checker","critic","report_generator"]
    hits=hybrid_retrieve(query,5, {"type":"research"}) or hybrid_retrieve("agent security research",5)
    findings=[h["text"] for h in hits]
    report=(f"Executive research report for: {query}\n\n" + " ".join(findings) + "\n\nSources are evidence-linked demo records; production deployments should use approved search/retrieval connectors and independent source validation.")
    return {"application":"autonomous_research_agent","stages":stages,"query":query,"findings":findings,"citations":[h["citation"] for h in hits],"fact_check":{"status":"pass" if hits else "fail","checked_claims":len(findings)},"critic":{"status":"pass","issues":[]},"report":report,"cost_usd":0.0,"latency_ms":1.0}


def incident_response(events: list[dict] | None = None) -> dict:
    events=events or SAMPLE_INCIDENT
    failed=sum(1 for e in events if e.get("event")=="failed_login")
    successful=any(e.get("event")=="successful_login" for e in events)
    powershell=any(e.get("event")=="powershell" for e in events)
    network=any(e.get("event")=="network_connection" for e in events)
    risk=min(100, 25*bool(failed>=2)+25*successful+25*powershell+15*network)
    hits=hybrid_retrieve("failed login successful authentication PowerShell suspicious network MITRE",5)
    return {"application":"agentic_incident_response","timeline":events,"attack_stage":"credential_access → execution → possible command-and-control" if powershell else "initial_access_investigation","risk_score":risk,"mitre":["T1059.001 PowerShell"] if powershell else [],"evidence":hits,"recommendations":["preserve endpoint and identity evidence","review authentication source and session","validate process lineage and destination","stage containment for human approval"],"approval_required":True,"containment_executed":False}


def enterprise_decision(question: str) -> dict:
    hits=hybrid_retrieve(question,5)
    if "churn" in question.lower():
        answer="Churn increased from 4.1% to 5.6%. The strongest correlated factors in the demo evidence are an 8% usage decline in the affected cohort, 13% more support contacts, longer resolution times and lower feature adoption. The evidence supports prioritizing adoption and service-friction analysis rather than asserting a single causal factor."
    else:
        answer="VEYRA combined document retrieval and structured evidence to produce a cited decision. Production adapters can add SQL, APIs and knowledge-graph queries behind the same governed router."
    return {"application":"enterprise_ai_decision_platform","question":question,"answer":answer,"evidence":hits,"citations":[h["citation"] for h in hits],"grounded":bool(hits),"sources_used":["RAG"]}


def evaluate_ai() -> dict:
    metrics={
      "rag_pipeline_a":{"context_precision":0.91,"context_recall":0.88,"faithfulness":0.94,"answer_relevance":0.92,"citation_correctness":0.96},
      "rag_pipeline_b":{"context_precision":0.84,"context_recall":0.93,"faithfulness":0.89,"answer_relevance":0.90,"citation_correctness":0.91},
      "agent_pipeline_a":{"tool_selection":0.95,"tool_call_correctness":0.94,"task_completion":0.91,"planning_quality":0.88,"recovery":0.86},
      "model_comparison":{"gpt":{"quality":0.93,"latency_ms":720,"cost_per_1k_tokens":0.004},"claude":{"quality":0.92,"latency_ms":810,"cost_per_1k_tokens":0.0045},"gemini":{"quality":0.90,"latency_ms":650,"cost_per_1k_tokens":0.0025},"open_model":{"quality":0.86,"latency_ms":540,"cost_per_1k_tokens":0.0008}},
    }
    return {"application":"llm_evaluation_reliability","dataset":"VEYRA-demo-eval-v1","metrics":metrics,"release_gate":{"minimum_faithfulness":0.90,"minimum_task_completion":0.85,"decision":"pass"},"note":"Demo benchmark values are deterministic fixtures; replace with measured evaluation runs in production."}


def catalog() -> list[dict]:
    return [
      {"id":"cybsoc_rag","name":"CyberSOC RAG — AI Security Analyst","category":"RAG + Cybersecurity","description":"Hybrid evidence retrieval, citations, threat correlation, MITRE mapping and grounded investigation."},
      {"id":"vulnerability_intelligence_rag","name":"Vulnerability Intelligence RAG","category":"RAG + Cybersecurity","description":"Risk-aware CVE/asset/KEV/SBOM prioritization and remediation reasoning."},
      {"id":"autonomous_research_agent","name":"Autonomous Research Agent","category":"Agentic AI","description":"Planner → search → retrieval → analysis → fact-check → critic → report workflow."},
      {"id":"agentic_incident_response","name":"Agentic Cybersecurity Incident Response","category":"Agentic AI + Cybersecurity","description":"Evidence-driven investigation, MITRE mapping, risk and approval-gated response."},
      {"id":"enterprise_ai_decision_platform","name":"Enterprise AI Knowledge & Decision Platform","category":"AI / GenAI","description":"Governed router pattern combining RAG, structured evidence, APIs/SQL seams and knowledge graph."},
      {"id":"llm_evaluation_reliability","name":"LLM Evaluation & AI Reliability Platform","category":"AI / GenAI","description":"RAG, agent and model evaluation with quality, safety, cost and latency release gates."},
    ]
