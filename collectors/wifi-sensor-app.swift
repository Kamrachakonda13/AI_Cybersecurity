// AegisX Wi-Fi Sensor app executable (bundled .app, LSUIElement).
// 1. Explicitly requests Location (this is what shows the system Allow dialog;
//    a bare CoreWLAN scan only silently withholds SSID/BSSID, never prompts).
// 2. Waits up to 90s for the answer, then runs a CoreWLAN scan and prints JSON.
// Read-only metadata only: SSID/BSSID/signal/channel/band. No passwords/keys.
import CoreLocation
import CoreWLAN
import Foundation

final class Asker: NSObject, CLLocationManagerDelegate {
    let mgr = CLLocationManager()
    var decided = false
    var granted = false
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedAlways, .authorized:
            granted = true; decided = true
        case .denied, .restricted:
            granted = false; decided = true
        case .notDetermined:
            break
        @unknown default:
            break
        }
    }
}

func bandName(_ channel: CWChannel?) -> String {
    guard let ch = channel else { return "" }
    switch ch.channelBand {
    case .band2GHz: return "2.4GHz"
    case .band5GHz: return "5GHz"
    case .band6GHz: return "6GHz"
    default: return ""
    }
}

let asker = Asker()
let initial = CLLocationManager.authorizationStatus()
let initialRaw = initial.rawValue
if initial == .notDetermined {
    asker.mgr.requestWhenInUseAuthorization()
    let deadline = Date().addingTimeInterval(600)
    while !asker.decided && Date() < deadline {
        RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.5))
    }
} else {
    asker.granted = (initial == .authorizedAlways || initial == .authorized)
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
let payload: [String: Any] = [
    "auth_raw": initialRaw,
    "location_granted": asker.granted,
    "networks": networks,
    "current": current,
]
if let data = try? JSONSerialization.data(withJSONObject: payload) {
    print(String(data: data, encoding: .utf8) ?? "{}")
} else {
    print("{\"location_granted\":false,\"networks\":[],\"current\":{\"ssid\":\"\"}}")
}
