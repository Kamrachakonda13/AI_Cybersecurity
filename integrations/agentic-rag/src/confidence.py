import os
import re

from dotenv import load_dotenv

load_dotenv()

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.0"))
MIN_CHUNKS = int(os.getenv("MIN_CHUNKS", "1"))

HARD_TOKEN_PATTERN = re.compile(
    r"\b(CVE-\d{4}-\d{4,7}|T\d{4}(?:\.\d{3})?|\w*[A-Z]+\w*\d+\w*)\b"
)


def evaluate_confidence(reranked_chunks: list) -> dict:
    if not reranked_chunks:
        return {
            "confident": False,
            "top_score": None,
            "num_chunks": 0,
            "reason": "No chunks retrieved.",
        }

    top_score = reranked_chunks[0].get("rerank_score")

    if top_score is None:
        return {
            "confident": len(reranked_chunks) >= MIN_CHUNKS,
            "top_score": None,
            "num_chunks": len(reranked_chunks),
            "reason": "No rerank scores; using count-only confidence check.",
        }

    if len(reranked_chunks) < MIN_CHUNKS:
        return {
            "confident": False,
            "top_score": float(top_score),
            "num_chunks": len(reranked_chunks),
            "reason": f"Fewer than {MIN_CHUNKS} chunks retrieved.",
        }

    if top_score < CONFIDENCE_THRESHOLD:
        return {
            "confident": False,
            "top_score": float(top_score),
            "num_chunks": len(reranked_chunks),
            "reason": f"Top rerank score {top_score:.3f} is below threshold {CONFIDENCE_THRESHOLD}.",
        }

    return {
        "confident": True,
        "top_score": float(top_score),
        "num_chunks": len(reranked_chunks),
        "reason": f"Top rerank score {top_score:.3f} exceeds threshold.",
    }


def evaluate_graph_confidence(edges: list) -> dict:
    if not edges:
        return {
            "confident": False,
            "num_edges": 0,
            "reason": "Graph traversal returned zero edges.",
        }
    return {
        "confident": True,
        "num_edges": len(edges),
        "reason": f"Graph traversal returned {len(edges)} edges.",
    }


def check_query_coverage(query: str, chunks: list) -> dict:
    """
    Check whether the retrieved chunks contain the 'hard' tokens in the query.
    Hard tokens: CVE IDs, ATT&CK technique IDs, or tokens with digits.
    """
    hard_tokens = set(m.group(0) for m in HARD_TOKEN_PATTERN.finditer(query))

    if not hard_tokens:
        return {
            "covered": True,
            "hard_tokens": [],
            "missing_tokens": [],
            "reason": "No hard tokens in query; coverage not applicable.",
        }

    corpus_text = " ".join((c.get("content") or "") for c in chunks).lower()
    missing = [tok for tok in hard_tokens if tok.lower() not in corpus_text]

    if missing:
        return {
            "covered": False,
            "hard_tokens": sorted(hard_tokens),
            "missing_tokens": sorted(missing),
            "reason": f"Retrieved chunks do not contain query tokens: {sorted(missing)}",
        }

    return {
        "covered": True,
        "hard_tokens": sorted(hard_tokens),
        "missing_tokens": [],
        "reason": "All hard tokens present in retrieved chunks.",
    }


if __name__ == "__main__":
    strong = [{"id": "a", "rerank_score": 8.5}, {"id": "b", "rerank_score": 3.2}]
    weak = [{"id": "a", "rerank_score": -7.0}, {"id": "b", "rerank_score": -9.5}]
    empty = []

    print("Strong:", evaluate_confidence(strong))
    print("Weak:", evaluate_confidence(weak))
    print("Empty:", evaluate_confidence(empty))
    print()
    print("Graph empty:", evaluate_graph_confidence([]))
    print("Graph strong:", evaluate_graph_confidence([{"source": "a", "target": "b"}]))
    print()
    q = "What is CVE-2021-44228?"
    chunks_hit = [{"content": "CVE-2021-44228 Apache Log4j2 Remote Code Execution"}]
    chunks_miss = [{"content": "CVE-2018-0802 Microsoft Office vulnerability"}]
    print("Coverage hit:", check_query_coverage(q, chunks_hit))
    print("Coverage miss:", check_query_coverage(q, chunks_miss))