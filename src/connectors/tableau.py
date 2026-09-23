"""
Tableau connector (fixture-based).

Real implementation would use the Tableau REST API with a Personal Access
Token (PAT) or connected app credentials.
"""

from .fixture_base import FixtureSourceConnector


class TableauConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "tableau"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["site_id"] = doc.get("site_id")
        return base
