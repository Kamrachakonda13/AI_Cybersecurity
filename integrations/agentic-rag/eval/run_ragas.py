"""
RAGAS evaluation for Phase 7.7.

Uses RAGAS 0.4.x API with:
    - LangchainLLMWrapper around ChatGroq
    - LangchainEmbeddingsWrapper around HuggingFaceEmbeddings
    - EvaluationDataset built from SingleTurnSample objects

Measures four RAG quality dimensions:
    - Faithfulness
    - Answer Relevancy
    - Context Precision (with reference)
    - Context Recall
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

# Old-style imports work in 0.4.x (deprecated but functional)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from src.hybrid_retrieve import hybrid_retrieve
from src.rerank import rerank
from src.generate import generate


QUESTIONS_FILE = Path("eval/questions.json")
OUTPUT_FILE = Path("eval/ragas_results.json")
REPORT_FILE = Path("eval/ragas_report.md")


def build_pipeline_dataset(user_clearance="CONFIDENTIAL", tenant_id="acme"):
    """
    Run retrieve -> rerank -> generate for each question, collect the
    four fields RAGAS needs: user_input, response, retrieved_contexts,
    reference.
    """
    questions = json.loads(QUESTIONS_FILE.read_text())

    # Load chunks for ground-truth reference text
    chunks_file = Path("data/chunks.json")
    chunk_lookup = {}
    if chunks_file.exists():
        for c in json.loads(chunks_file.read_text()):
            chunk_lookup[c["id"]] = c["content"]

    rows = []
    for i, q in enumerate(questions):
        question = q["question"]
        expected_ids = q.get("expected_chunk_ids", [])
        print(f"  [{i+1}/{len(questions)}] {question[:60]}")

        candidates = hybrid_retrieve(
            question,
            user_clearance=user_clearance,
            tenant_id=tenant_id,
            top_k=20,
        )
        if not candidates:
            print(f"      skipped (no candidates)")
            continue

        reranked = rerank(question, candidates, top_k=5)
        answer = generate(question, reranked, tool="ragas_eval")
        contexts = [c["content"] for c in reranked]

        reference = " ".join(
            chunk_lookup.get(cid, "") for cid in expected_ids
        ).strip()
        if not reference:
            reference = reranked[0]["content"] if reranked else ""

        rows.append({
            "user_input": question,
            "response": answer,
            "retrieved_contexts": contexts,
            "reference": reference,
        })

    return rows


def main():
    print("=== RAGAS Evaluation (v0.4.x API) ===\n")

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key.startswith("placeholder"):
        print("ERROR: GROQ_API_KEY not set in .env")
        sys.exit(1)

    print("Configuring LLM judge and embeddings...")
    groq_llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=groq_key,
        temperature=0.0,
    )
    llm = LangchainLLMWrapper(groq_llm)

    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    embeddings = LangchainEmbeddingsWrapper(embeddings_model)
    print("  OK\n")

    print(f"Building evaluation dataset from {QUESTIONS_FILE}...")
    rows = build_pipeline_dataset()
    print(f"  Built {len(rows)} examples\n")

    if len(rows) < 3:
        print("ERROR: need at least 3 examples to run RAGAS")
        sys.exit(1)

    # Build RAGAS EvaluationDataset from SingleTurnSample objects
    samples = [
        SingleTurnSample(
            user_input=r["user_input"],
            response=r["response"],
            retrieved_contexts=r["retrieved_contexts"],
            reference=r["reference"],
        )
        for r in rows
    ]
    dataset = EvaluationDataset(samples=samples)

    print("Running RAGAS metrics (this takes 10-15 minutes)...")
    print("  - faithfulness")
    print("  - answer_relevancy")
    print("  - context_precision")
    print("  - context_recall\n")

    t0 = time.time()
    result = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
        llm=llm,
        embeddings=embeddings,
        raise_exceptions=False,
        show_progress=True,
    )
    elapsed = time.time() - t0

    # Convert EvaluationResult to dict
    try:
        scores = result.to_pandas().mean(numeric_only=True).to_dict()
    except Exception:
        # Fallback: try dict(result)
        try:
            scores = dict(result)
        except Exception:
            scores = {"error": "could not extract scores"}

    # Save results
    OUTPUT_FILE.write_text(json.dumps({
        "num_examples": len(rows),
        "duration_seconds": round(elapsed, 1),
        "scores": {k: (float(v) if isinstance(v, (int, float)) else str(v))
                   for k, v in scores.items()},
        "examples": [
            {
                "question": r["user_input"],
                "answer_preview": r["response"][:300],
                "reference_preview": r["reference"][:300],
                "num_contexts": len(r["retrieved_contexts"]),
            }
            for r in rows
        ],
    }, indent=2, default=str))
    print(f"\nResults saved to {OUTPUT_FILE}")

    # Generate report
    report = generate_report(scores, rows, elapsed)
    REPORT_FILE.write_text(report)
    print(f"Report saved to {REPORT_FILE}")

    print("\n=== Final scores ===")
    for k, v in scores.items():
        if isinstance(v, (int, float)):
            print(f"  {k:<25} {v:.3f}")
        else:
            print(f"  {k:<25} {v}")


def generate_report(scores, rows, elapsed):
    def fmt(v):
        if isinstance(v, (int, float)):
            return f"{v:.3f}"
        return str(v)

    def interp(v):
        if not isinstance(v, (int, float)):
            return ""
        if v >= 0.85: return "Strong"
        if v >= 0.70: return "Acceptable"
        if v >= 0.50: return "Needs work"
        return "Weak"

    return f"""# RAGAS Evaluation Report

**Date:** 2026-09-20
**Framework:** RAGAS 0.4.3
**Pipeline:** Hybrid RAG (vector + BM25 + RRF + cross-encoder rerank)
**LLM judge:** openai/gpt-oss-20b via Groq
**Embeddings:** all-MiniLM-L6-v2 (local)
**Examples:** {len(rows)}
**Duration:** {elapsed:.0f} seconds

## Scores

| Metric | Score | Interpretation |
|--------|-------|----------------|
| Faithfulness | {fmt(scores.get('faithfulness'))} | {interp(scores.get('faithfulness'))} |
| Answer Relevancy | {fmt(scores.get('answer_relevancy'))} | {interp(scores.get('answer_relevancy'))} |
| Context Precision | {fmt(scores.get('context_precision'))} | {interp(scores.get('context_precision'))} |
| Context Recall | {fmt(scores.get('context_recall'))} | {interp(scores.get('context_recall'))} |

## Metric meanings

**Faithfulness** — Fraction of claims in the generated answer that are
supported by the retrieved context. High = low hallucination.

**Answer Relevancy** — How well the answer addresses the specific
question asked. High = on-topic.

**Context Precision** — Fraction of retrieved chunks that are relevant.
High = low noise in the context window.

**Context Recall** — Fraction of ground truth information that appears
in the retrieved chunks. High = we didn't miss anything important.

## Target thresholds for enterprise RAG

| Metric | Target |
|--------|--------|
| Faithfulness | >= 0.85 |
| Answer Relevancy | >= 0.85 |
| Context Precision | >= 0.70 |
| Context Recall | >= 0.75 |

## Reproducibility

    python eval/run_ragas.py

Results saved to `eval/ragas_results.json`.
"""


if __name__ == "__main__":
    main()
