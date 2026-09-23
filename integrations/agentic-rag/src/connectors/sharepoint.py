"""SharePoint connector (fixture-based)."""

from .fixture_base import FixtureSourceConnector


class SharePointConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "sharepoint"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["site_id"] = doc.get("site_id")
        base["library"] = doc.get("library", "Shared Documents")
        return base
