from app.services.v50_trust_control_plane import (
    evaluate_agent_authority, evaluate_gateway_request, compare_mcp_fingerprint,
    evaluate_memory, assess_transaction, compare_behavior, build_digital_twin
)

def test_agent_authority_and_gateway():
    a=evaluate_agent_authority({"agent_id":"a1","issuer":"issuer","owner":"owner","credential_ref":"ref","allowed_tools":["read"],"expires_at":"2026-12-01","status":"active"})
    assert a["status"] == "trusted"
    g=evaluate_gateway_request({"tool":"write","external":True},{"allowed_tools":["read"],"require_approval":True})
    assert g["decision"] == "deny"

def test_mcp_memory_transaction_behavior():
    m=compare_mcp_fingerprint({"tools_hash":"a","permissions_hash":"p","endpoint_hash":"e","version":"1"},{"tools_hash":"b","permissions_hash":"p","endpoint_hash":"e","version":"2"})
    assert m["status"] == "approval_required"
    mem=evaluate_memory({"content_hash":"h","provenance":"src","owner":"u","poisoning_score":0.1})
    assert mem["status"] == "trusted"
    tx=assess_transaction({"amount":100,"transaction_ceiling":50,"new_destination":True})
    assert tx["decision"] == "block"
    bh=compare_behavior({"tools":["read"],"destinations":["internal"],"delegation_depth":1,"transaction_ceiling":100},{"tools":["read","write"],"destinations":["internal"],"delegation_depth":2,"transaction_amount":150})
    assert bh["status"] == "high_risk"

def test_digital_twin():
    r=build_digital_twin("agent",[{"id":"agent"},{"id":"mcp"},{"id":"db","critical":True}],[{"source":"agent","target":"mcp"},{"source":"mcp","target":"db"}])
    assert r["blast_radius"] == 3
    assert "quarantine_root_agent" in r["containment_options"]
