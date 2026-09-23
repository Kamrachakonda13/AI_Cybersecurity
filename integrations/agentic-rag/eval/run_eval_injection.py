"""
Phase 9.2b / 9.6 — Prompt injection classifier benchmark.

Runs the classifier (baseline or embedding) against:
  - data/security/injections_test.jsonl  (held-out injections)
  - data/security/benign_test.jsonl      (benign)

Reports:
  - Detection rate (recall on injections)
  - False positive rate (on benign)
  - Per-category detection breakdown
  - Missed injections (evasion vectors)
  - False positives (over-blocking)

Usage:
  python -m eval.run_eval_injection              # baseline classifier
  python -m eval.run_eval_injection --classifier embedding
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DATA_DIR = Path("data/security")
RESULTS_JSON = Path("eval/results_injection_baseline.json")
RESULTS_MD = Path("eval/results_phase9.md")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def get_classifier(name: str):
    if name == "baseline":
        from src.security.injection_patterns import classify as baseline
        return baseline
    if name == "embedding":
        from src.security.injection_classifier import classify as embedding
        return embedding
    raise ValueError(f"unknown classifier: {name}")


def evaluate(classifier_name: str):
    classifier = get_classifier(classifier_name)

    injections = load_jsonl(DATA_DIR / "injections_test.jsonl")
    benign = load_jsonl(DATA_DIR / "benign_test.jsonl")

    print(f"Classifier: {classifier_name}")
    print(f"Injections (test): {len(injections)}")
    print(f"Benign (test):     {len(benign)}")
    print()

    # --- injections ---
    missed = []
    caught_by_cat = Counter()
    total_by_cat = Counter()
    for item in injections:
        v = classifier(item["prompt"])
        total_by_cat[item["category"]] += 1
        if v.is_injection:
            caught_by_cat[item["category"]] += 1
        else:
            missed.append(item)

    # --- benign ---
    false_positives = []
    for item in benign:
        v = classifier(item["prompt"])
        if v.is_injection:
            false_positives.append({**item, "predicted_category": v.category})

    tp = sum(caught_by_cat.values())
    fn = len(missed)
    fp = len(false_positives)
    tn = len(benign) - fp

    detection_rate = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn)

    print("=" * 60)
    print(f"Detection rate:        {detection_rate*100:.1f}%  ({tp}/{tp+fn})")
    print(f"False positive rate:   {fpr*100:.1f}%  ({fp}/{fp+tn})")
    print(f"Precision:             {precision*100:.1f}%")
    print(f"Accuracy:              {accuracy*100:.1f}%")
    print()
    print("Per-category detection:")
    for cat in sorted(total_by_cat):
        c = caught_by_cat[cat]
        t = total_by_cat[cat]
        print(f"  {cat:<26} {c}/{t}  ({c/t*100:.0f}%)")

    # --- write results ---
    summary = {
        "classifier": classifier_name,
        "total_injections": len(injections),
        "total_benign": len(benign),
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        "detection_rate": round(detection_rate, 4),
        "false_positive_rate": round(fpr, 4),
        "precision": round(precision, 4),
        "accuracy": round(accuracy, 4),
        "per_category": {
            cat: {"caught": caught_by_cat[cat], "total": total_by_cat[cat]}
            for cat in sorted(total_by_cat)
        },
    }

    RESULTS_JSON.write_text(json.dumps({
        "summary": summary,
        "missed": [{"id": m["id"], "category": m["category"], "prompt": m["prompt"]} for m in missed],
        "false_positives": [{"id": m["id"], "category": m["category"], "prompt": m["prompt"]} for m in false_positives],
    }, indent=2))

    print()
    print(f"Wrote {RESULTS_JSON}")
    print()
    print("Missed injections (evasion vectors):")
    for m in missed[:10]:
        print(f"  [{m['category']}] {m['prompt'][:80]}")
    if not missed:
        print("  (none)")
    print()
    print("False positives (over-blocked benign):")
    for m in false_positives[:10]:
        print(f"  [{m['category']}] {m['prompt'][:80]}")
    if not false_positives:
        print("  (none)")

    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classifier", default="baseline", choices=["baseline", "embedding"])
    args = ap.parse_args()
    evaluate(args.classifier)


if __name__ == "__main__":
    main()
