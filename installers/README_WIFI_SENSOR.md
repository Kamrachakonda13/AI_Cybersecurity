# VEYRA Local Wi-Fi Sensor

The web console cannot directly scan the computer's Wi-Fi radio because browsers and Docker do not expose raw Wi-Fi scanning. VEYRA therefore includes a small **read-only localhost sensor**. It reads nearby Wi-Fi metadata using the operating system's native tools and never collects Wi-Fi passwords, keys, packet contents, or credentials.

Start it with `python3 collectors/endpoint-agent.py --sensor`. For a product deployment, package it as a macOS LaunchAgent / Windows service / Linux systemd user service so the user does not need to use Terminal.

The console uses `http://127.0.0.1:8765` only for Wi-Fi radio data. LAN discovery remains through the enrolled endpoint collector and backend.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
