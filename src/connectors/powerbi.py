"""
Power BI connector (fixture-based).

Real implementation would use the Power BI REST API via the Microsoft identity
platform (Azure AD). Key endpoints:
    GET /v1.0/myorg/groups                    - list workspaces
    GET /v1.0/myorg/groups/{id}/reports       - list reports
    GET /v1.0/myorg/groups/{id}/datasets      - list datasets

The connector ingests report descriptions, dataset schemas, and KPI metadata
as text documents. The unified document model handles this the same way it
handles any other text-based source.
"""

from .fixture_base import FixtureSourceConnector


class PowerBIConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "powerbi"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["workspace_id"] = doc.get("workspace_id")
        return base
