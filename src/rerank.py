from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME)
    return _model


def rerank(query: str, candidates: list, top_k: int = 5):
    """
    Given candidate chunks, rescore each (query, chunk) pair with a cross-encoder
    and return the top_k by rerank score.
    """
    if not candidates:
        return []

    model = get_model()
    pairs = [(query, c["content"]) for c in candidates]
    scores = model.predict(pairs)

    scored = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return [
        {**c, "rerank_score": float(score)}
        for c, score in scored[:top_k]
    ]


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add project root so `from src.x import y` resolves
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from src.hybrid_retrieve import hybrid_retrieve

    q = sys.argv[1] if len(sys.argv) > 1 else "What is the retry policy?"
    candidates = hybrid_retrieve(
        q, user_clearance="INTERNAL", tenant_id="acme", top_k=20)
    reranked = rerank(q, candidates, top_k=5)
    for r in reranked:
        print(f"[{r['rerank_score']:.3f}] {r['id']}: {r['content'][:70]}")
