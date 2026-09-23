"""
Cross-silo discovery benchmark for Phase 6.

Measures three properties:
  1. Hit rate            - the user has permission and correct content returned
  2. Correctly denied    - the user lacks permission and gets an empty result
  3. Cross-silo rate     - fraction of results from teams other than user's own

Correctness is measured as:
  - HIT if the must_contain keyword appears in any result
  - CORRECTLY DENIED if the query requires a clearance the user lacks AND
    the result set is empty
  - MISS otherwise
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.federated_search import federated_search  # noqa: E402


# Each query declares the minimum clearance required to retrieve the answer.
# If the user's clearance is below that, an empty result is "correctly denied".
QUERIES = [
    {
        "query": "deployment runbook",
        "must_contain": "deployment",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "security policy",
        "must_contain": "policy",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "observability vendor",
        "must_contain": "observability",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "onboarding playbook",
        "must_contain": "onboarding",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "incident postmortem",
        "must_contain": "incident",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "kubernetes migration",
        "must_contain": "kubernetes",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "api retry policy",
        "must_contain": "retry",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "churn analysis",
        "must_contain": "churn",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "financial close",
        "must_contain": "financial",
        "min_clearance": "CONFIDENTIAL",
    },
    {
        "query": "schema registry",
        "must_contain": "schema",
        "min_clearance": "INTERNAL",
    },
    {
        "query": "marketing FAQ",
        "must_contain": "acme",
        "min_clearance": "PUBLIC",
    },
]


CLEARANCE_RANK = {"PUBLIC": 1, "INTERNAL": 2, "CONFIDENTIAL": 3, "RESTRICTED": 4}


USERS = [
    {
        "user_id": "alice@acme.com", "role": "csuite", "tenant_id": "acme",
        "clearance": "CONFIDENTIAL", "teams": ["executive"],
        "label": "csuite/executive",
    },
    {
        "user_id": "bob@acme.com", "role": "manager", "tenant_id": "acme",
        "clearance": "INTERNAL", "teams": ["platform"],
        "label": "manager/platform",
    },
    {
        "user_id": "carol@acme.com", "role": "junior", "tenant_id": "acme",
        "clearance": "PUBLIC", "teams": ["product"],
        "label": "junior/product",
    },
]


def _has_clearance(user: dict, required: str) -> bool:
    return CLEARANCE_RANK[user["clearance"]] >= CLEARANCE_RANK[required]


def evaluate_user(user: dict) -> dict:
    per_query = []
    hits = 0
    correctly_denied = 0
    misses = 0
    total_cross_silo = 0
    total_results = 0

    for q in QUERIES:
        result = federated_search(q["query"], user, top_k=20, final_k=5)
        results = result["results"]

        # Correctness classification
        hit = False
        for r in results:
            content_lower = (r.get("content") or "").lower()
            if q["must_contain"].lower() in content_lower:
                hit = True
                break

        has_clearance = _has_clearance(user, q["min_clearance"])

        if hit:
            status = "HIT"
            hits += 1
        elif not has_clearance and len(results) == 0:
            status = "DENIED"
            correctly_denied += 1
        elif not has_clearance and len(results) > 0:
            # User lacks clearance but got some results anyway. This is fine
            # if the results are filtered correctly, but the benchmark treats
            # it as a miss because the answer wasn't found.
            status = "MISS"
            misses += 1
        else:
            status = "MISS"
            misses += 1

        # Cross-silo
        cross_silo_count = 0
        user_teams = set(user.get("teams", []))
        for r in results:
            source_team = r.get("owner_team", "")
            if source_team and source_team not in user_teams:
                cross_silo_count += 1

        total_cross_silo += cross_silo_count
        total_results += len(results)

        per_query.append({
            "query": q["query"],
            "status": status,
            "result_count": len(results),
            "cross_silo_results": cross_silo_count,
            "user_has_clearance": has_clearance,
            "required_clearance": q["min_clearance"],
        })

    n = len(QUERIES)
    return {
        "user": user["label"],
        "hit_rate": hits / n if n else 0.0,
        "correctly_denied_rate": correctly_denied / n if n else 0.0,
        "miss_rate": misses / n if n else 0.0,
        "hits": hits,
        "correctly_denied": correctly_denied,
        "misses": misses,
        "cross_silo_rate": total_cross_silo / total_results if total_results else 0.0,
        "total_results": total_results,
        "per_query": per_query,
    }


def main():
    print("=" * 70)
    print("Phase 6.15 - Cross-silo discovery benchmark")
    print("=" * 70)
    print()

    summaries = []
    for user in USERS:
        result = evaluate_user(user)
        summaries.append(result)

        print(f"User: {result['user']}")
        print(f"  Hit rate:             {result['hit_rate']:.0%}  ({result['hits']} hits)")
        print(f"  Correctly denied:     {result['correctly_denied_rate']:.0%}  ({result['correctly_denied']} denied)")
        print(f"  Miss rate:            {result['miss_rate']:.0%}  ({result['misses']} misses)")
        print(f"  Cross-silo rate:      {result['cross_silo_rate']:.0%}")
        print(f"  Total results:        {result['total_results']}")
        print()

        for pq in result["per_query"]:
            print(f"    [{pq['status']:<6}] {pq['query']:<22} "
                  f"results={pq['result_count']} "
                  f"cross-silo={pq['cross_silo_results']} "
                  f"required={pq['required_clearance']}")
        print()
        print("-" * 70)
        print()

    avg_hit = sum(s["hit_rate"] for s in summaries) / len(summaries)
    avg_denied = sum(s["correctly_denied_rate"] for s in summaries) / len(summaries)
    avg_miss = sum(s["miss_rate"] for s in summaries) / len(summaries)

    # Weighted cross-silo: only over users who actually received results
    total_cross_silo = sum(s["total_results"] * s["cross_silo_rate"] for s in summaries)
    total_results_all = sum(s["total_results"] for s in summaries)
    overall_cross_silo = total_cross_silo / total_results_all if total_results_all else 0.0

    print()
    print("=" * 70)
    print("Overall")
    print("=" * 70)
    print(f"Average hit rate:             {avg_hit:.0%}")
    print(f"Average correctly denied:     {avg_denied:.0%}")
    print(f"Average miss rate:            {avg_miss:.0%}")
    print(f"Overall cross-silo rate:      {overall_cross_silo:.0%}")
    print("=" * 70)

    out = Path("eval/results_cross_silo.json")
    out.write_text(json.dumps({
        "average_hit_rate": avg_hit,
        "average_correctly_denied_rate": avg_denied,
        "average_miss_rate": avg_miss,
        "overall_cross_silo_rate": overall_cross_silo,
        "per_user": summaries,
    }, indent=2))
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
