"""Canonical tool ID slugification.

Produces safe, URL-friendly, filesystem-friendly IDs from arbitrary names.

Rules:
    - lowercase
    - any run of non-alphanumeric characters collapses to a single hyphen
    - strip leading/trailing hyphens
    - never emits &, /, \\, spaces, or consecutive hyphens
"""
import re

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    if not text:
        return ""
    s = _SLUG_RE.sub("-", text.lower())
    return s.strip("-")
