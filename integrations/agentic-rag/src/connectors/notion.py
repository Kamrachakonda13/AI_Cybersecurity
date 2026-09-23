"""
Notion connector (fixture-based).

Real implementation would use the Notion API with an integration token.
Key endpoints:
    POST /v1/search                    - search pages and databases
    GET  /v1/blocks/{block_id}/children - get page content
    POST /v1/databases/{database_id}/query - query a database

The connector ingests page content as documents. In a real deployment, Notion's
block structure would be converted to plain text or markdown.
"""

from .fixture_base import FixtureSourceConnector


class NotionConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "notion"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["database_id"] = doc.get("database_id")
        return base
