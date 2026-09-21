"""Curated 2026 AI/agent security tool extensions for AegisX.

Metadata only. AegisX never executes these tools from the SaaS API; execution is
performed by enrolled, isolated, policy-bound workers/connectors.
"""

AI_CUTTING_EDGE_2026 = [
    # LLM red teaming / evaluation
    ("pyrit", "PyRIT", "LLM Red Team", "Adversarial testing of generative AI systems", "approved_ai_worker"),
    ("deepteam", "DeepTeam", "LLM Red Team", "LLM and agent red-team test orchestration", "approved_ai_worker"),
    ("giskard", "Giskard", "LLM Evaluation", "LLM/ML security and quality evaluation", "approved_ai_worker"),
    ("deepeval", "DeepEval", "LLM Evaluation", "LLM evaluation and regression testing", "approved_ai_worker"),
    ("inspect-ai", "Inspect AI", "Agent Evaluation", "AI evaluation framework for controlled security benchmarks", "approved_ai_worker"),
    ("openai-evals", "OpenAI Evals", "LLM Evaluation", "Model evaluation and regression framework", "approved_ai_worker"),
    ("lm-evaluation-harness", "EleutherAI LM Evaluation Harness", "LLM Evaluation", "Standardized model evaluation harness", "approved_ai_worker"),
    ("helm", "HELM", "LLM Evaluation", "Holistic language-model evaluation and benchmarking", "approved_ai_worker"),
    ("agentdojo", "AgentDojo", "Agent Evaluation", "Controlled benchmark for agent/tool security behavior", "isolated_lab_only"),
    ("agentbench", "AgentBench", "Agent Evaluation", "Agent capability and safety benchmarking", "isolated_lab_only"),
    ("cyberseceval", "CyberSecEval", "AI Red Team", "Cybersecurity-focused model safety evaluation", "isolated_lab_only"),
    ("art", "Adversarial Robustness Toolbox", "Adversarial ML", "Adversarial ML testing and defenses", "isolated_analysis_worker"),
    ("textattack", "TextAttack", "Adversarial ML", "Adversarial NLP robustness testing", "isolated_analysis_worker"),
    ("foolbox", "Foolbox", "Adversarial ML", "Adversarial robustness evaluation", "isolated_analysis_worker"),
    ("robustbench", "RobustBench", "Adversarial ML", "Robustness benchmarking and reference models", "isolated_analysis_worker"),
    ("trojai", "TrojAI", "Model Security", "Trojan/backdoor model research and evaluation", "isolated_analysis_worker"),
    ("counterfit", "Counterfit", "Adversarial ML", "Adversarial ML assessment framework", "isolated_analysis_worker"),
    # Model / artifact security
    ("modelscan", "Protect AI ModelScan", "Model Security", "Scan ML model artifacts for unsafe components", "isolated_analysis_worker"),
    ("fickling", "Fickling", "Model Security", "Analyze Python pickle artifacts for unsafe behavior", "isolated_analysis_worker"),
    ("picklescan", "PickleScan", "Model Security", "Scan pickle-based ML artifacts for unsafe payloads", "isolated_analysis_worker"),
    ("garak", "Garak", "LLM Red Team", "LLM vulnerability probing and adversarial testing", "approved_ai_worker"),
    # Agent / MCP / A2A
    ("mcp-inspector", "MCP Inspector", "MCP Security", "Inspect and test MCP servers and tool interfaces", "isolated_lab_only"),
    ("mcp-scanner", "MCP Security Scanner", "MCP Security", "Inventory and assess MCP server/tool configurations", "approved_ai_worker"),
    ("invariant", "Invariant", "Agent Security", "Runtime security and policy analysis for AI agents", "approved_ai_worker"),
    ("agent-security-initiative-samples", "OWASP Agentic Security Initiative Samples", "Agent Security", "Controlled vulnerable-agent security training corpus", "isolated_lab_only"),
    ("agentic-skills-top10", "OWASP Agentic Skills Top 10", "Agent Security", "Risk taxonomy and assessment guidance for agent skills", "approved_ai_worker"),
    ("cyberagents-exchange-inspector", "CyberAgents Exchange AI Inspector", "Agent Security", "Security review integration for community AI components", "approved_connector"),
    ("a2a-security-tests", "A2A Security Test Suite", "A2A Security", "Controlled testing of agent-to-agent identity and message trust", "isolated_lab_only"),
    # Guardrails / gateways / policy
    ("llama-firewall", "LlamaFirewall", "AI Gateway", "Runtime guardrails and policy enforcement for LLM applications", "approved_ai_worker"),
    ("llama-guard", "Llama Guard", "AI Gateway", "Content safety classification and policy enforcement", "approved_ai_worker"),
    ("nemo-guardrails", "NVIDIA NeMo Guardrails", "AI Gateway", "Programmable guardrails for conversational and agentic systems", "approved_ai_worker"),
    ("guardrails-ai", "Guardrails AI", "AI Gateway", "Validation and safety guardrail framework", "approved_ai_worker"),
    ("litellm", "LiteLLM", "AI Gateway", "Model gateway, routing and centralized policy point", "approved_ai_worker"),
    ("portkey", "Portkey", "AI Gateway", "AI gateway observability, guardrails and routing integration", "approved_connector"),
    ("lakera-guard", "Lakera Guard", "Prompt Injection", "Prompt/data security and threat detection integration", "approved_connector"),
    ("neuraltrust", "NeuralTrust", "AI Security", "AI security posture and runtime controls integration", "approved_connector"),
    # Observability / tracing
    ("opentelemetry-genai", "OpenTelemetry GenAI", "AI Observability", "Standardized traces and telemetry for model/agent operations", "approved_connector"),
    ("langfuse", "Langfuse", "AI Observability", "LLM/agent tracing, evaluation and cost telemetry", "approved_connector"),
    ("phoenix-arize", "Arize Phoenix", "AI Observability", "LLM tracing, evaluation and observability", "approved_connector"),
    ("traceloop", "Traceloop", "AI Observability", "OpenTelemetry-based LLM observability", "approved_connector"),
    ("mlflow", "MLflow", "ML Lifecycle", "Model lifecycle, registry and evaluation integration", "approved_connector"),
    ("weave", "Weights & Biases Weave", "AI Observability", "LLM application tracing and evaluation", "approved_connector"),
    ("braintrust", "Braintrust", "AI Evaluation", "LLM/agent evaluation and monitoring integration", "approved_connector"),
    ("langsmith", "LangSmith", "AI Observability", "LLM/agent tracing and evaluation integration", "approved_connector"),
    # RAG / data / evaluation
    ("ragas", "Ragas", "RAG Security", "RAG evaluation and retrieval-quality regression", "approved_ai_worker"),
    ("trulens", "TruLens", "RAG Security", "LLM and RAG evaluation and feedback functions", "approved_ai_worker"),
    ("llamaindex", "LlamaIndex", "RAG Security", "RAG/agent application integration and evaluation", "approved_ai_worker"),
    ("haystack", "Haystack", "RAG Security", "RAG and agent pipeline evaluation integration", "approved_ai_worker"),
    ("qdrant", "Qdrant", "Vector DB Security", "Vector database integration and security testing", "approved_connector"),
    ("milvus", "Milvus", "Vector DB Security", "Vector database integration and security testing", "approved_connector"),
    ("weaviate", "Weaviate", "Vector DB Security", "Vector database integration and security testing", "approved_connector"),
    ("chroma", "Chroma", "Vector DB Security", "Vector store integration and retrieval security testing", "approved_connector"),
    # Supply chain / provenance
    ("syft-ai", "Syft AI/SBOM", "AI Supply Chain", "AI artifact and dependency inventory integration", "approved_worker"),
    ("cosign-ai", "Cosign/Sigstore", "AI Supply Chain", "Artifact signing and provenance verification", "approved_worker"),
    ("slsa-ai", "SLSA", "AI Supply Chain", "Supply-chain provenance and build integrity controls", "approved_worker"),
    ("in-toto-ai", "in-toto", "AI Supply Chain", "Artifact provenance and supply-chain attestations", "approved_worker"),
    ("osv-scanner-ai", "OSV-Scanner", "AI Supply Chain", "Dependency vulnerability scanning for AI applications", "approved_worker"),
    ("gitleaks-ai", "Gitleaks", "AI Secrets", "Secret detection in AI/application repositories", "approved_worker"),
    # AI governance / security posture
    ("nist-ai-rmf", "NIST AI RMF", "AI Governance", "AI risk-management control mapping", "approved_connector"),
    ("mitre-atlas", "MITRE ATLAS", "AI Threat Intelligence", "AI adversary technique mapping and threat intelligence", "approved_connector"),
    # 2026 security-platform / runtime / supply-chain additions
    ("kyverno", "Kyverno", "Kubernetes Governance", "Kubernetes-native policy, validation, mutation and image verification", "approved_worker"),
    ("inspektor-gadget", "Inspektor Gadget", "Kubernetes", "eBPF-based Kubernetes and Linux runtime observability and inspection", "approved_worker"),
    ("prempti", "Prempti", "Agent Security", "Experimental runtime visibility and policy for AI-agent tool-call activity", "experimental_worker"),
    ("open-policy-agent", "Open Policy Agent", "Policy as Code", "General-purpose policy decision and authorization engine", "approved_worker"),
    ("tuf", "The Update Framework", "Software Supply Chain", "Secure software update framework with threshold trust and rollback protection", "approved_worker"),
    ("openssf-scorecard", "OpenSSF Scorecard", "Software Supply Chain", "Automated open-source project security health assessment", "approved_worker"),
    ("guac", "GUAC", "Software Supply Chain", "Graph-based aggregation and querying of software supply-chain evidence", "approved_worker"),
    ("mcp-shield-runtime", "MCP Shield Runtime", "MCP Security", "Runtime MCP gateway with parameter policies, approvals, secret redaction and audit", "experimental_worker"),
    ("pipelock", "Pipelock", "AI Network Security", "AI-agent egress firewall for MCP, A2A and mediated network traffic", "experimental_worker"),
    ("adrian-agent-security", "Adrian Agent Security", "Agent Security", "Runtime monitoring and intervention for AI-agent actions and tool calls", "experimental_worker"),
    ("sint-protocol", "SINT Protocol", "Agent Governance", "Open runtime authority and evidence protocol for consequential agent actions", "experimental_connector"),
]

def registry():
    out=[]
    for tid,name,cat,purpose,worker in AI_CUTTING_EDGE_2026:
        out.append({
            "id": tid, "name": name, "category": cat, "purpose": purpose,
            "execution_profile": worker, "admin_only": True, "access_tier": "admin",
            "privileged_usage": worker in {"isolated_lab_only","isolated_analysis_worker"},
            "browser_shell": False, "status": "cataloged", "source": "aegisx-ai-cutting-edge-2026",
            "help": {
                "summary": purpose,
                "safe_workflow": "Define an approved AI asset/test scope, run the evaluation or inspection on a managed worker or approved connector, review evidence, then map findings to AegisX controls.",
                "evidence": ["asset/model/agent identifier", "test or inspection context", "policy decision", "trace ID", "artifact hash", "timestamp"],
                "common_mistakes": ["Testing production secrets or unapproved models", "Treating one benchmark as proof of security", "Failing to preserve model/tool/config versions"],
                "next_step": "Correlate findings with AegisX AI Security, Security Graph, OWASP, NIST AI RMF and MITRE ATLAS controls.",
                "help_boundary": "Defensive/authorized testing only; no credential theft, payload delivery, persistence, C2, evasion or hack-back instructions."
            }
        })
    return out
