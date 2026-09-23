import json
import sys
from pathlib import Path

# Add project root to sys.path so `from src.retrieve import retrieve` works
# regardless of which directory the script is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retrieve import retrieve  # noqa: E402

QUESTIONS = json.loads(Path("eval/questions.json").read_text())


def main():
    hits_at_1 = hits_at_3 = hits_at_5 = 0
    mrr_total = 0.0

    for q in QUESTIONS:
        results = retrieve(q["question"], top_k=5)
        retrieved_ids = [r["id"] for r in results]
        expected = set(q["expected_chunk_ids"])

        if expected & set(retrieved_ids[:1]):
            hits_at_1 += 1
        if expected & set(retrieved_ids[:3]):
            hits_at_3 += 1
        if expected & set(retrieved_ids[:5]):
            hits_at_5 += 1

        rr = 0.0
        for rank, cid in enumerate(retrieved_ids, start=1):
            if cid in expected:
                rr = 1.0 / rank
                break
        mrr_total += rr

        status = "HIT@3" if expected & set(retrieved_ids[:3]) else "MISS"
        print(f"[{status}] {q['question']}")
        print(f"        retrieved: {retrieved_ids}")
        print(f"        expected:  {sorted(expected)}")

    n = len(QUESTIONS)
    print()
    print("=" * 50)
    print(f"Questions:    {n}")
    print(f"Hit Rate @ 1: {hits_at_1 / n:.2%}")
    print(f"Hit Rate @ 3: {hits_at_3 / n:.2%}")
    print(f"Hit Rate @ 5: {hits_at_5 / n:.2%}")
    print(f"MRR:          {mrr_total / n:.3f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
