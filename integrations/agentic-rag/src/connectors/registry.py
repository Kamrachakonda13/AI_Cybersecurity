"""
Connector registry for Phase 6.

Discovers, loads, and manages all configured source connectors. The registry
reads a manifest file (data/connectors/registry.json) that lists every connector
config path, then instantiates the right class for each one.

The registry isolates failures: if one connector fails to load, the others
still load. Failed loads are recorded and reported but do not raise.

Usage:
    from src.connectors.registry import ConnectorRegistry
    registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")

    # List what loaded
    for entry in registry.list_sources():
        print(entry["name"], entry["status"])

    # Iterate over working connectors
    for name, connector in registry.all_connectors():
        for change in connector.list_changed_since(cursor=None):
            ...

    # Get one specific connector
    connector = registry.get("s3")
"""

import importlib
import json

from dotenv import load_dotenv
from pathlib import Path
from typing import Iterator, Optional


# Load .env at import time so connectors that read os.environ get credentials.
load_dotenv()

# Mapping from connector_type string to (module_path, class_name).
# Adding a new connector means adding one line here.
CONNECTOR_CLASS_MAP = {
    "local_fs":      ("src.connectors.local_fs",     "LocalFSConnector"),
    "pdf_fs":        ("src.connectors.pdf_fs",       "PDFFSConnector"),
    "s3":            ("src.connectors.s3",           "S3Connector"),
    "ms_graph":      ("src.connectors.ms_graph",     "MSGraphConnector"),
    "google_drive":  ("src.connectors.google_drive", "GoogleDriveConnector"),
    "sharepoint":    ("src.connectors.sharepoint",   "SharePointConnector"),
    "m365":          ("src.connectors.m365",         "M365Connector"),
    "powerbi":       ("src.connectors.powerbi",      "PowerBIConnector"),
    "tableau":       ("src.connectors.tableau",      "TableauConnector"),
    "confluence":    ("src.connectors.confluence",   "ConfluenceConnector"),
    "jira":          ("src.connectors.jira",         "JiraConnector"),
    "slack":         ("src.connectors.slack",        "SlackConnector"),
    "notion":        ("src.connectors.notion",       "NotionConnector"),
}


class ConnectorLoadError(Exception):
    """Raised when a connector cannot be loaded. Captured by the registry."""
    pass


class ConnectorRegistry:
    """
    Central registry of all configured source connectors.
    """

    def __init__(self):
        self._connectors: dict = {}   # name -> connector instance
        self._failures: dict = {}     # name -> error message
        self._configs: dict = {}      # name -> parsed config dict

    # -------------------------------------------------------------------
    # Loading
    # -------------------------------------------------------------------

    @classmethod
    def from_manifest(cls, manifest_path: str) -> "ConnectorRegistry":
        """
        Build a registry from a manifest file listing connector config paths.
        """
        registry = cls()

        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            raise ConnectorLoadError(f"Manifest not found: {manifest_path}")

        manifest = json.loads(manifest_file.read_text())
        entries = manifest.get("connectors", [])

        for entry in entries:
            name = entry.get("name")
            config_path = entry.get("config")
            if not name or not config_path:
                continue
            registry._try_load(name, config_path)

        return registry

    def _try_load(self, name: str, config_path: str):
        """Load a single connector. Record failure but do not raise."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise ConnectorLoadError(f"Config not found: {config_path}")

            config = json.loads(config_file.read_text())
            self._configs[name] = config

            connector_type = config.get("connector_type", name)
            if connector_type not in CONNECTOR_CLASS_MAP:
                raise ConnectorLoadError(
                    f"Unknown connector_type: {connector_type}"
                )

            module_name, class_name = CONNECTOR_CLASS_MAP[connector_type]

            module = importlib.import_module(module_name)
            klass = getattr(module, class_name)

            # All connectors accept config_path as a keyword argument.
            # Real connectors with additional required args (like s3, ms_graph)
            # handle their own environment loading inside __init__.
            instance = klass(config_path=config_path)

            self._connectors[name] = instance

        except Exception as e:
            self._failures[name] = f"{type(e).__name__}: {str(e)[:200]}"

    # -------------------------------------------------------------------
    # Introspection
    # -------------------------------------------------------------------

    def list_sources(self) -> list:
        """
        Return a list of dicts describing every connector, both loaded and failed.
        """
        out = []

        for name, connector in self._connectors.items():
            config = self._configs.get(name, {})
            out.append({
                "name": name,
                "source_system": getattr(connector, "SOURCE_SYSTEM", "unknown"),
                "display_name": config.get("display_name", name),
                "status": "loaded",
                "config_path": f"data/connectors/{name}.json",
            })

        for name, error in self._failures.items():
            config = self._configs.get(name, {})
            out.append({
                "name": name,
                "source_system": config.get("connector_type", name),
                "display_name": config.get("display_name", name),
                "status": "failed",
                "error": error,
            })

        return out

    def get(self, name: str):
        """Return a single connector by name. Raises if not loaded."""
        if name not in self._connectors:
            if name in self._failures:
                raise ConnectorLoadError(
                    f"Connector {name} failed to load: {self._failures[name]}"
                )
            raise KeyError(f"No connector registered with name: {name}")
        return self._connectors[name]

    def all_connectors(self) -> Iterator[tuple]:
        """Yield (name, connector) pairs for every successfully loaded connector."""
        for name, connector in self._connectors.items():
            yield name, connector

    def loaded_names(self) -> list:
        return list(self._connectors.keys())

    def failed_names(self) -> list:
        return list(self._failures.keys())

    def summary(self) -> dict:
        return {
            "loaded": len(self._connectors),
            "failed": len(self._failures),
            "loaded_names": self.loaded_names(),
            "failed_names": self.failed_names(),
            "failures": dict(self._failures),
        }


# -------------------------------------------------------------------------
# Self-test
# -------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pathlib import Path as P

    print("=== Phase 6.11 connector registry self-test ===\n")

    project_root = P(__file__).resolve().parent.parent.parent
    manifest = project_root / "data" / "connectors" / "registry.json"

    if not manifest.exists():
        print(f"FAIL: manifest not found at {manifest}")
        sys.exit(1)

    registry = ConnectorRegistry.from_manifest(str(manifest))

    summary = registry.summary()
    print(f"Loaded: {summary['loaded']}")
    print(f"Failed: {summary['failed']}")
    print()

    print("Connectors:")
    for entry in registry.list_sources():
        status = entry["status"]
        name = entry["name"]
        source = entry.get("source_system", "?")
        if status == "loaded":
            print(f"  [OK]     {name:<15} ({source})")
        else:
            err = entry.get("error", "")[:80]
            print(f"  [FAILED] {name:<15} ({source}) -- {err}")

    print()

    if summary["failed"] > 0:
        print(f"WARNING: {summary['failed']} connector(s) failed to load.")
        for name, err in summary["failures"].items():
            print(f"  {name}: {err}")
    else:
        print("All connectors loaded successfully.")

    # Quick document count across all loaded connectors
    print()
    print("Document counts:")
    total = 0
    for name, connector in registry.all_connectors():
        try:
            docs = list(connector.list_changed_since(cursor=None))
            total += len(docs)
            print(f"  {name:<15} {len(docs):>3} documents")
        except Exception as e:
            print(f"  {name:<15} ERROR: {str(e)[:60]}")

    print()
    print(f"Total documents across all sources: {total}")
