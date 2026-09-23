"""
Access control filter logic for federated search.

Given a user's identity (role, team, tenant, user_id), produces:
  - The list of clearance levels the user is allowed to see
  - The list of teams the user belongs to (for share_scope matching)
  - The user's principal string (for acl matching)

Then, in the search query, the ACL filter is:

    clearance_level = ANY($allowed_levels)
    AND tenant_id = $tenant
    AND (
         owner_team = ANY($user_teams)
         OR share_scope = 'org'
         OR share_scope && $user_teams              -- array overlap
         OR acl::jsonb @> $user_principal_json       -- principal containment
    )

Where share_scope is either the string 'team', 'org', or a JSON array of team
names. In the chunks table, share_scope is stored inside alternate_sources? No —
share_scope is not currently stored on the chunk. We add it as a column.
"""

# Clearance hierarchy
CLEARANCE_RANK = {
    "PUBLIC": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4,
}


def allowed_clearance_levels(user_clearance: str) -> list:
    """Return all clearance levels at or below the user's clearance."""
    max_rank = CLEARANCE_RANK.get(user_clearance, 0)
    return [level for level, rank in CLEARANCE_RANK.items() if rank <= max_rank]


def user_teams(role: str, explicit_teams: list = None) -> list:
    """
    Return the list of teams this user belongs to.

    In the demo, the user's team is passed explicitly. In production, this
    would be resolved from the identity provider or a group membership table.
    """
    if explicit_teams:
        return list(explicit_teams)
    return []


def user_principal(user_id: str) -> dict:
    """
    Return the principal object that must be contained in a chunk's acl
    for the user to have explicit access.
    """
    return {"principal_type": "user", "principal_id": user_id, "access": "read"}


def build_acl_filter(user: dict) -> dict:
    """
    Given a user dict:
        {
          "user_id": "alice@acme.com",
          "role": "csuite",
          "tenant_id": "acme",
          "clearance": "CONFIDENTIAL",
          "teams": ["platform", "sre"],
        }

    Return a dict with the parameters needed to build the SQL filter.
    """
    return {
        "allowed_levels": allowed_clearance_levels(user["clearance"]),
        "tenant_id": user["tenant_id"],
        "user_teams": user.get("teams", []),
        "user_principal": user_principal(user["user_id"]),
    }


def can_retrieve(user: dict, chunk: dict) -> bool:
    """
    Python-side check: can the given user retrieve the given chunk?
    Mirrors the SQL filter exactly. Used in tests.
    """
    # 1. Clearance
    if chunk.get("clearance_level") not in allowed_clearance_levels(user["clearance"]):
        return False

    # 2. Tenant
    if chunk.get("tenant_id") != user["tenant_id"]:
        return False

    # 3. Ownership / share scope / acl
    user_team_set = set(user.get("teams", []))
    owner_team = chunk.get("owner_team", "")
    share_scope = chunk.get("share_scope")

    # Owner team match
    if owner_team in user_team_set:
        return True

    # Org-wide
    if share_scope == "org":
        return True

    # Array share scope
    if isinstance(share_scope, list) and user_team_set & set(share_scope):
        return True

    # Explicit ACL
    principal = user_principal(user["user_id"])
    for grant in chunk.get("acl", []):
        if (grant.get("principal_type") == principal["principal_type"]
                and grant.get("principal_id") == principal["principal_id"]):
            return True

    return False


if __name__ == "__main__":
    print("=== ACL filter self-test ===\n")

    user = {
        "user_id": "alice@acme.com",
        "role": "manager",
        "tenant_id": "acme",
        "clearance": "INTERNAL",
        "teams": ["platform"],
    }

    # Test 1: allowed levels
    levels = allowed_clearance_levels("INTERNAL")
    assert set(levels) == {"PUBLIC", "INTERNAL"}, levels
    print("Test 1 (allowed_clearance_levels): PASS")

    # Test 2: filter dict
    f = build_acl_filter(user)
    assert f["tenant_id"] == "acme"
    assert "PUBLIC" in f["allowed_levels"]
    assert "CONFIDENTIAL" not in f["allowed_levels"]
    print("Test 2 (build_acl_filter): PASS")

    # Test 3: can_retrieve for owner team
    chunk = {
        "clearance_level": "INTERNAL",
        "tenant_id": "acme",
        "owner_team": "platform",
        "share_scope": "team",
        "acl": [],
    }
    assert can_retrieve(user, chunk) is True
    print("Test 3 (owner team match): PASS")

    # Test 4: can_retrieve fails for clearance
    chunk["clearance_level"] = "CONFIDENTIAL"
    assert can_retrieve(user, chunk) is False
    print("Test 4 (clearance ceiling): PASS")

    # Test 5: share_scope org
    chunk = {
        "clearance_level": "INTERNAL",
        "tenant_id": "acme",
        "owner_team": "hr",
        "share_scope": "org",
        "acl": [],
    }
    assert can_retrieve(user, chunk) is True
    print("Test 5 (share_scope=org): PASS")

    # Test 6: share_scope list intersection
    chunk = {
        "clearance_level": "INTERNAL",
        "tenant_id": "acme",
        "owner_team": "sre",
        "share_scope": ["sre", "platform", "security"],
        "acl": [],
    }
    assert can_retrieve(user, chunk) is True
    print("Test 6 (share_scope array overlap): PASS")

    # Test 7: explicit ACL
    chunk = {
        "clearance_level": "INTERNAL",
        "tenant_id": "acme",
        "owner_team": "other",
        "share_scope": "team",
        "acl": [{"principal_type": "user", "principal_id": "alice@acme.com", "access": "read"}],
    }
    assert can_retrieve(user, chunk) is True
    print("Test 7 (explicit ACL): PASS")

    # Test 8: deny by default
    chunk = {
        "clearance_level": "INTERNAL",
        "tenant_id": "acme",
        "owner_team": "other",
        "share_scope": "team",
        "acl": [],
    }
    assert can_retrieve(user, chunk) is False
    print("Test 8 (deny by default): PASS")

    print()
    print("All ACL tests PASS")
