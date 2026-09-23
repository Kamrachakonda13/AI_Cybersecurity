"""
Content fingerprinting for Phase 6.

Computes canonical SHA-256 hashes of document content so that the same
content, ingested from two different sources, produces the same fingerprint.

Two fingerprints per document:

    content_fingerprint:
        hash of normalized text content only.
        Used for cross-source deduplication.
        Two documents with identical content but different titles,
        owners, or source paths produce the same content_fingerprint.

    exact_fingerprint:
        hash of normalized content PLUS the source_system and source_id.
        Used for idempotent re-ingestion.
        Same document re-ingested from the same source produces the same
        exact_fingerprint, so the pipeline can skip it.

Normalization rules are versioned. When the rules change, all stored
fingerprints must be recomputed. The version prefix on every fingerprint
("fp:v1:...") makes this explicit.

Fail-closed behavior: an empty or whitespace-only content string produces
no fingerprint (returns None). Callers must handle this.
"""

import hashlib
import re
import unicodedata
from typing import Optional


# Bump this when normalization rules change. Stored fingerprints with an
# older version must be recomputed.
NORMALIZATION_VERSION = "v1"


# ---------------------------------------------------------------------------
# Unicode normalization
# ---------------------------------------------------------------------------

# Common typographic characters mapped to their ASCII equivalents.
# Google Drive, SharePoint, Word, and Notion all emit different Unicode
# variants of the same visible character. Normalizing them prevents
# false "different content" results.
_TYPOGRAPHIC_MAP = {
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u2026": "...", # ellipsis
    "\u00a0": " ",   # non-breaking space
    "\u200b": "",    # zero-width space
    "\u200c": "",    # zero-width non-joiner
    "\u200d": "",    # zero-width joiner
    "\ufeff": "",    # byte-order mark
}


def _normalize_unicode(text: str) -> str:
    """Apply NFKC normalization, then replace typographic chars with ASCII."""
    # NFKC handles composed vs decomposed forms (é vs e + combining accent)
    text = unicodedata.normalize("NFKC", text)
    for original, replacement in _TYPOGRAPHIC_MAP.items():
        text = text.replace(original, replacement)
    return text


# ---------------------------------------------------------------------------
# Whitespace and formatting normalization
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCTUATION_TAIL_RE = re.compile(r"[.!?,;:]+\s*$")


def _normalize_whitespace(text: str) -> str:
    """Collapse all runs of whitespace (including newlines) to a single space."""
    return _WHITESPACE_RE.sub(" ", text)


def _normalize_markdown(text: str) -> str:
    """
    Strip common markdown formatting that is cosmetic, not semantic.
    Headers, bold/italic markers, list bullets, code fences.
    """
    # Remove code fences but keep the code inside
    text = re.sub(r"```[a-zA-Z0-9_-]*\n", "", text)
    text = text.replace("```", "")

    # Remove bold/italic markers
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)

    # Remove header markers but keep the text
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove list markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    return text


# ---------------------------------------------------------------------------
# Main normalization
# ---------------------------------------------------------------------------

def normalize_content(
    text: str,
    *,
    strip_markdown: bool = True,
    lowercase: bool = True,
    collapse_whitespace: bool = True,
    strip_trailing_punctuation: bool = False,
) -> str:
    """
    Apply the full normalization pipeline to content.

    Default behavior (all flags True except strip_trailing_punctuation):
        - Unicode typographic chars → ASCII
        - Markdown markup removed
        - All text lowercased
        - All whitespace collapsed to single spaces
        - Leading and trailing whitespace stripped
    """
    if not text:
        return ""

    text = _normalize_unicode(text)

    if strip_markdown:
        text = _normalize_markdown(text)

    if collapse_whitespace:
        text = _normalize_whitespace(text)

    if lowercase:
        text = text.lower()

    if strip_trailing_punctuation:
        text = _PUNCTUATION_TAIL_RE.sub("", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Fingerprint computation
# ---------------------------------------------------------------------------

def _hash(text: str) -> str:
    """Return the hex SHA-256 of a UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _prefix(version: str = NORMALIZATION_VERSION) -> str:
    return f"fp:{version}:"


def content_fingerprint(
    content: str,
    *,
    strip_markdown: bool = True,
    lowercase: bool = True,
) -> Optional[str]:
    """
    Return the canonical content fingerprint, or None if content is empty
    after normalization.

    Two documents with identical content but different source_system or
    source_id produce the same content_fingerprint.
    """
    normalized = normalize_content(
        content,
        strip_markdown=strip_markdown,
        lowercase=lowercase,
    )
    if not normalized:
        return None
    return _prefix() + _hash(normalized)


def exact_fingerprint(
    source_system: str,
    source_id: str,
    content: str,
    *,
    strip_markdown: bool = True,
    lowercase: bool = True,
) -> Optional[str]:
    """
    Return the exact fingerprint: content + source identity.

    Used for idempotent re-ingestion. Re-ingesting the same document from
    the same source produces the same exact_fingerprint.
    """
    normalized = normalize_content(
        content,
        strip_markdown=strip_markdown,
        lowercase=lowercase,
    )
    if not normalized:
        return None
    combined = f"{source_system}|{source_id}|{normalized}"
    return _prefix() + _hash(combined)


# ---------------------------------------------------------------------------
# Fingerprint validation
# ---------------------------------------------------------------------------

_FP_RE = re.compile(r"^fp:(v\d+):([0-9a-f]{64})$")


def is_valid_fingerprint(fp: Optional[str]) -> bool:
    """Check whether a string is a well-formed fingerprint."""
    if not fp or not isinstance(fp, str):
        return False
    return bool(_FP_RE.match(fp))


def fingerprint_version(fp: str) -> Optional[str]:
    """Extract the version prefix ('v1', 'v2', ...) from a fingerprint."""
    if not is_valid_fingerprint(fp):
        return None
    return _FP_RE.match(fp).group(1)


def is_current_version(fp: str) -> bool:
    """Check whether a fingerprint was produced by the current normalization rules."""
    return fingerprint_version(fp) == NORMALIZATION_VERSION


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Phase 6.2 fingerprint self-test ===\n")

    # Test 1: same content, different whitespace → same fingerprint
    a = "Hello world, this is a test."
    b = "Hello    world,\n\nthis is a test."
    fp_a = content_fingerprint(a)
    fp_b = content_fingerprint(b)
    print("Test 1 (whitespace-insensitive):", "PASS" if fp_a == fp_b else "FAIL")
    print(f"  {fp_a}")

    # Test 2: same content, different case → same fingerprint
    c = "HELLO WORLD, THIS IS A TEST."
    fp_c = content_fingerprint(c)
    print("Test 2 (case-insensitive):", "PASS" if fp_a == fp_c else "FAIL")

    # Test 3: same content, one with markdown → same fingerprint
    d = "# Hello world, this is a test."
    fp_d = content_fingerprint(d)
    print("Test 3 (markdown-insensitive):", "PASS" if fp_a == fp_d else "FAIL")

        # Test 4: same content, typographic quote variant → same fingerprint
    e = "Hello, it's a test."          # straight apostrophe
    f = "Hello, it\u2019s a test."    # curly right single quote
    fp_e = content_fingerprint(e)
    fp_f = content_fingerprint(f)
    print("Test 4 (typographic normalization):", "PASS" if fp_e == fp_f else "FAIL")

    # Test 5: genuinely different content → different fingerprint
    h = "Hello world, this is a different test."
    fp_h = content_fingerprint(h)
    print("Test 5 (different content):", "PASS" if fp_a != fp_h else "FAIL")

    # Test 6: exact_fingerprint includes source identity
    fp_ex_1 = exact_fingerprint("local_fs", "/path/a.txt", a)
    fp_ex_2 = exact_fingerprint("local_fs", "/path/b.txt", a)
    fp_ex_3 = exact_fingerprint("s3", "/path/a.txt", a)
    print("Test 6 (exact differs by source_id):", "PASS" if fp_ex_1 != fp_ex_2 else "FAIL")
    print("Test 7 (exact differs by source_system):", "PASS" if fp_ex_1 != fp_ex_3 else "FAIL")
    print("Test 8 (exact stable for same input):", "PASS" if fp_ex_1 == exact_fingerprint("local_fs", "/path/a.txt", a) else "FAIL")

    # Test 9: empty content → None
    fp_empty = content_fingerprint("")
    fp_whitespace = content_fingerprint("   \n\n   ")
    print("Test 9 (empty content → None):", "PASS" if fp_empty is None and fp_whitespace is None else "FAIL")

    # Test 10: fingerprint validation
    print("Test 10 (is_valid_fingerprint):", "PASS" if is_valid_fingerprint(fp_a) and not is_valid_fingerprint("not-a-fp") else "FAIL")
    print("Test 11 (fingerprint_version):", "PASS" if fingerprint_version(fp_a) == "v1" else "FAIL")
    print("Test 12 (is_current_version):", "PASS" if is_current_version(fp_a) else "FAIL")

    # Test 13: cross-source dedup works
    # Same content, one from Google Drive, one from SharePoint
    shared_content = "The platform deployment runbook.\n\nStep 1: Run migrations.\nStep 2: Deploy."
    fp_drive = content_fingerprint(shared_content)
    fp_sharepoint = content_fingerprint(shared_content)
    print("Test 13 (cross-source dedup):", "PASS" if fp_drive == fp_sharepoint else "FAIL")

    # Test 14: strict mode preserves case
    fp_lower = content_fingerprint("Hello World", lowercase=True)
    fp_strict = content_fingerprint("Hello World", lowercase=False)
    fp_strict_other = content_fingerprint("hello world", lowercase=False)
    print("Test 14 (strict mode distinguishes case):", "PASS" if fp_strict != fp_strict_other else "FAIL")

    # Test 15: 64 hex chars after prefix
    parts = fp_a.split(":")
    print("Test 15 (hash is 64 hex chars):", "PASS" if len(parts) == 3 and len(parts[2]) == 64 else "FAIL")

    print()
    print("=== Normalization examples ===")
    sample = "# Deployment Runbook\n\n**Step 1:** Run migrations.\n\n- Item one\n- Item two\n\n\u201cFinal step.\u201d"
    print("Original:")
    print(repr(sample))
    print("\nNormalized:")
    print(repr(normalize_content(sample)))
    print("\nFingerprint:")
    print(content_fingerprint(sample))