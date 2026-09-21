"""AegisX deterministic, explainable risk engine.

Help — formula, dependencies, dependents:
- `calculate_risk(...)`: weighted sum capped at 100.0, rounded to 1 decimal:
    criticality×5 + cvss×5 + exploitability×8 + 15 if exposed + privilege×4
    + data_sensitivity×5 + threat×10 + anomaly×8.
  Pure function (no DB, no I/O) — safe to unit-test; covered by `test_risk.py`.
- `severity(score)`: ≥80 CRITICAL, ≥60 HIGH, ≥35 MEDIUM, else LOW. These bands
  drive the UI badges, `SEV_HELP` text in `frontend/src/main.jsx`, and the
  `SEVERITY_PLAYBOOKS` keys in `services/teams.py` (keep the three in sync).
- Depended on by: `services/seed.py` (scores demo findings) and
  `POST /api/risk/calculate` in `api/routes.py`.
"""
def calculate_risk(*, criticality:int, cvss:float, exploitability:float=1.0, exposure:bool=False, privilege:int=1, data_sensitivity:int=1, threat:float=0.0, anomaly:float=0.0) -> float:
    score = (criticality * 5) + (cvss * 5) + (exploitability * 8) + (15 if exposure else 0) + (privilege * 4) + (data_sensitivity * 5) + (threat * 10) + (anomaly * 8)
    return round(min(100.0, score), 1)

def severity(score:float) -> str:
    """Map a 0–100 risk score to a severity band (see module docstring)."""
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 35: return "MEDIUM"
    return "LOW"
