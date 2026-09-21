from app.services.v35_security_lifecycle import STAGES, lifecycle_plan, lifecycle_overview

def test_v35_has_ten_lifecycle_stages():
    assert len(STAGES)==10
    assert [x[0] for x in STAGES][-1]=='revalidate'

from test_v12 import db

def test_v35_plan_is_governed(db):
    plan=lifecycle_plan(db)
    assert plan['execution']=='plan_only'
    assert len(plan['stages'])==10
    assert 'approval' in ' '.join(lifecycle_overview(db)['guardrails'])
