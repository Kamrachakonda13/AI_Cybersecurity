# Lawful network visibility — read before enabling collectors

VEYRA can show **devices on your network, DNS-browsing metadata, and login
attempts (including third-party attackers)** — but only where you have a lawful
basis. In most workplaces that means: you own the network, you have written
authorization, and users have been notified (acceptable-use policy / banner).
When in doubt, ask legal. Never monitor someone else's network.

## What is collected (and what is NOT)

| Data | Source | NOT collected |
|---|---|---|
| Devices (hostname, IP, MAC, OS, owner) | `lab/collector.py` neighbour table / lab ping-sweep you trigger | No port scan, no credentials, no screen/content |
| Browsing | DNS query metadata: device → domain + counts (`/api/ingest/dns`) | No URLs paths, no page content, no MITM/TLS break |
| Logins | Auth outcomes: user, source IP, host, success/fail (`/api/ingest/logins`) | No passwords or hashes, ever |

## Blue-team setup (your laptop lab)

```bash
# 1. passive, read-only — parses YOUR arp table, sends nothing
python3 lab/collector.py --dry-run
# 2. ingest your own neighbours with owner tag
python3 lab/collector.py --post --owner "Blue team"
# 3. optional lab ping-sweep (private /16-or-smaller only, asks YES)
python3 lab/collector.py --active 192.168.1.0/24 --post
# 4. forward YOUR router/Pi-hole DNS log + YOUR hosts' auth logs via the
#    ingest endpoints (see /docs → API /api/dns/top, /api/logins/summary)
```

## Reading attacker attempts

- Identity → Login summary: `by_ip` / `by_user` with `candidate: true` at ≥ 5
  fails. An unknown external IP hammering `admin` = password-spray candidate.
- Click any candidate for the help text, then pivot: Security Graph
  (`connection_owner`) → did that IP also show in flows/DNS? Endpoint → which
  host was targeted? Forensics → upload the quarantined payload.
- Respond per IR: block at YOUR perimeter, rotate creds, preserve logs.
  Do not touch the attacker's systems.

## Red-team use

Generate spray traffic **against `vulnerable-web` only**, then confirm blue sees
it in `/api/logins/summary`. Anything outside the lab scope doc is forbidden.

## Wi-Fi + LAN Visibility (v2.5.1+)

The **Network → Wi-Fi & LAN Visibility** screen is intentionally split into two windows:

1. **Nearby Wi-Fi Networks** — read-only wireless metadata from the computer's Wi-Fi radio: SSID, BSSID, signal, channel and security where the OS exposes it.
2. **My LAN Devices** — devices discovered on the selected/owned LAN using the enrolled endpoint sensor and VEYRA discovery pipeline.

### Two router modes

The UI provides a dropdown for **Router Mode A** and **Router Mode B**. Each profile has an editable expected SSID. This is useful for routers exposing two bands/SSIDs or two operating configurations. The selected profile filters the nearby-network view.

### Unauthorized-device investigation

VEYRA maintains a device baseline. New MAC/IP observations are **UNKNOWN** until the user verifies them. A user can click **Trust** or **Untrust** from the console; no terminal command is required. This is a baseline control, not proof of maliciousness.

For high-confidence investigation, correlate an unexpected device with the router's association/DHCP logs and VEYRA flow/session telemetry. Do not deauthenticate, attack, or otherwise disrupt a device from VEYRA.

### Local Wi-Fi sensor

Browsers cannot directly access raw nearby-Wi-Fi scan data, and Docker containers cannot see the host's Wi-Fi radio. VEYRA therefore includes a small read-only localhost sensor at `127.0.0.1:8765`. It uses the host OS native Wi-Fi inspection facilities and never collects Wi-Fi passwords, keys or packet contents.

For a production installation, the sensor should be installed as a signed background service (macOS LaunchAgent, Windows service, or Linux systemd service), so users interact only with the VEYRA GUI.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
