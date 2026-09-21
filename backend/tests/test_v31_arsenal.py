from app.services.sudo_arsenal import arsenal_overview, list_tools, tool_detail, build_trace_plan


def test_arsenal_has_tools_and_privileged_subset():
    o = arsenal_overview()
    assert o["tool_count"] > 500
    assert o["privileged_count"] > 0
    assert o["hack_back"] == "disabled"


def test_tool_detail_has_ui_and_terminal_guidance():
    tool = list_tools()[0]
    d = tool_detail(tool["id"])
    assert d["ui_usage"]["step_1"]
    assert "--help" in d["terminal_usage"]["first_check"]


def test_trace_plan_is_defensive():
    p = build_trace_plan("203.0.113.10", "10.0.0.5:443", "2026-09-10T08:00:00Z", ["bad.example"])
    assert p["plan_id"].startswith("TRACE-")
    assert "hack-back" in p["prohibited"]
    assert "evidence_bundle" in p["outputs"]
