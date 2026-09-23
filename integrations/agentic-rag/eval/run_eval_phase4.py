import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.hybrid_retrieve import hybrid_retrieve
from src.rerank import rerank

QUESTIONS = json.loads(Path("eval/questions.json").read_text())


def main():
    hits_at_1 = hits_at_3 = hits_at_5 = 0
    mrr_total = 0.0
    miss_count = 0

    for q in QUESTIONS:
        candidates = hybrid_retrieve(
            q["question"],
            user_clearance="CONFIDENTIAL",
            tenant_id="acme",
            top_k=20,
        )
        reranked = rerank(q["question"], candidates, top_k=5)
        retrieved_ids = [r["id"] for r in reranked]
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

        hit3 = expected & set(retrieved_ids[:3])
        if not hit3:
            miss_count += 1

        status = "HIT@3" if hit3 else "MISS"
        print(f"[{status}] {q['question'][:55]}")
        print(f"        top-3: {retrieved_ids[:3]}")

    n = len(QUESTIONS)
    print()
    print("=" * 55)
    print("Phase 2 Evaluation - Hybrid + RRF + Rerank + RBAC")
    print(f"Questions:    {n}")
    print(f"Hit Rate @ 1: {hits_at_1 / n:.2%}")
    print(f"Hit Rate @ 3: {hits_at_3 / n:.2%}")
    print(f"Hit Rate @ 5: {hits_at_5 / n:.2%}")
    print(f"MRR:          {mrr_total / n:.3f}")
    print("=" * 55)
    print(f"MISS count:   {miss_count}")


if __name__ == "__main__":
    main()