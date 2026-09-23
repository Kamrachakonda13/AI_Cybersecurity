import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402
from groq import Groq  # noqa: E402

from src.metrics import record_llm_call  # noqa: E402

load_dotenv()

_client = None
MODEL_NAME = "openai/gpt-oss-20b"


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("placeholder"):
            raise RuntimeError(
                "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
                "and put it in .env"
            )
        _client = Groq(api_key=api_key)
    return _client


GROUNDING_PROMPT = """You are a precise assistant. Answer the user's question using ONLY the context below.

Rules:
- If the answer is not in the context, respond exactly: "I don't know based on the provided context."
- Do not use outside knowledge.
- Cite the chunk IDs you used in brackets, e.g. [sample_001_0000].

Context:
{context}

Question: {question}

Answer:"""


def generate(question: str, chunks: list, tool: str | None = None) -> str:
    """
    Grounded generation. Records token usage in metrics.
    """
    context = "\n\n".join(
        f"[{c.get('id', 'unknown')}] {c.get('content', '')}" for c in chunks
    )
    prompt = GROUNDING_PROMPT.format(context=context, question=question)

    response = get_client().chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    # Record token usage if available
    usage = getattr(response, "usage", None)
    if usage is not None:
        record_llm_call(
            model=MODEL_NAME,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            tool=tool,
        )

    return response.choices[0].message.content


if __name__ == "__main__":
    import json

    from src.metrics import snapshot

    chunks = [
        {
            "id": "sample_001_0001",
            "content": "Failed login attempts trigger a 15-minute lockout after 5 consecutive failures.",
        }
    ]
    answer = generate("How many failed login attempts trigger a lockout?", chunks, tool="test")
    print("Answer:", answer)
    print()
    print("Metrics:", json.dumps(snapshot(), indent=2))