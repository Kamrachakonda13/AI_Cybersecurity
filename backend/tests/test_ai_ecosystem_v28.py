import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.ai_ecosystem import registry, overview

def test_ai_ecosystem_has_broad_coverage():
    tools = registry()
    assert len(tools) >= 100
    ids = [t['id'] for t in tools]
    assert len(ids) == len(set(ids))
    categories = {t['category'] for t in tools}
    for expected in {'LLM Red Team','Agent Security','MCP Security','RAG Security','AI Supply Chain','AI Observability','AI Governance'}:
        assert expected in categories

def test_ai_tool_cards_have_help_and_governance():
    for tool in registry():
        assert tool['admin_only'] is True
        assert tool['execution_profile'] in {'isolated_ai_worker','approved_ai_worker'}
        assert tool['help']['safe_workflow']
        assert tool['help']['evidence']

def test_ai_overview_matches_catalog():
    o=overview()
    assert o['tool_count'] == len(registry())
