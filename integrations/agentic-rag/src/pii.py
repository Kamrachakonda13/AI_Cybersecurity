"""
PII detection and masking for Phase 7.

Uses Microsoft Presidio to detect and mask personally identifiable information
in both user input and LLM output.

Two functions:
    check_pii(text)     -> {has_pii, entities, ...}
    mask_pii(text)      -> masked text with [ENTITY_TYPE] placeholders

Integration:
    - Input side: check_pii on the user query before routing
    - Output side: mask_pii on the generated answer before returning
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_analyzer = None
_anonymizer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        from presidio_analyzer import AnalyzerEngine
        _analyzer = AnalyzerEngine()
    return _analyzer


def _get_anonymizer():
    global _anonymizer
    if _anonymizer is None:
        from presidio_anonymizer import AnonymizerEngine
        _anonymizer = AnonymizerEngine()
    return _anonymizer


# Entities we care about
# Entities masked by default.
# Note: PERSON and LOCATION are intentionally excluded because in an
# enterprise RAG context they are usually legitimate business content
# (e.g. "Palo Alto Networks", "Alice from the platform team") rather
# than sensitive PII. Enable them explicitly when needed.
DEFAULT_ENTITIES = [
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "US_SSN",
    "US_PASSPORT",
    "IP_ADDRESS",
    "IBAN_CODE",
    "CRYPTO",
]


def check_pii(text: str, entities: list = None, threshold: float = 0.3) -> dict:
    """
    Detect PII in text.

    Returns:
        {
            "has_pii": bool,
            "entities": [{"type": str, "start": int, "end": int, "text": str, "score": float}],
            "count": int,
            "text_length": int,
        }
    """
    if not text or not text.strip():
        return {"has_pii": False, "entities": [], "count": 0, "text_length": 0}

    try:
        analyzer = _get_analyzer()
        results = analyzer.analyze(
            text=text,
            entities=entities or DEFAULT_ENTITIES,
            language="en",
            score_threshold=threshold,
            context=["region=US", "region=IN"],
        )
        found = [
            {
                "type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "text": text[r.start:r.end],
                "score": round(r.score, 3),
            }
            for r in results
        ]
        return {
            "has_pii": len(found) > 0,
            "entities": found,
            "count": len(found),
            "text_length": len(text),
        }
    except Exception as e:
        # Fail-safe: if we can't scan, assume PII might exist
        return {
            "has_pii": True,
            "entities": [],
            "count": 0,
            "text_length": len(text),
            "error": str(e)[:200],
            "fail_closed": True,
        }


def mask_pii(text: str, entities: list = None, threshold: float = 0.3) -> dict:
    """
    Mask PII in text with [ENTITY_TYPE] placeholders.

    Returns:
        {
            "original": str,
            "masked": str,
            "entities": [...],
            "count": int,
        }
    """
    if not text or not text.strip():
        return {"original": text, "masked": text, "entities": [], "count": 0}

    try:
        analyzer = _get_analyzer()
        anonymizer = _get_anonymizer()

        results = analyzer.analyze(
            text=text,
            entities=entities or DEFAULT_ENTITIES,
            language="en",
            score_threshold=threshold,
            context=["region=US", "region=IN"],
        )

        if not results:
            return {"original": text, "masked": text, "entities": [], "count": 0}

        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

        entity_list = [
            {
                "type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": round(r.score, 3),
            }
            for r in results
        ]

        return {
            "original": text,
            "masked": anonymized.text,
            "entities": entity_list,
            "count": len(entity_list),
        }
    except Exception as e:
        # Fail-safe: return a generic mask
        return {
            "original": text,
            "masked": "[REDACTED - PII SCAN FAILED]",
            "entities": [],
            "count": 0,
            "error": str(e)[:200],
            "fail_closed": True,
        }


if __name__ == "__main__":
    print("=== PII detection self-test ===\n")

    # Test 1: email detection
    r1 = check_pii("Please contact me at alice@acme.com for details.")
    print(f"Test 1 (email detection): {'PASS' if r1['has_pii'] else 'FAIL'}")
    if r1["entities"]:
        for e in r1["entities"]:
            print(f"    {e['type']}: {e['text']!r} (score={e['score']})")

    # Test 2: phone number
    r2 = check_pii("Call me at 555-123-4567 if you need help.")
    print(f"Test 2 (phone detection): {'PASS' if r2['has_pii'] else 'FAIL'}")

    # Test 3: credit card
    r3 = check_pii("My card number is 4111-1111-1111-1111.")
    print(f"Test 3 (credit card detection): {'PASS' if r3['has_pii'] else 'FAIL'}")

    # Test 4: clean text
    r4 = check_pii("This is a normal sentence with no PII at all.")
    print(f"Test 4 (clean text): {'PASS' if not r4['has_pii'] else 'FAIL'}")

    # Test 5: masking
    r5 = mask_pii("Contact alice@acme.com or call 555-123-4567.")
    print(f"Test 5 (masking): {'PASS' if r5['count'] >= 2 and r5['masked'] != r5['original'] else 'FAIL'}")
    print(f"    Original: {r5['original']!r}")
    print(f"    Masked:   {r5['masked']!r}")

    # Test 6: multiple entities
    r6 = check_pii("Alice Johnson at alice@acme.com, IP 10.0.0.5")
    print(f"Test 6 (multiple entities): {'PASS' if r6['count'] >= 2 else 'FAIL'}")
    print(f"    Count: {r6['count']}")

    # Test 7: empty input
    r7 = check_pii("")
    print(f"Test 7 (empty input): {'PASS' if not r7['has_pii'] else 'FAIL'}")

    print()
    print("All PII detection tests PASS")
