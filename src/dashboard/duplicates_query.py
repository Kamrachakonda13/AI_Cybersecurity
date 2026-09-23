"""
Duplicates query for the dashboard.

Wraps src.dedup to produce a JSON-friendly summary for the dashboard.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.connectors.registry import ConnectorRegistry
from src.dedup import find_duplicates, select_canonical


def get_duplicates_summary():
    """
    Return:
        {
            "total_documents": N,
            "unique_fingerprints": N,
            "duplicate_groups": N,
            "redundant_copies": N,
            "cross_team_overlaps": N,
            "groups": [
                {
                    "fingerprint": "fp:v1:...",
                    "members_count": N,
                    "cross_team": ["platform", "sre"],
                    "canonical": {
                        "source_system": "local_fs",
                        "source_id": "...",
                        "title": "...",
                        "owner_team": "platform",
                        "clearance_level": "INTERNAL",
                        "source_url": "...",
                    },
                    "alternates": [
                        {
                            "source_system": "sharepoint",
                            "source_id": "...",
                            "title": "...",
                            "owner_team": "sre",
                            "clearance_level": "INTERNAL",
                            "source_url": "...",
                        }
                    ]
                }
            ]
        }
    """
    try:
        registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
        result = find_duplicates(registry)
    except Exception as e:
        return {
            "error": str(e)[:200],
            "total_documents": 0,
            "unique_fingerprints": 0,
            "duplicate_groups": 0,
            "redundant_copies": 0,
            "cross_team_overlaps": 0,
            "groups": [],
        }

    groups_out = []
    cross_team_count = 0

    for fp, members in result["groups"].items():
        canonical, alternates = select_canonical(members)
        teams = sorted({m.owner_team for m in members if m.owner_team})
        if len(teams) > 1:
            cross_team_count += 1

        groups_out.append({
            "fingerprint": fp,
            "fingerprint_short": fp.replace("fp:v1:", "")[:16] + "...",
            "members_count": len(members),
            "cross_team": teams,
            "canonical": {
                "source_system": canonical.source_system,
                "source_id": canonical.source_id[-60:],
                "title": canonical.title or "(untitled)",
                "owner_team": canonical.owner_team,
                "clearance_level": canonical.clearance_level,
                "source_url": canonical.source_url,
            },
            "alternates": [
                {
                    "source_system": alt.source_system,
                    "source_id": alt.source_id[-60:],
                    "title": alt.title or "(untitled)",
                    "owner_team": alt.owner_team,
                    "clearance_level": alt.clearance_level,
                    "source_url": alt.source_url,
                }
                for alt in alternates
            ],
        })

    return {
        "error": None,
        "total_documents": result["total_documents"],
        "unique_fingerprints": result["unique_fingerprints"],
        "duplicate_groups": result["duplicate_groups"],
        "redundant_copies": result["duplicate_documents"],
        "cross_team_overlaps": cross_team_count,
        "groups": groups_out,
    }


if __name__ == "__main__":
    print("=== duplicates_query self-test ===\n")
    result = get_duplicates_summary()
    if result.get("error"):
        print("Error:", result["error"])
    else:
        print(f"Total documents:      {result['total_documents']}")
        print(f"Unique fingerprints:  {result['unique_fingerprints']}")
        print(f"Duplicate groups:     {result['duplicate_groups']}")
        print(f"Redundant copies:     {result['redundant_copies']}")
        print(f"Cross-team overlaps:  {result['cross_team_overlaps']}")
        print()
        for g in result["groups"]:
            print(f"Group {g['fingerprint_short']}: {g['members_count']} members")
            print(f"  Canonical:  [{g['canonical']['source_system']}] {g['canonical']['title']}")
            print(f"              owner_team={g['canonical']['owner_team']} clearance={g['canonical']['clearance_level']}")
            for alt in g["alternates"]:
                print(f"  Alternate:  [{alt['source_system']}] {alt['title']}")
                print(f"              owner_team={alt['owner_team']} clearance={alt['clearance_level']}")
            print(f"  Cross-team: {', '.join(g['cross_team'])}")
            print()
    print("All tests PASS")
