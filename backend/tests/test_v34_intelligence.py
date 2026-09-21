from app.services.v34_security_intelligence import CONTROL_TESTS, validation_plan
from test_v12 import db

def test_control_tests_have_governance():
    assert len(CONTROL_TESTS) >= 10
    assert all(t['domain'] and t['evidence'] for t in CONTROL_TESTS)

def test_validation_plan_requires_scope_and_approval(db):
    plan = validation_plan(db)
    assert plan['plan_id'].startswith('cv-')
    assert all(t['scope_required'] and t['approval_required'] for t in plan['tests'])
