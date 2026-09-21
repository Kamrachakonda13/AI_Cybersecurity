"""LAN/Wi-Fi neighbour discovery (observed hosts + offline MAC-vendor lookup).

Help — design, dependencies:
- `OUI`: curated offline prefix table (common client/IoT silicon). No network
  lookups — works air-gapped. `vendor_for_mac()` normalises separators/case.
- `upsert_discovery(db, items)`: items {ip_address, mac, hostname, source}.
  Matches by MAC when present else by IP; refreshes `last_seen`, fills blanks,
  resolves `vendor` server-side. Returns {hosts, new}. Depends on:
  `DiscoveredHost` model only. Served by `POST /api/ingest/discovery`;
  read by `GET /api/discovery/hosts|/summary`; shown in the Network-section
  Wi-Fi panel. Enrolled agents stay in `Device` — this table is unknowns first.
"""
OUI = {
    "00:1B:63": "Apple", "00:1C:B3": "Apple", "00:1D:4F": "Apple", "00:1E:C2": "Apple",
    "00:1F:5B": "Apple", "00:1F:F3": "Apple", "00:21:E9": "Apple", "00:22:41": "Apple",
    "00:23:12": "Apple", "00:23:32": "Apple", "00:23:6C": "Apple", "00:23:AB": "Apple",
    "00:24:36": "Apple", "00:25:00": "Apple", "00:26:08": "Apple", "00:26:4A": "Apple",
    "00:26:B0": "Apple", "00:26:BB": "Apple", "28:CF:DA": "Apple", "3C:15:C2": "Apple",
    "40:30:04": "Apple", "44:2A:60": "Apple", "4C:57:CA": "Apple", "60:C5:47": "Apple",
    "68:96:7B": "Apple", "70:11:24": "Apple", "78:3A:84": "Apple", "7C:6D:F8": "Apple",
    "80:E6:50": "Apple", "88:53:95": "Apple", "8C:7B:9D": "Apple", "90:72:40": "Apple",
    "9C:04:EB": "Apple", "A4:B8:05": "Apple", "AC:87:A3": "Apple", "B8:09:8A": "Apple",
    "BC:54:2F": "Apple", "C8:2C:2C": "Apple", "D0:23:DB": "Apple", "D8:A2:5E": "Apple",
    "DC:2B:2A": "Apple", "E0:AC:CB": "Apple", "E4:CE:8F": "Apple", "F0:18:98": "Apple",
    "F4:0F:24": "Apple", "F8:1E:DF": "Apple",
    "00:12:FB": "Samsung", "00:16:6B": "Samsung", "00:17:D5": "Samsung", "00:1A:8A": "Samsung",
    "00:1D:F6": "Samsung", "00:1E:7D": "Samsung", "00:21:19": "Samsung", "00:24:91": "Samsung",
    "3C:8B:FE": "Samsung", "48:49:5F": "Samsung", "50:01:BB": "Samsung", "5C:3C:27": "Samsung",
    "78:1F:DB": "Samsung", "8C:F5:A3": "Samsung", "9C:3A:AF": "Samsung", "CC:07:AB": "Samsung",
    "00:1A:11": "Google", "3C:5A:37": "Google", "54:60:09": "Google", "94:EB:2C": "Google",
    "F4:F5:D8": "Google", "18:B4:30": "Google (Nest)",
    "0C:47:C9": "Amazon", "34:D2:70": "Amazon", "40:B4:CD": "Amazon", "44:65:0D": "Amazon",
    "68:37:E9": "Amazon", "74:C2:46": "Amazon", "7C:2F:80": "Amazon",
    "00:1B:77": "Intel", "00:1C:C0": "Intel", "00:1E:64": "Intel", "00:21:5C": "Intel",
    "00:21:6A": "Intel", "00:22:FA": "Intel", "00:22:FB": "Intel", "00:24:D6": "Intel",
    "3C:A9:F4": "Intel", "40:A8:F0": "Intel", "44:03:2C": "Intel", "4C:34:88": "Intel",
    "60:67:20": "Intel", "7C:5C:F8": "Intel", "9C:B6:D0": "Intel", "A0:88:69": "Intel",
    "00:14:22": "Dell", "00:1E:4F": "Dell", "00:21:70": "Dell", "00:22:19": "Dell",
    "00:24:E8": "Dell", "00:26:B9": "Dell", "18:03:73": "Dell", "34:E6:D7": "Dell",
    "3C:2C:30": "HP", "70:5A:0F": "HP", "80:C1:6E": "HP", "A0:8C:FD": "HP",
    "00:1A:6B": "Lenovo", "00:1E:EC": "Lenovo", "00:21:CC": "Lenovo", "50:7B:9D": "Lenovo",
    "04:7F:0E": "Xiaomi", "14:F6:5A": "Xiaomi", "28:6C:07": "Xiaomi", "34:80:B3": "Xiaomi",
    "50:64:2B": "Xiaomi", "64:09:80": "Xiaomi", "64:B0:A6": "Xiaomi", "78:11:DC": "Xiaomi",
    "00:18:82": "Huawei", "00:25:9E": "Huawei", "04:BD:70": "Huawei", "10:1B:54": "Huawei",
    "20:2B:C1": "Huawei", "48:49:C7": "Huawei", "E4:A7:A0": "Huawei",
    "9C:2C:83": "OnePlus", "D4:CB:F7": "OnePlus",
    "00:1B:FB": "Sony", "30:10:B3": "Sony",
    "00:1C:62": "LG", "34:4D:EA": "LG", "A8:16:B2": "LG",
    "00:15:5D": "Microsoft (Hyper-V)", "00:03:FF": "Microsoft", "28:18:78": "Microsoft",
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi", "E4:5F:01": "Raspberry Pi",
    "24:6F:28": "Espressif (ESP32)", "24:0A:C4": "Espressif", "30:AE:A4": "Espressif",
    "3C:71:BF": "Espressif", "7C:DF:A1": "Espressif", "84:CC:A8": "Espressif",
    "A4:CF:12": "Espressif", "BC:DD:C2": "Espressif", "CC:50:E3": "Espressif",
    "18:FE:34": "Espressif", "EC:64:C9": "Espressif",
    "00:0C:29": "VMware", "00:50:56": "VMware", "00:05:69": "VMware",
    "00:0D:3A": "Microsoft (Xbox)", "00:1D:D8": "Microsoft",
    "00:23:AE": "Sonos", "78:28:CA": "Sonos", "94:9F:3E": "Sonos",
    "00:17:88": "Philips Hue", "00:0E:8F": "Canon", "00:1B:A9": "Epson",
    "98:BA:5F": "TP-Link",
    "44:F7:9F": "Cloud Network Tech (Foxconn OEM)",
}


def normalize_mac(mac: str) -> str:
    """Upper-case colon form (`aa-bb-cc…`/`aabbcc…` → `AA:BB:CC…`). Returns '' when unusable."""
    h = "".join(c for c in (mac or "").upper() if c in "0123456789ABCDEF")
    if len(h) != 12:
        return ""
    return ":".join(h[i:i + 2] for i in range(0, 12, 2))


def vendor_for_mac(mac: str) -> str:
    """OUI lookup on the first 3 bytes. Returns vendor, 'Randomized (privacy MAC)',
    or 'Unknown'.

    Help: modern phones/laptops randomize Wi-Fi MACs (locally-administered bit,
    0x02 of the first byte, set) — such addresses can never match an OUI table,
    so they get their own label instead of a wrong vendor guess.
    """
    norm = normalize_mac(mac)
    if not norm:
        return "Unknown"
    if norm == "FF:FF:FF:FF:FF:FF":
        return "Broadcast"
    if int(norm[:2], 16) & 0x02:
        return "Randomized (privacy MAC)"
    return OUI.get(norm[:8], "Unknown")


def upsert_discovery(db, items: list[dict]) -> dict:
    """Upsert neighbours by MAC (preferred) else IP. Returns {hosts, new}."""
    from datetime import datetime, timezone
    from ..models import DiscoveredHost
    hosts = new = 0
    for it in items:
        ip = str(it.get("ip_address", "")).strip()
        if not ip:
            continue
        mac = normalize_mac(str(it.get("mac", "")))
        row = None
        if mac:
            row = db.query(DiscoveredHost).filter(DiscoveredHost.mac == mac).first()
        if row is None:
            row = db.query(DiscoveredHost).filter(DiscoveredHost.ip_address == ip).first()
        now = datetime.now(timezone.utc)
        if row is None:
            row = DiscoveredHost(ip_address=ip, mac=mac,
                                 hostname=str(it.get("hostname", ""))[:255],
                                 vendor=vendor_for_mac(mac),
                                 source=str(it.get("source", "agent-discover"))[:64])
            db.add(row)
            new += 1
        else:
            row.ip_address = ip  # DHCP may reassign; the MAC is the stable identity
            if mac:
                row.mac = mac
                row.vendor = vendor_for_mac(mac)
            if it.get("hostname"):
                row.hostname = str(it["hostname"])[:255]
            if it.get("source"):
                row.source = str(it["source"])[:64]
            row.last_seen = now
        hosts += 1
    db.commit()
    return {"hosts": hosts, "new": new}
