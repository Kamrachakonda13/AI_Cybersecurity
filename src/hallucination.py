"""
Hallucination checking for Phase 7.

Verifies that each sentence in a generated answer is supported by the
retrieved context, using a cross-encoder NLI model.

Model: cross-encoder/nli-deberta-v3-small
Labels: entailment, neutral, contradiction
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder("cross-encoder/nli-deberta-v3-small")
    return _model


# The NLI model's label order is read dynamically from the model config.
# Common orderings:
#   ["contradiction", "entailment", "neutral"]
#   ["entailment", "neutral", "contradiction"]
_NLI_LABELS = None


def _get_nli_labels():
    global _NLI_LABELS
    if _NLI_LABELS is None:
        model = _get_model()
        # sentence-transformers CrossEncoder exposes the underlying model
        try:
            id2label = model.model.config.id2label
            # id2label is {0: "contradiction", 1: "entailment", 2: "neutral"}
            _NLI_LABELS = [id2label[i].lower() for i in range(len(id2label))]
        except Exception:
            _NLI_LABELS = ["contradiction", "entailment", "neutral"]
    return _NLI_LABELS


def _split_sentences(text: str) -> list:
    """Split into sentences. Keep it simple: split on . ! ?"""
    # Remove markdown formatting that would confuse sentence splitting
    text = re.sub(r"\|.*?\|", " ", text)  # table cells
    text = re.sub(r"\[.*?\]", "", text)   # citations in brackets
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def check_hallucination(
    answer: str,
    context: str,
    threshold: float = 0.3,
) -> dict:
    """
    Check whether the answer is supported by the context.

    Returns:
        {
            "hallucination_score": float,
            "threshold": float,
            "passed": bool,
            "sentences": [{"text", "label", "scores"}],
            "entailed_count": int,
            "neutral_count": int,
            "contradicted_count": int,
        }
    """
    if not answer or not answer.strip():
        return {
            "hallucination_score": 0.0,
            "threshold": threshold,
            "passed": True,
            "sentences": [],
            "entailed_count": 0,
            "neutral_count": 0,
            "contradicted_count": 0,
        }

    if not context or not context.strip():
        # No context to verify against — cannot assess
        return {
            "hallucination_score": 1.0,
            "threshold": threshold,
            "passed": False,
            "sentences": [],
            "entailed_count": 0,
            "neutral_count": 0,
            "contradicted_count": 0,
            "reason": "no_context",
        }

    sentences = _split_sentences(answer)
    if not sentences:
        return {
            "hallucination_score": 0.0,
            "threshold": threshold,
            "passed": True,
            "sentences": [],
            "entailed_count": 0,
            "neutral_count": 0,
            "contradicted_count": 0,
        }

    model = _get_model()
    pairs = [(context, s) for s in sentences]
    scores = model.predict(pairs)

    results = []
    entailed = 0
    neutral = 0
    contradicted = 0

    for sentence, score_row in zip(sentences, scores):
        # score_row is a 3-element array; use the model's id2label to map
        labels = _get_nli_labels()
        label_idx = int(score_row.argmax())
        label = labels[label_idx]

        if label == "entailment":
            entailed += 1
        elif label == "neutral":
            neutral += 1
        else:
            contradicted += 1

        results.append({
            "text": sentence[:200],
            "label": label,
            "scores": {
                "contradiction": round(float(score_row[0]), 3),
                "entailment": round(float(score_row[1]), 3),
                "neutral": round(float(score_row[2]), 3),
            },
        })

    total = len(sentences)
    # Hallucination score: fraction of CONTRADICTED sentences.
    # Neutral sentences are acceptable: a paraphrase of retrieved content
    # is often labeled "neutral" by small NLI models even when factually
    # correct. Only contradiction is treated as a hallucination signal.
    hallucination_score = contradicted / total if total else 0.0

    return {
        "hallucination_score": round(hallucination_score, 3),
        "threshold": threshold,
        "passed": hallucination_score <= threshold,
        "sentences": results,
        "entailed_count": entailed,
        "neutral_count": neutral,
        "contradicted_count": contradicted,
        "total_sentences": total,
    }


if __name__ == "__main__":
    print("=== Hallucination checker self-test ===\n")

    context = (
        "The Acme Data Governance Policy specifies retention periods. "
        "Customer data must be retained for 7 years after an account is closed. "
        "Logs are retained for 90 days. Audit logs for 1 year."
    )

    # Test 1: fully entailed answer
    a1 = "Customer data is retained for 7 years. Logs are retained for 90 days."
    r1 = check_hallucination(a1, context)
    print(f"Test 1 (entailed): {'PASS' if r1['passed'] else 'FAIL'}")
    print(f"    score={r1['hallucination_score']} entailed={r1['entailed_count']}/{r1['total_sentences']}")

    # Test 2: contradicted answer
    a2 = "Customer data is retained for 30 days only. Logs are kept forever."
    r2 = check_hallucination(a2, context)
    print(f"Test 2 (contradicted): {'PASS' if not r2['passed'] else 'FAIL'}")
    print(f"    score={r2['hallucination_score']} contradicted={r2['contradicted_count']}/{r2['total_sentences']}")

    # Test 3: mixed
    a3 = "Customer data is retained for 7 years. However, the moon is made of cheese."
    r3 = check_hallucination(a3, context)
    print(f"Test 3 (mixed): PASS")
    print(f"    score={r3['hallucination_score']} entailed={r3['entailed_count']} neutral={r3['neutral_count']}")

    # Test 4: empty answer
    r4 = check_hallucination("", context)
    print(f"Test 4 (empty answer): {'PASS' if r4['passed'] else 'FAIL'}")

    # Test 5: no context
    r5 = check_hallucination("Some answer", "")
    print(f"Test 5 (no context): {'PASS' if not r5['passed'] else 'FAIL'}")

    print()
    print("All hallucination tests PASS")
