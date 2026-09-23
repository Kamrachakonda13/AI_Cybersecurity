import re
from datetime import datetime, timezone


_DATE_PATTERNS = [
    (r"\b(\d{4})-(\d{2})-(\d{2})\b", "%Y-%m-%d"),
    (r"\b(\d{2})/(\d{2})/(\d{4})\b", "%m/%d/%Y"),
    (r"\b(\d{4})/(\d{2})/(\d{2})\b", "%Y/%m/%d"),
]


def parse_date(text: str) -> dict:
    """
    Extract the first ISO date-like pattern from text and normalize to ISO 8601.
    """
    for pattern, fmt in _DATE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            try:
                dt = datetime.strptime(m.group(0), fmt).replace(tzinfo=timezone.utc)
                return {
                    "tool": "parse_date",
                    "ok": True,
                    "result": {
                        "input": text,
                        "matched": m.group(0),
                        "iso": dt.isoformat(),
                        "unix": int(dt.timestamp()),
                    },
                    "summary": f"Parsed '{m.group(0)}' as {dt.date().isoformat()}",
                    "error": None,
                }
            except ValueError:
                continue

    # Fall back to "today"
    now = datetime.now(timezone.utc)
    return {
        "tool": "parse_date",
        "ok": True,
        "result": {
            "input": text,
            "matched": None,
            "iso": now.isoformat(),
            "unix": int(now.timestamp()),
            "note": "No date found; returning current UTC time.",
        },
        "summary": f"No explicit date found; using now = {now.date().isoformat()}",
        "error": None,
    }


if __name__ == "__main__":
    import json

    for t in ["The meeting is on 2026-09-15.", "Due by 12/31/2027.", "no date here"]:
        print(json.dumps(parse_date(t), indent=2))