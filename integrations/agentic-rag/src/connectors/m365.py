"""Microsoft 365 connector (fixture-based, Teams focus)."""

from .fixture_base import FixtureSourceConnector


class M365Connector(FixtureSourceConnector):
    SOURCE_SYSTEM = "m365"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["channel"] = doc.get("channel")
        return base
