"""Central VEYRA help registry.

The UI can progressively move from scattered inline help to this machine-readable
registry. Content is defensive: it explains purpose, evidence, safe operation and
approval boundaries without providing offensive execution instructions.
"""
HELP = {
    "security_graph": {
        "title": "Security Graph",
        "purpose": "Connect assets, services, identities, sessions, flows, cloud resources and AI assets.",
        "questions": [
            "Which internet-facing assets can reach sensitive resources?",
            "Which identity is associated with a suspicious connection?",
            "Which process/user owns an exposed service?"
        ],
        "evidence": ["asset inventory", "service/process attribution", "identity/session telemetry", "network flows"],
    },
    "incident_response": {
        "title": "Incident Response",
        "purpose": "Preserve evidence, reconstruct timelines, enrich indicators and coordinate approved containment.",
        "workflow": ["preserve", "scope", "timeline", "enrich", "contain with approval", "eradicate", "verify"],
    },
    "forensics": {
        "title": "Forensics",
        "purpose": "Static triage of files, emails, PDFs, Office files, binaries and PCAPs.",
        "rule": "Samples are not executed by the API. Use isolated analyst tooling for deeper reverse engineering.",
    },
    "ai_security": {
        "title": "AI Security",
        "purpose": "Inventory and protect models, applications, agents, tools, memory, prompts, RAG and vector stores.",
        "controls": ["prompt-injection testing", "tool allowlists", "tenant-aware retrieval", "output validation",
                     "memory integrity", "model/tool provenance", "agent tracing", "human approval"],
    },
    "rag": {
        "title": "RAG Security",
        "purpose": "Ground analyst answers in authorized evidence instead of unrestricted model memory.",
        "pipeline": ["authorize", "hybrid retrieve", "rerank", "graph enrich", "generate", "cite", "audit"],
    },
    "tooling": {
        "title": "Security Tooling",
        "purpose": "Catalog and govern security tools used by authorized red/blue teams.",
        "rule": "VEYRA is the control plane; dangerous execution remains isolated and approval-gated.",
    },
}
