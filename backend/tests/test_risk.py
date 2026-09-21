"""Tests for `services/risk.py`: cap-at-100 and the 4 severity bands.

Help: pure-function tests, no DB. Run from `backend/`: `python3 -m pytest tests -q`.
"""
from app.services.risk import calculate_risk, severity

def test_risk_caps_at_100():
    assert calculate_risk(criticality=5,cvss=10,exploitability=1,exposure=True,privilege=5,data_sensitivity=5,threat=1,anomaly=1) == 100.0

def test_severity():
    assert severity(90)=="CRITICAL"
    assert severity(65)=="HIGH"
    assert severity(40)=="MEDIUM"
    assert severity(10)=="LOW"
