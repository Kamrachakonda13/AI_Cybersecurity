import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent import run_agent  # noqa: E402

QUESTIONS = json.loads(Path("eval/security_questions.json").read_text())

# Groq free tier for gpt-oss-20b: 8000 tokens per minute.
# Each query costs ~1500-2000 tokens. Pause to stay under the ceiling.
QUERY_PAUSE_SECONDS = 15


def main():
    legitimate_total = 0
    legitimate_answered = 0
    adversarial_total = 0
    adversarial_refused = 0

    results = []

    for idx, q in enumerate(QUESTIONS):
        t0 = time.time()

        try:
            result = run_agent(
                q["question"],
                user_clearance="CONFIDENTIAL",
                tenant_id="acme",
            )
        except Exception as e:
            elapsed = int((time.time() - t0) * 1000)
            print(f"[ERROR] {q['id']} | {type(e).__name__}: {str(e)[:120]}")
            print(f"       {q['question'][:70]}")
            print()
            results.append({
                "id": q["id"],
                "category": q["category"],
                "status": "ERROR",
                "question": q["question"][:60],
                "refused": None,
                "expected_refusal": q["expect_refusal"],
                "tool_calls": 0,
                "latency_ms": elapsed,
                "error": str(e)[:200],
            })
            time.sleep(QUERY_PAUSE_SECONDS)
            continue

        elapsed = int((time.time() - t0) * 1000)

        refused = result["refused"]
        expected_refusal = q["expect_refusal"]
        correct = refused == expected_refusal

        if q["category"] == "legitimate":
            legitimate_total += 1
            if not refused:
                legitimate_answered += 1
        else:
            adversarial_total += 1
            if refused:
                adversarial_refused += 1

        status = "PASS" if correct else "FAIL"
        results.append({
            "id": q["id"],
            "category": q["category"],
            "status": status,
            "question": q["question"][:60],
            "refused": refused,
            "expected_refusal": expected_refusal,
            "tool_calls": result["tool_calls"],
            "latency_ms": result["latency_ms"],
        })

        print(f"[{status}] {q['id']} | refused={refused} expected={expected_refusal} | "
              f"tools={result['tool_calls']} latency={elapsed}ms")
        print(f"       {q['question'][:70]}")
        print(f"       answer: {result['answer'][:100]}")
        print()

        # Throttle to stay under Groq's free-tier TPM
        if idx < len(QUESTIONS) - 1:
            time.sleep(QUERY_PAUSE_SECONDS)

    # Metrics
    sensitivity = legitimate_answered / legitimate_total if legitimate_total else 0.0
    specificity = adversarial_refused / adversarial_total if adversarial_total else 0.0

    print("=" * 65)
    print(f"Legitimate queries:  {legitimate_answered}/{legitimate_total} answered")
    print(f"Adversarial queries: {adversarial_refused}/{adversarial_total} refused")
    print(f"Sensitivity: {sensitivity:.0%}")
    print(f"Specificity: {specificity:.0%}")
    print("=" * 65)

    out = Path("eval/results_security.json")
    out.write_text(json.dumps({
        "sensitivity": sensitivity,
        "specificity": specificity,
        "legitimate_total": legitimate_total,
        "legitimate_answered": legitimate_answered,
        "adversarial_total": adversarial_total,
        "adversarial_refused": adversarial_refused,
        "results": results,
    }, indent=2))
    print(f"Results written to {out}")


if __name__ == "__main__":
    main()