// AegisX macOS Wi-Fi scan (JIT edition) — read-only metadata, no passwords/keys.
// Run with the Apple-signed toolchain runner, e.g. `/usr/bin/swift wifi-scan-jit.swift`.
// Why JIT and not a compiled binary: airportd/locationd only disclose SSIDs to
// clients with a verifiable code identity ("masquerading client" otherwise), and an
// ad-hoc-signed build has none — while the Apple-signed swift runner does.
// Output: {"networks":[...], "current":{...}} on stdout.
import CoreWLAN
import Foundation

func bandName(_ channel: CWChannel?) -> String {
    guard let ch = channel else { return "" }
    switch ch.channelBand {
    case .band2GHz: return "2.4GHz"
    case .band5GHz: return "5GHz"
    case .band6GHz: return "6GHz"
    default: return ""
    }
}

var networks: [[String: Any]] = []
var current: [String: Any] = ["ssid": ""]
let client = CWWiFiClient.shared()
if let iface = client.interface() {
    if let ssid = iface.ssid() {
        current = ["ssid": ssid, "bssid": iface.bssid() ?? "", "interface": iface.interfaceName ?? ""]
    }
    do {
        let found = try iface.scanForNetworks(withName: nil)
        for n in found {
            let chNum = n.wlanChannel?.channelNumber ?? 0
            networks.append([
                "ssid": n.ssid ?? "",
                "bssid": (n.bssid ?? "").uppercased(),
                "signal_dbm": n.rssiValue,
                "channel": "\(chNum)",
                "band": bandName(n.wlanChannel),
                "security": "Unknown",
                "source": "macOS-CoreWLAN",
            ])
        }
        networks.sort { ($0["signal_dbm"] as? Int ?? -100) > ($1["signal_dbm"] as? Int ?? -100) }
    } catch {
        fputs("scan error: \(error)\n", stderr)
    }
}
let payload: [String: Any] = ["networks": networks, "current": current]
if let data = try? JSONSerialization.data(withJSONObject: payload) {
    print(String(data: data, encoding: .utf8) ?? "{}")
} else {
    print("{\"networks\":[],\"current\":{\"ssid\":\"\"}}")
}
