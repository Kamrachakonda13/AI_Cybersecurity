from app.db import SessionLocal, Base, engine
from app.models import AISupplyChainAsset, AIAssetTrustRecord, AIBOMRecord, AgentTrajectory, TrustDecisionRecord
from app.services.v50_trust_control_plane import evaluate_asset, evaluate_trajectory, trust_decision, make_aibom, build_trust_graph
Base.metadata.create_all(bind=engine)

def test_v50_asset_never_trusted_by_registration():
    x=evaluate_asset({'asset_id':'x','name':'x','asset_type':'model'})
    assert x['status']=='untrusted'
    assert 'identity' in x['missing']

def test_v50_full_trust_contract():
    x={k:'yes' for k in ('publisher','provenance_uri','digest','behavior_baseline','trajectory_policy','evidence_sha256','circuit_breaker_id')}
    x.update({'policy_status':'approved','validation_status':'passed','deployment_status':'controlled','runtime_identity':'spiffe://veyra/agent/demo'})
    assert evaluate_asset(x)['status']=='trusted'

def test_v50_trajectory_blocks_chain_violation():
    r=evaluate_trajectory([{'identity':'a','tool':'read','destination':'db','approved':True},{'identity':'a','tool':'send','destination':'evil'}],{'allowed_tools':['read'],'allowed_destinations':['db']})
    assert r['status']=='fail'
    assert len(r['violations'])>=2

def test_v50_graph_and_aibom_are_hashable():
    a={'asset_id':'model-1','asset_type':'model','name':'demo','version':'1','digest':'sha256:abc','publisher':'test'}
    bom=make_aibom(a,[{'source_id':'model-1','target_id':'agent-1','relationship':'used_by'}])
    graph=build_trust_graph([a],[{'source_id':'model-1','target_id':'agent-1','relationship':'used_by'}])
    assert len(bom['document_sha256'])==64 and graph['node_count']==1
