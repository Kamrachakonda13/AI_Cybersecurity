from test_v12 import db
from app.db import Base
from app.models import Asset, Finding, PostureSnapshot
from app.services.v38_posture_time_machine import current, create_snapshot, history, compare_latest

def test_v38_current_and_snapshot(db):
    db.add(Asset(hostname='v38-host', ip_address='10.0.0.8', criticality=4))
    db.add(Finding(asset_id=1, title='Patch gap', severity='HIGH', cvss=8.1, risk_score=65, status='open'))
    db.commit()
    d=current(db)
    assert d['release']=='3.8'
    s=create_snapshot(db)
    assert s['snapshot_id'].startswith('ps_')
    assert len(s['hash_sha256'])==64
    assert history(db)['snapshots']

def test_v38_compare_requires_two_snapshots(db):
    assert compare_latest(db)['status']=='insufficient_history'
