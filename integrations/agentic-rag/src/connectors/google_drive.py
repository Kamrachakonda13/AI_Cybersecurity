"""
Google Drive connector (fixture-based).

Real implementation would use the Google Drive API v3 via google-api-python-client
with a service account or OAuth 2.0. The connector structure - listing, incremental
sync, ACL mapping - is identical; only the client changes.

Configuration mirrors the fixture base. To make this real, subclass and replace
the fixture loading with Drive API calls.
"""

from .fixture_base import FixtureSourceConnector


class GoogleDriveConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "google_drive"

    def transform_document(self, doc: dict) -> dict:
        """
        Drive-specific fields are already in the fixture, but this hook is where
        a real implementation would add Drive metadata like:
            - exportLinks (for Google Docs conversion to text)
            - capabilities
            - shared drive ID
        """
        base = super().transform_document(doc)
        base["drive_owner_email"] = doc.get("owner")
        return base