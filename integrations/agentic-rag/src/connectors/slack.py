"""
Slack connector (fixture-based).

Real implementation would use the Slack Web API with a bot token. Key endpoints:
    conversations.list      - list channels
    conversations.history   - list messages in a channel
    conversations.replies   - list thread replies

The connector ingests thread text as documents. In a real deployment, threads
would be converted from the Slack JSON structure to plain text.
"""

from .fixture_base import FixtureSourceConnector


class SlackConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "slack"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["channel"] = doc.get("channel")
        return base
