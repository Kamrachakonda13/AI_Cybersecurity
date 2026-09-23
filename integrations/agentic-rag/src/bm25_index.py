import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

CHUNKS_FILE = Path("data/chunks.json")


def tokenize(text: str):
    """Lowercase, keep alphanumeric tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Index:
    def __init__(self, chunks):
        self.chunks = chunks
        self.ids = [c["id"] for c in chunks]
        self.corpus_tokens = [tokenize(c["content"]) for c in chunks]
        self.index = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 20):
        tokens = tokenize(query)
        scores = self.index.get_scores(tokens)
        ranked = sorted(
            zip(self.ids, scores, self.chunks),
            key=lambda x: x[1],
            reverse=True,
        )
        return [
            {"id": cid, "score": float(score), "chunk": chunk}
            for cid, score, chunk in ranked[:top_k]
            if score > 0
        ]


_index = None


def get_index():
    global _index
    if _index is None:
        chunks = json.loads(CHUNKS_FILE.read_text())
        _index = BM25Index(chunks)
    return _index


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "retry policy"
    idx = get_index()
    results = idx.search(q, top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['id']}: {r['chunk']['content'][:80]}")
