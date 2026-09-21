# Lawful forensics & reverse-engineering with VEYRA (read this first)

VEYRA helps you **inspect what an outside attacker did to you** — it does not
help you break into them. "Hacking back" (unauthorized access, retaliatory
payloads, credential reuse, DoS) is illegal in most jurisdictions even when you
were attacked first. If you are breached: contain, preserve, report.

## Lawful workflow both teams follow

1. **Isolate, don't retaliate.** Disconnect the affected lab host from the
   network. Snapshot the container/VM (`docker commit`, disk image) before
   touching anything. Record who handled what (chain of custody).
2. **Static analysis in VEYRA.** UI → Forensics → upload the quarantined file
   (≤ 5 MB, never executed). You get hash, type, risk, flags with why-text,
   IOCs and string sample — audit-logged.
3. **Correlate.** Take extracted IPs/URLs to Security Graph
   (`/api/graph/answer?kind=connection_owner`) and Identity (who ran it?) +
   Network flows (did it beacon out?).
4. **Deep review on your workstation.** Open lab copies in Kali tools:
   Ghidra/radare2 (disassembly), Volatility (memory image), Wireshark (PCAP you
   own), Autopsy (disk image). Never point these at third-party systems.
5. **Report.** File findings + audit trail; notify leadership / authorities per
   policy. Keep the image for investigators.

## Kali mapping (what runs where)

| Need | Kali tool (workstation) | VEYRA (this platform) |
|---|---|---|
| Identify | sha256sum, file, exiftool | hash + magic-type per upload |
| Strings | strings, binwalk | printable-string sample |
| Signatures | YARA, ClamAV | heuristic keyword/pattern flags |
| RE | Ghidra, radare2 | header hints only — full RE is local |
| Network | Wireshark, tshark | IOC → graph/flow correlation |
| Host/disk/mem | Volatility, Autopsy | Endpoint/Identity correlation |

## Off-limits (blocked by design)

- No sample execution or malware detonation in the API.
- No Metasploit/Burp-active replay against anyone.
- No scanning, login attempts, or payload delivery outside `vulnerable-web`/lab.
- Uploads are memory-only, capped, never stored; anything bigger goes to your
  workstation with write-blockers.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
