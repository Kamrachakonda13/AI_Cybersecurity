"""
Confluence connector (fixture-based).

Real implementation would use the Confluence Cloud REST API with an API token
or Atlassian Connect app. Key endpoints:
    GET /wiki/rest/api/spaces                  - list spaces
    GET /wiki/rest/api/content                 - list pages
    GET /wiki/rest/api/content/{id}            - get page body
"""

from .fixture_base import FixtureSourceConnector


class ConfluenceConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "confluence"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["space_key"] = doc.get("space_key")
        return base
