import json
from pathlib import Path

CLEAN = Path("data/clean")
CHUNKS_FILE = Path("data/chunks.json")

CHUNK_SIZE = 400
OVERLAP = 50

# Clearance hierarchy: PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED
CLEARANCE_BY_FILE = {
    "sample_001.md": "INTERNAL",       # Authentication policy
    "sample_002.md": "PUBLIC",         # Retry policy (general API info)
    "sample_003.md": "CONFIDENTIAL",   # Data retention (regulatory)
    "sample_004.md": "PUBLIC",         # Monitoring
    "sample_005.md": "INTERNAL",       # Deployment procedures
    "sample_006.md": "INTERNAL",       # Security incident response
}

DEFAULT_TENANT = "acme"


def chunk_text(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            last_period = text.rfind(".", start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
    return chunks


def main():
    all_chunks = []
    files = sorted(CLEAN.glob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        clearance = CLEARANCE_BY_FILE.get(path.name, "INTERNAL")
        for i, chunk in enumerate(chunk_text(text, CHUNK_SIZE, OVERLAP)):
            if len(chunk) < 50:
                continue
            all_chunks.append({
                "id": f"{path.stem}_{i:04d}",
                "source_file": path.name,
                "chunk_index": i,
                "content": chunk,
                "clearance_level": clearance,
                "tenant_id": DEFAULT_TENANT,
            })

    CHUNKS_FILE.write_text(json.dumps(all_chunks, indent=2))
    print(f"Created {len(all_chunks)} chunks from {len(files)} files")
    for c in all_chunks[:5]:
        print(
            f"  {c['id']}: clearance={c['clearance_level']}, tenant={c['tenant_id']}")


if __name__ == "__main__":
    main()
