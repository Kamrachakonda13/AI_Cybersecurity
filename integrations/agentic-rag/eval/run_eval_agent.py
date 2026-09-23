import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent import run_agent  # noqa: E402

QUESTIONS = json.loads(Path("eval/agent_questions.json").read_text())


def main():
    correct_tool = 0
    total = len(QUESTIONS)

    for q in QUESTIONS:
        result = run_agent(q["question"], user_clearance="CONFIDENTIAL", tenant_id="acme")
        step_tools = [s["tool"] for s in result["steps"] if s["kind"] == "tool_call"]
        first_tool = step_tools[0] if step_tools else "none"
        match = first_tool == q["expected_tool"]

        if match:
            correct_tool += 1

        status = "OK" if match else "MISMATCH"
        print(f"[{status}] {q['question'][:55]}")
        print(f"          expected: {q['expected_tool']}  got: {first_tool}")
        print(f"          tool_calls: {result['tool_calls']}  latency: {result['latency_ms']} ms")
        print(f"          answer: {result['answer'][:100]}")
        print()

    print("=" * 55)
    print(f"Questions:          {total}")
    print(f"Tool routing match: {correct_tool}/{total} ({correct_tool / total:.0%})")
    print("=" * 55)


if __name__ == "__main__":
    main()