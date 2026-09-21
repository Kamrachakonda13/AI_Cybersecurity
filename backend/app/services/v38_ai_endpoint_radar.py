"""Curated AI-provider and endpoint security radar for AegisX v3.8."""
from .v38_posture_time_machine import AI_PROVIDER_RADAR, ENDPOINT_RELEASES

def overview():
 return {"release":"3.8","providers":AI_PROVIDER_RADAR,"endpoint_platforms":ENDPOINT_RELEASES,"guardrails":["Do not infer a vulnerability from a release label alone.","Correlate installed build/package/model/tool evidence before asserting exposure.","AI may prioritize; vendor advisories and endpoint telemetry are authoritative."]}
