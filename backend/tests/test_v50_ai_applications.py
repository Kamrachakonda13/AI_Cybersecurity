"""Tests for backend/app/services/v50_ai_applications.py.

Covers the six VEYRA v5.0 AI applications, the shared RAG primitive, and the
catalog. The applications are demo fixtures — the tests validate structure,
determinism, governance markers, and evidence grounding.
"""
from app.services import v50_ai_applications as apps


# ---------------------------------------------------------------------------
# Helpers & constants
# ---------------------------------------------------------------------------

def test_sha_is_deterministic():
    assert apps._sha({"a": 1, "b": 2}) == apps._sha({"b": 2, "a": 1})


def test_sha_changes_with_content():
    assert apps._sha({"a": 1}) != apps._sha({"a": 2})


def test_tokens_lowercases():
    assert apps._tokens("HELLO WORLD") == apps._tokens("hello world")


def test_tokens_min_length_3():
    # 1- and 2-char tokens should be dropped
    assert apps._tokens("a ab abc") == {"abc"}


def test_tokens_empty_string():
    assert apps._tokens("") == set()


def test_corpus_has_expected_count():
    assert len(apps.CORPUS) == 8


def test_corpus_entries_have_required_fields():
    for doc in apps.CORPUS:
        assert "id" in doc
        assert "title" in doc
        assert "type" in doc
        assert "text" in doc
        assert "tags" in doc
        assert isinstance(doc["tags"], list)


def test_corpus_ids_are_unique():
    ids = [d["id"] for d in apps.CORPUS]
    assert len(ids) == len(set(ids))


def test_sample_incident_shape():
    assert len(apps.SAMPLE_INCIDENT) >= 5
    for event in apps.SAMPLE_INCIDENT:
        assert "ts" in event
        assert "event" in event


# ---------------------------------------------------------------------------
# hybrid_retrieve()
# ---------------------------------------------------------------------------

def test_hybrid_retrieve_returns_at_most_top_k():
    hits = apps.hybrid_retrieve("powershell", top_k=3)
    assert len(hits) <= 3


def test_hybrid_retrieve_result_shape():
    hits = apps.hybrid_retrieve("powershell", top_k=3)
    for h in hits:
        assert set(h.keys()) >= {"id", "title",
                                 "type", "score", "text", "citation"}
        assert h["citation"] == f"[{h['id']}]"


def test_hybrid_retrieve_orders_by_score_descending():
    hits = apps.hybrid_retrieve("powershell", top_k=5)
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_hybrid_retrieve_deterministic():
    a = apps.hybrid_retrieve("powershell authentication", top_k=5)
    b = apps.hybrid_retrieve("powershell authentication", top_k=5)
    assert [h["id"] for h in a] == [h["id"] for h in b]


def test_hybrid_retrieve_filter_by_type():
    hits = apps.hybrid_retrieve("attack", top_k=5, filters={"type": "mitre"})
    for h in hits:
        assert h["type"] == "mitre"


def test_hybrid_retrieve_unmatched_query_returns_empty():
    hits = apps.hybrid_retrieve("zzzz-nothing-matches-here", top_k=5)
    assert hits == []


# ---------------------------------------------------------------------------
# cybsoc_rag()
# ---------------------------------------------------------------------------

def test_cybsoc_rag_shape():
    result = apps.cybsoc_rag("suspicious PowerShell")
    assert result["application"] == "cybsoc_rag"
    assert "answer" in result
    assert isinstance(result["answer"], str) and result["answer"]
    assert "retrieval" in result
    assert "citations" in result
    assert "grounded" in result
    assert "latency_ms" in result


def test_cybsoc_rag_citations_match_retrieval():
    result = apps.cybsoc_rag("suspicious PowerShell")
    expected_citations = [h["citation"] for h in result["retrieval"]]
    assert result["citations"] == expected_citations


def test_cybsoc_rag_mentions_powershell_when_mitre_present():
    result = apps.cybsoc_rag("PowerShell activity")
    if any(h["type"] == "mitre" for h in result["retrieval"]):
        assert "PowerShell" in result["answer"] or "MITRE" in result["answer"]


def test_cybsoc_rag_deterministic_answer():
    a = apps.cybsoc_rag("suspicious PowerShell")
    b = apps.cybsoc_rag("suspicious PowerShell")
    assert a["answer"] == b["answer"]
    assert [h["id"] for h in a["retrieval"]] == [h["id"]
                                                 for h in b["retrieval"]]


# ---------------------------------------------------------------------------
# vulnerability_rag()
# ---------------------------------------------------------------------------

def test_vulnerability_rag_shape():
    result = apps.vulnerability_rag()
    assert result["application"] == "vulnerability_intelligence_rag"
    assert "query" in result
    assert "priority_queue" in result
    assert "retrieval" in result
    assert "citations" in result


def test_vulnerability_rag_priority_queue_sorted():
    result = apps.vulnerability_rag()
    scores = [a["risk_score"] for a in result["priority_queue"]]
    assert scores == sorted(scores, reverse=True)


def test_vulnerability_rag_asset_fields():
    result = apps.vulnerability_rag()
    for a in result["priority_queue"]:
        assert set(a.keys()) >= {
            "asset", "cve", "cvss", "kev", "exposed",
            "criticality", "data", "risk_score", "reason",
        }
        assert 0 <= a["risk_score"] <= 100


def test_vulnerability_rag_kev_exposed_first():
    """The internet-facing KEV asset should outrank the others."""
    result = apps.vulnerability_rag()
    top = result["priority_queue"][0]
    assert top["kev"] is True
    assert top["exposed"] is True


# ---------------------------------------------------------------------------
# autonomous_research()
# ---------------------------------------------------------------------------

def test_autonomous_research_shape():
    result = apps.autonomous_research("agent security research")
    assert result["application"] == "autonomous_research_agent"
    assert "stages" in result
    assert "findings" in result
    assert "report" in result
    assert "fact_check" in result
    assert "critic" in result


def test_autonomous_research_stages():
    result = apps.autonomous_research("agent security")
    expected = {"planner", "search_agent", "retrieval_agent", "analyst",
                "fact_checker", "critic", "report_generator"}
    assert set(result["stages"]) == expected


def test_autonomous_research_fact_check_passes_with_hits():
    result = apps.autonomous_research("agent security research")
    if result["findings"]:
        assert result["fact_check"]["status"] == "pass"
        assert result["fact_check"]["checked_claims"] == len(
            result["findings"])


def test_autonomous_research_offline_cost():
    """Demo adapter is offline — cost should be 0.0."""
    result = apps.autonomous_research("anything")
    assert result["cost_usd"] == 0.0


# ---------------------------------------------------------------------------
# incident_response()
# ---------------------------------------------------------------------------

def test_incident_response_uses_default_events():
    result = apps.incident_response()
    assert result["application"] == "agentic_incident_response"
    assert result["timeline"] == apps.SAMPLE_INCIDENT


def test_incident_response_accepts_custom_events():
    custom = [
        {"ts": "01:00", "event": "failed_login", "user": "bob"},
        {"ts": "01:01", "event": "failed_login", "user": "bob"},
    ]
    result = apps.incident_response(custom)
    assert result["timeline"] == custom


def test_incident_response_approval_gated():
    """Even at high risk, containment must not execute."""
    result = apps.incident_response()
    assert result["approval_required"] is True
    assert result["containment_executed"] is False


def test_incident_response_detects_powershell():
    result = apps.incident_response()
    assert "T1059.001 PowerShell" in result["mitre"]


def test_incident_response_risk_score_in_range():
    result = apps.incident_response()
    assert 0 <= result["risk_score"] <= 100


def test_incident_response_without_powershell():
    events = [{"ts": "01:00", "event": "failed_login", "user": "bob"}]
    result = apps.incident_response(events)
    assert result["mitre"] == []
    assert "initial_access" in result["attack_stage"]


# ---------------------------------------------------------------------------
# enterprise_decision()
# ---------------------------------------------------------------------------

def test_enterprise_decision_shape():
    result = apps.enterprise_decision("Why did churn increase?")
    assert result["application"] == "enterprise_ai_decision_platform"
    assert "answer" in result
    assert "evidence" in result
    assert "citations" in result
    assert "grounded" in result


def test_enterprise_decision_churn_specific_answer():
    result = apps.enterprise_decision("Why did churn increase?")
    assert "4.1%" in result["answer"]
    assert "5.6%" in result["answer"]


def test_enterprise_decision_generic_answer():
    result = apps.enterprise_decision("What is our security posture?")
    assert "VEYRA" in result["answer"]


# ---------------------------------------------------------------------------
# evaluate_ai()
# ---------------------------------------------------------------------------

def test_evaluate_ai_shape():
    result = apps.evaluate_ai()
    assert result["application"] == "llm_evaluation_reliability"
    assert "dataset" in result
    assert "metrics" in result
    assert "release_gate" in result


def test_evaluate_ai_release_gate_passes():
    result = apps.evaluate_ai()
    assert result["release_gate"]["decision"] == "pass"


def test_evaluate_ai_metrics_structure():
    result = apps.evaluate_ai()
    metrics = result["metrics"]
    # 4 keys expected based on the module
    assert "rag_pipeline_a" in metrics
    assert "rag_pipeline_b" in metrics
    assert "agent_pipeline_a" in metrics
    assert "model_comparison" in metrics


# ---------------------------------------------------------------------------
# catalog()
# ---------------------------------------------------------------------------

def test_catalog_has_six_apps():
    items = apps.catalog()
    assert len(items) == 6


def test_catalog_ids_match_expected():
    ids = {item["id"] for item in apps.catalog()}
    expected = {
        "cybsoc_rag",
        "vulnerability_intelligence_rag",
        "autonomous_research_agent",
        "agentic_incident_response",
        "enterprise_ai_decision_platform",
        "llm_evaluation_reliability",
    }
    assert ids == expected


def test_catalog_entries_have_shape():
    for item in apps.catalog():
        assert "id" in item
        assert "name" in item
        assert "category" in item
        assert "description" in item


# ---------------------------------------------------------------------------
# Structural boundary checks
# ---------------------------------------------------------------------------

def test_module_does_not_execute_shell():
    """Regression guard: no subprocess / os.system in the module source."""
    from pathlib import Path
    import re
    repo = Path(__file__).resolve().parents[2]
    source = (repo / "backend" / "app" / "services" /
              "v50_ai_applications.py").read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)
