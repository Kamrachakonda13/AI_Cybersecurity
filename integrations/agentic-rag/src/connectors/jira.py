"""
Jira connector (fixture-based).

Real implementation would use the Jira Cloud REST API with an API token or
OAuth 2.0. Key endpoints:
    GET /rest/api/3/project                    - list projects
    GET /rest/api/3/search                     - search issues
    GET /rest/api/3/issue/{issueIdOrKey}       - get issue details
"""

from .fixture_base import FixtureSourceConnector


class JiraConnector(FixtureSourceConnector):
    SOURCE_SYSTEM = "jira"

    def transform_document(self, doc: dict) -> dict:
        base = super().transform_document(doc)
        base["project_key"] = doc.get("project_key")
        return base
