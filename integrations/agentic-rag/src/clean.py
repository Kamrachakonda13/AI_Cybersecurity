import re
from pathlib import Path
from bs4 import BeautifulSoup

RAW = Path("data/raw")
CLEAN = Path("data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def main():
    count = 0
    for path in sorted(RAW.glob("*.md")):
        cleaned = clean_text(path.read_text(encoding="utf-8"))
        (CLEAN / path.name).write_text(cleaned, encoding="utf-8")
        print(f"Cleaned {path.name}: {len(cleaned)} chars")
        count += 1
    print(f"Done. Cleaned {count} files.")


if __name__ == "__main__":
    main()
