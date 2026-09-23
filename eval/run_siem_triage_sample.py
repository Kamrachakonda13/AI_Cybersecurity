"""
Phase 8.5 — Sample triage run.

Runs the LLM triage on a small, deterministic subset of incidents so
we can validate the prompt and the output schema before spending
quota on the full 122.

Sample selection (deterministic, seed 42):
  - 3 largest multi-alert incidents
  - 2 random singletons

Prints a decision table for manual review.
"""
import json
import random
import sys
from pathlib import Path

# Path shim so `python eval/run_siem_triage_sample.py` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.siem_ingest import load_alerts
from src.siem_correlate import correlate
from src.siem_triage import triage_incident, build_incident_prompt


def main():
    rng = random.Random(42)

    alerts = load_alerts()
    incidents = correlate(alerts)

    multi = sorted([i for i in incidents if i.size > 1], key=lambda i: -i.size)
    singles = [i for i in incidents if i.size == 1]

    sample = multi[:3] + rng.sample(singles, 2)

    print(f"Triaging {len(sample)} incidents (3 largest + 2 random singletons)")
    print("=" * 78)

    for inc in sample:
        print(f"\n[{inc.incident_id}] size={inc.size} severity={inc.severity} "
              f"host={inc.primary_entity['host']} user={inc.primary_entity['user']}")
        print(f"  ground_truth: {inc.ground_truth_summary()}")

        decision = triage_incident(inc)

        print(f"  → {decision.decision}  (confidence: {decision.confidence:.2f})")
        print(f"  → reason: {decision.reason}")

        # Simple correctness check for the sample
        truth = inc.ground_truth_summary()
        if truth == "TRUE_POSITIVE" and decision.decision == "ESCALATE":
            print("  ✓ correct (TP escalated)")
        elif truth == "FALSE_POSITIVE" and decision.decision == "SUPPRESS":
            print("  ✓ correct (FP suppressed)")
        else:
            print(f"  ✗ mismatch (truth={truth}, decision={decision.decision})")

    print("\n" + "=" * 78)
    print("Done. Review the outputs above before running the full benchmark.")


if __name__ == "__main__":
    main()
