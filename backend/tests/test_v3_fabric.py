from app.db import SessionLocal, Base, engine
from app.services.v3_fabric import overview, graph_read_model, attack_reconstruction, ai_investigation, response_plan, recovery_check
from app.models import Asset, Finding, Incident, NetworkFlow, Identity

def test_v3_read_models_are_operational():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try:
        a=Asset(hostname='v3-test-host',ip_address='10.77.0.10',criticality=5)
        db.add(a); db.commit(); db.refresh(a)
        db.add(Finding(asset_id=a.id,title='v3 test finding',severity='HIGH',risk_score=75,cvss=8.0,status='open'))
        db.add(Incident(title='v3 test incident',severity='HIGH',asset='v3-test-host',status='open'))
        db.add(NetworkFlow(src_asset_id=a.id,src_ip='10.77.0.10',dst_ip='198.51.100.10',dst_port=443,bytes_out=900000,risk_score=82))
        db.add(Identity(username='v3-admin',privilege=5,mfa_enabled=False))
        db.commit()
        assert overview(db)['version']=='3.0.0'
        assert graph_read_model(db)['nodes']
        assert attack_reconstruction(db)['events']
        assert ai_investigation(db)['signals']
        assert response_plan(db)['actions']
        assert recovery_check(db)['overall'] in {'ready_for_review','not_verified'}
    finally:
        db.close()
