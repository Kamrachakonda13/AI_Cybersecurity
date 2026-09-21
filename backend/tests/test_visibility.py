"""Tests for visibility + artifact parsers (`services/visibility.py`, `services/forensics.py`).

Help: in-memory DB for brute-force grouping + DNS summaries; byte-crafted inputs
for eml macro/docx/pcap parsers. Depends on `app.db.Base`, all models, stdlib
`struct`/`zipfile` (mirrors the parser implementations).
"""
import io
import struct
import zipfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import LoginAttempt, DnsQuery
from app.services.visibility import brute_force_candidates, browsing_summary
from app.services.forensics import analyze_bytes


def _db():
    eng = create_engine("sqlite:///:memory:")
    S = sessionmaker(bind=eng)
    Base.metadata.create_all(bind=eng)
    return S()


def test_brute_force_candidate_flagged():
    s = _db()
    s.add_all([LoginAttempt(username="admin", source_ip="9.9.9.9", success=False) for _ in range(6)])
    s.add(LoginAttempt(username="admin", source_ip="9.9.9.9", success=True))
    s.commit()
    r = brute_force_candidates(s)
    assert r["failed"] == 6
    assert any(x["source_ip"] == "9.9.9.9" and x["candidate"] for x in r["by_ip"])
    s.close()


def test_browsing_summary_counts():
    s = _db()
    s.add_all([DnsQuery(hostname="laptop-1", domain="example.com", hits=3),
               DnsQuery(hostname="laptop-1", domain="evil.tk", hits=7),
               DnsQuery(hostname="lab-pc", domain="example.com", hits=1)])
    s.commit()
    r = browsing_summary(s)
    assert r["top_domains"][0] == {"domain": "evil.tk", "hits": 7}
    assert len(r["per_device"]) == 2
    s.close()


def test_eml_phish_flags():
    eml = (b"From: spoof@evil.tk\r\nSubject: Verify your password now\r\n"
           b"To: me@lab.local\r\nContent-Type: text/plain\r\n\r\n"
           b"Click https://evil.tk/login now to verify your password")
    r = analyze_bytes(eml, "phish.eml")
    assert r["artifact"]["kind"] == "eml"
    assert any(f["rule"] == "phish:social-engineering-url" for f in r["flags"])
    assert r["risk"] in ("HIGH", "CRITICAL")


def test_office_macro_flags():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", "<w:doc/>")
        z.writestr("word/vbaProject.bin", "macro")
    r = analyze_bytes(buf.getvalue(), "invoice.docm")
    assert r["artifact"]["has_macro"] is True
    assert any(f["rule"] == "doc:macro" for f in r["flags"])


def _pcap_one_dns(name=b"evil.tk"):
    # global header (LE) + one Ethernet/IPv4/UDP packet with DNS query
    labels = b"".join(bytes([len(p)]) + p for p in name.split(b".")) + b"\x00"
    dns = struct.pack(">HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0) + labels + struct.pack(">HH", 1, 1)
    udp = struct.pack(">HHHH", 12345, 53, 8 + len(dns), 0) + dns
    ip = bytes([0x45, 0, 0, 0, 0, 0, 0, 0, 64, 17, 0, 0, 10, 0, 0, 2, 8, 8, 8, 8])
    ip = ip[:2] + struct.pack(">H", 20 + len(udp)) + ip[4:]
    eth = b"\x00" * 12 + struct.pack(">H", 0x0800)
    pkt = eth + ip + udp
    hdr = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    rec = struct.pack("<IIII", 0, 0, len(pkt), len(pkt)) + pkt
    return hdr + rec


def test_pcap_dns_parsed_and_flagged():
    r = analyze_bytes(_pcap_one_dns(), "cap.pcap")
    assert r["artifact"]["kind"] == "pcap"
    assert r["artifact"]["packet_count"] == 1
    assert "evil.tk" in r["artifact"]["dns_names"]
    assert any(f["rule"] == "pcap:suspicious-domain" for f in r["flags"])
