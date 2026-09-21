"""VEYRA cutting-edge AI security ecosystem catalog.

This is metadata and governance only. It does not install packages or execute tools.
Each entry describes a security capability VEYRA can expose through a managed worker.
The catalog deliberately includes both open-source and commercial/connector candidates;
availability and licensing are verified by the worker/marketplace before installation.
"""
from __future__ import annotations

AI_TOOLS = [
    # LLM / GenAI red-team & evaluation
    ("garak", "LLM Red Team", "LLM vulnerability scanner and probe framework"),
    ("promptfoo", "LLM Evaluation", "Prompt/model evaluation, red teaming and regression testing"),
    ("pyrit", "LLM Red Team", "Microsoft framework for AI red-team automation"),
    ("inspect-ai", "LLM Evaluation", "Evaluation framework for controlled AI safety/security tasks"),
    ("inspect-evals", "LLM Evaluation", "Reusable Inspect evaluation suites"),
    ("deepteam", "LLM Red Team", "LLM security and vulnerability testing framework"),
    ("giskard", "LLM Evaluation", "AI/ML model testing and security evaluation"),
    ("deepeval", "LLM Evaluation", "LLM evaluation and testing framework"),
    ("openai-evals", "LLM Evaluation", "Evaluation framework for model behavior"),
    ("lm-eval-harness", "LLM Evaluation", "Large-language-model evaluation harness"),
    ("helm", "LLM Evaluation", "Holistic language model evaluation"),
    ("tango-bench", "Agent Evaluation", "Agent/tool-use benchmark integration candidate"),
    ("agentdojo", "Agent Red Team", "Controlled benchmark for prompt-injection and agent security"),
    ("agentbench", "Agent Evaluation", "Agent capability/security benchmark integration candidate"),
    ("cyberseceval", "AI Cybersecurity", "AI cybersecurity capability evaluation"),
    ("llm-guard", "AI Gateway", "Input/output scanners for LLM applications"),
    ("rebuff", "Prompt Injection", "Prompt-injection detection integration candidate"),
    ("rebuffai", "Prompt Injection", "Prompt-injection detection integration candidate"),
    ("protectai-modelscan", "AI Supply Chain", "Scan ML model files for unsafe code/components"),
    ("fickling", "AI Supply Chain", "Python pickle security analysis"),
    ("modelscan", "AI Supply Chain", "ML model artifact security scanner"),
    ("picklescan", "AI Supply Chain", "Pickle/model artifact security scanning"),
    ("art", "Adversarial ML", "Adversarial Robustness Toolbox"),
    ("textattack", "Adversarial ML", "NLP adversarial testing framework"),
    ("foolbox", "Adversarial ML", "Adversarial attack/robustness evaluation library"),
    ("cleverhans", "Adversarial ML", "Adversarial machine-learning research framework"),
    ("robustbench", "Adversarial ML", "Robustness benchmark integration candidate"),
    ("trojanvision", "Model Security", "Neural network backdoor/trojan research toolkit"),
    ("trojai", "Model Security", "ML model security research and trojan detection"),
    ("counterfit", "Adversarial ML", "Microsoft AI security assessment toolkit"),
    # Agent / MCP / A2A
    ("mcp-scanner", "MCP Security", "MCP server/tool security scanning integration"),
    ("mcp-inspector", "MCP Security", "MCP server inspection and debugging"),
    ("mcp-security", "MCP Security", "MCP policy, tool and transport security integration"),
    ("mcp-guardian", "MCP Security", "MCP runtime governance integration candidate"),
    ("mcp-proxy", "MCP Security", "Policy enforcement/proxy integration for MCP traffic"),
    ("mcp-audit", "MCP Security", "MCP configuration and audit integration candidate"),
    ("a2a-security", "A2A Security", "Agent-to-agent identity and authorization assessment"),
    ("agentic-security", "Agent Security", "Agent identity, tool authorization and runtime policy checks"),
    ("invariant", "Agent Security", "Invariant-style policy/runtime verification integration"),
    ("nemo-guardrails", "AI Guardrails", "Programmable LLM interaction guardrails"),
    ("guardrails-ai", "AI Guardrails", "Validation and guardrail framework"),
    ("llm-firewall", "AI Gateway", "LLM request/response policy enforcement integration"),
    ("lakera-guard", "AI Gateway", "Enterprise prompt/data security connector"),
    ("hiddenlayer", "AI Security", "AI model/runtime security connector"),
    ("robust-intelligence", "AI Security", "AI security platform connector"),
    ("calypsoai", "AI Security", "AI security/governance connector"),
    ("neuraltrust", "AI Security", "LLM/agent security and governance connector"),
    # AI observability / tracing
    ("langfuse", "AI Observability", "LLM/agent tracing, evaluation and cost telemetry"),
    ("phoenix-arize", "AI Observability", "LLM/agent observability and evaluation"),
    ("opentelemetry-genai", "AI Observability", "OpenTelemetry GenAI semantic telemetry integration"),
    ("traceloop", "AI Observability", "OpenTelemetry-based LLM observability"),
    ("mlflow", "ML Lifecycle", "Model lifecycle, registry and experiment governance"),
    ("wandb", "ML Lifecycle", "ML experiment/model governance connector"),
    ("weave", "AI Observability", "LLM evaluation and tracing connector"),
    ("helicone", "AI Observability", "LLM gateway observability connector"),
    ("litellm", "AI Gateway", "Multi-provider LLM gateway and policy integration"),
    ("portkey", "AI Gateway", "Enterprise AI gateway and guardrail connector"),
    ("braintrust", "AI Evaluation", "LLM evaluation and tracing connector"),
    ("langsmith", "AI Observability", "LLM/agent tracing and evaluation connector"),
    # RAG / data security
    ("ragas", "RAG Security", "RAG evaluation and groundedness testing"),
    ("deepeval-rag", "RAG Security", "RAG metrics/evaluation integration"),
    ("trulens", "RAG Security", "LLM/RAG evaluation and feedback"),
    ("llamaindex", "RAG Security", "RAG/application framework integration"),
    ("haystack", "RAG Security", "RAG pipeline security/evaluation integration"),
    ("nemo-retriever", "RAG Security", "Retrieval security integration candidate"),
    ("vectordbbench", "Vector DB Security", "Vector database performance/security test harness"),
    ("pgvector", "Vector DB", "PostgreSQL vector storage integration"),
    ("qdrant", "Vector DB", "Vector database security connector"),
    ("milvus", "Vector DB", "Vector database security connector"),
    ("weaviate", "Vector DB", "Vector database security connector"),
    ("chromadb", "Vector DB", "Vector database security connector"),
    ("pinecone", "Vector DB", "Managed vector database security connector"),
    # ML / data / supply chain
    ("datasheets", "AI Governance", "Dataset/data-card governance integration"),
    ("dvc", "AI Supply Chain", "Dataset/model versioning and provenance"),
    ("lakefs", "AI Data Security", "Data versioning and lineage connector"),
    ("syft-ml", "AI SBOM", "AI/ML artifact SBOM integration"),
    ("grype-ml", "AI Supply Chain", "AI artifact vulnerability scanning integration"),
    ("cosign-ml", "AI Supply Chain", "Signed AI artifact provenance integration"),
    ("in-toto", "AI Supply Chain", "Software/AI supply-chain attestations"),
    ("slsa", "AI Supply Chain", "SLSA provenance and build integrity"),
    ("sigstore", "AI Supply Chain", "Keyless artifact signing and verification"),
    ("osv-scanner", "AI Supply Chain", "Dependency vulnerability scanning"),
    ("depscan", "AI Supply Chain", "Dependency/SBOM vulnerability analysis"),
    ("semgrep-ai", "AI AppSec", "AI-assisted static analysis integration"),
    ("codeql-ai", "AI AppSec", "CodeQL security analysis integration"),
    ("snyk-ai", "AI AppSec", "AI/application dependency security connector"),
    ("github-advanced-security", "AI AppSec", "Code, secret and dependency security connector"),
    ("gitguardian", "AI Secrets", "Secrets detection connector"),
    ("gitleaks-ai", "AI Secrets", "Secrets scanning integration"),
    # AI governance / risk
    ("nist-ai-rmf", "AI Governance", "NIST AI RMF control mapping"),
    ("owasp-llm-top10", "AI Governance", "OWASP LLM Top 10 control mapping"),
    ("owasp-agentic-top10", "Agent Governance", "OWASP Agentic Applications Top 10 mapping"),
    ("mitre-atlas", "AI Threat Intelligence", "MITRE ATLAS technique mapping"),
    ("mitre-cve-ai", "AI Threat Intelligence", "AI-specific vulnerability intelligence mapping"),
    ("model-card-toolkit", "AI Governance", "Model-card governance artifacts"),
    ("ai-incident-response", "AI Incident Response", "AI incident evidence/response workflow integration"),
    ("ai-red-team-orchestrator", "AI Red Team", "Governed AI security assessment orchestration"),
    ("ai-soc-copilot", "AI SOC", "AI-assisted SOC investigation integration"),
    ("agent-policy-engine", "Agent Governance", "Deterministic agent/tool policy enforcement"),
    ("agent-identity-broker", "Agent Identity", "Short-lived agent identity and capability broker"),
    ("capability-lease-gate", "Agent Identity", "Invocation-scoped capability lease enforcement"),
    ("ai-kill-switch", "Agent Safety", "Emergency agent disablement / circuit-breaker control"),
    ("agent-sandbox", "Agent Safety", "Isolated agent execution environment integration"),
    ("ai-egress-gateway", "AI Network Security", "Controlled egress for AI workloads"),
    ("prompt-provenance", "Prompt Security", "Prompt/context provenance and integrity tracking"),
    ("memory-firewall", "Agent Memory Security", "Agent memory policy and provenance enforcement"),
    ("rag-access-gateway", "RAG Security", "Authorization-aware retrieval gateway"),
    ("tool-supply-chain-scanner", "Agent Supply Chain", "Scan skills, MCP servers and tool definitions for risk"),
    ("skill-manifest-scanner", "Agent Supply Chain", "Agent skill/package manifest security checks"),
    ("model-registry-security", "AI Governance", "Model registry security and approval workflow"),
    ("aibom-generator", "AI SBOM", "AI bill-of-materials generation integration"),
]


def registry():
    out = []
    for name, category, purpose in AI_TOOLS:
        privileged = category in {"AI Red Team", "Agent Identity", "Agent Safety", "AI Network Security"}
        out.append({
            "id": name,
            "name": name,
            "category": category,
            "purpose": purpose,
            "access_tier": "privileged_admin" if privileged else "admin",
            "admin_only": True,
            "privileged_usage": privileged,
            "execution_profile": "isolated_ai_worker" if privileged else "approved_ai_worker",
            "status": "cataloged",
            "source": "veyra-ai-ecosystem-2026",
            "help": {
                "what_it_does": purpose,
                "safe_workflow": "Select an approved AI asset, define scope, run the governed evaluation on a managed worker, review evidence, then map results to AI security controls.",
                "evidence": ["model/agent identifier", "test case", "policy decision", "trace ID", "artifact hash", "timestamp"],
                "common_mistakes": ["Testing an unapproved model", "Mixing production secrets into test prompts", "Treating a benchmark score as proof of security"],
                "next_step": "Correlate the finding with VEYRA AI Security, Security Graph, MITRE ATLAS and governance controls.",
            },
        })
    return out


def overview():
    tools = registry()
    cats = {}
    for t in tools:
        cats[t["category"]] = cats.get(t["category"], 0) + 1
    return {"tool_count": len(tools), "categories": cats, "catalog": "AI security ecosystem", "note": "Catalog entries are governed integration candidates; installation and execution occur only on managed workers."}
