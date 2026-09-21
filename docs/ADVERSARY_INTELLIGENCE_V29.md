# VEYRA v3.0 — Adversary Intelligence & Wireless Defense Fabric

## Purpose

v3.0 turns the existing Wi-Fi/LAN visibility and investigation capabilities into first-class defensive workflows. It is designed to help an incident responder retrace an intrusion from observed evidence rather than attempt retaliation.

## UI surfaces

1. **Adversary Intelligence** — mission overview and investigation pipeline.
2. **Wireless Defense** — access points, LAN/wireless clients, trusted baseline and rogue/baseline candidates.
3. **Attack Timeline** — cross-source chronology for network flows, sessions and audit events.
4. **Infrastructure Investigation** — service → process → PID → user attribution, network flow review and identity exposure.
5. **Attribution & Evidence** — evidence-backed attribution hypotheses plus evidence-bundle staging.

## Investigation chain

`Observe → Preserve → Correlate → Reconstruct → Enrich → Hypothesize → Verify → Contain → Recover`

The UI deliberately distinguishes an **unknown** device from a confirmed malicious device. Attribution is always a hypothesis until corroborated by independent evidence.

## Wireless workflow

- Ingest read-only SSID/BSSID/channel/security metadata from the local sensor.
- Compare observed access points and clients with the expected baseline.
- Correlate unknown clients with DHCP, router association, identity, DNS and flow telemetry.
- Preserve raw evidence and collection metadata before remediation.
- Route any authorized wireless assessment through the existing governed worker fabric.

### Explicitly out of scope for the SaaS console

Credential capture, deauthentication/disruption, persistence, C2, hack-back, destructive actions and unrestricted shell execution.

## Attribution workflow

VEYRA can rank hypotheses using observed evidence such as:

- unexpected wireless/LAN devices;
- unusual network flows;
- process/PID/user attribution;
- privileged or anomalous sessions;
- threat-intelligence correlations;
- audit and containment history.

A hypothesis must include supporting and contradicting evidence and a next verification step. The platform must not infer a person's identity from an IP address, MAC address or threat-intel match alone.

## Evidence bundle

A staged bundle records:

- collection identity;
- UTC timestamp;
- source and scope;
- SHA-256 artifact integrity values;
- storage location;
- access history / chain of custody.

Production deployment should place immutable artifacts in WORM/object-lock storage and retain the original source artifacts alongside normalized records.

## API

- `GET /api/v29/overview`
- `GET /api/v29/wireless`
- `GET /api/v29/timeline`
- `GET /api/v29/infrastructure`
- `GET /api/v29/attribution` — admin gated
- `POST /api/v29/evidence-bundle` — admin gated

## Production hardening backlog

- Signed worker identity with short-lived workload credentials.
- Immutable evidence storage with legal-hold support.
- Router/DHCP/802.1X/RADIUS/Switch controller connectors.
- PCAP ingestion and Zeek/Suricata normalization through isolated workers.
- Bluetooth/RFID/SDR telemetry adapters with the same evidence contract.
- Case-level chain-of-custody and exportable forensic packages.
- External threat-intelligence enrichment with source provenance and confidence.
- Human approval for every containment side effect.
