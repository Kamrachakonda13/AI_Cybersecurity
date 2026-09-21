// AegisX macOS Wi-Fi scan helper (read-only metadata, no passwords/keys).
// Uses CoreWLAN because Apple removed the `airport -s` CLI on modern macOS.
// Build: swiftc -O -o wifi-scan-macos wifi-scan-macos.swift
// Run: ./wifi-scan-macos  -> {"networks":[...], "current":{...}} on stdout.
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
