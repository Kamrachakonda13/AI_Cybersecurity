import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

KEV_FILE = Path("data/security/kev.json")
ATTACK_FILE = Path("data/security/attack.json")
OUT_FILE = Path("data/security/security_corpus.json")


def load_kev_chunks() -> list:
    """Convert each KEV vulnerability into a prose chunk.
    Sorted by dateAdded descending so recent/viral CVEs come first."""
    data = json.loads(KEV_FILE.read_text())
    vulns = data.get("vulnerabilities", [])
    # Sort by dateAdded (ISO date string), most recent first
    vulns_sorted = sorted(
        vulns,
        key=lambda v: v.get("dateAdded", ""),
        reverse=True,
    )

    chunks = []
    for i, v in enumerate(vulns_sorted):
        cve = v.get("cveID", "")
        vendor = v.get("vendorProject", "")
        product = v.get("product", "")
        name = v.get("vulnerabilityName", "")
        desc = v.get("shortDescription", "")
        action = v.get("requiredAction", "")
        due = v.get("dueDate", "")
        known_ransomware = v.get("knownRansomwareCampaignUse", "Unknown")

        content = (
            f"Vulnerability {cve}: {name}\n\n"
            f"Vendor: {vendor}\n"
            f"Product: {product}\n\n"
            f"Description: {desc}\n\n"
            f"Required action: {action}\n"
            f"Due date: {due}\n"
            f"Known ransomware campaign use: {known_ransomware}"
        )

        chunks.append({
            "id": f"kev_{cve}" if cve else f"kev_{i:04d}",
            "source_file": "cisa_kev",
            "chunk_index": i,
            "content": content,
            "clearance_level": "INTERNAL",
            "tenant_id": "acme",
        })
    return chunks

def load_attack_chunks() -> list:
    """Convert each ATT&CK technique into a prose chunk."""
    data = json.loads(ATTACK_FILE.read_text())
    chunks = []
    idx = 0

    for obj in data.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        technique_id = ""
        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                technique_id = ref.get("external_id", "")
                break

        if not technique_id:
            continue

        name = obj.get("name", "")
        description = obj.get("description", "")
        # Truncate long descriptions to keep chunks reasonable
        description = description[:1500]

        tactics = [
            phase.get("phase_name", "")
            for phase in obj.get("kill_chain_phases", [])
            if phase.get("kill_chain_name") == "mitre-attack"
        ]

        content = (
            f"Technique {technique_id}: {name}\n\n"
            f"Tactics: {', '.join(tactics) if tactics else 'unspecified'}\n\n"
            f"Description: {description}"
        )

        chunks.append({
            "id": f"attack_{technique_id}",
            "source_file": "mitre_attack",
            "chunk_index": idx,
            "content": content,
            "clearance_level": "CONFIDENTIAL",  # Technique detail is more sensitive
            "tenant_id": "acme",
        })
        idx += 1

    return chunks


def main():
    if not KEV_FILE.exists():
        raise FileNotFoundError(f"{KEV_FILE} not found. Run the curl command from Phase 5.2.")
    if not ATTACK_FILE.exists():
        raise FileNotFoundError(f"{ATTACK_FILE} not found. Run the curl command from Phase 5.2.")

    print("Loading CISA KEV...")
    kev_chunks = load_kev_chunks()
    print(f"  {len(kev_chunks)} KEV chunks")

    print("Loading MITRE ATT&CK...")
    attack_chunks = load_attack_chunks()
    print(f"  {len(attack_chunks)} ATT&CK chunks")

    all_chunks = kev_chunks + attack_chunks

    # Balance the corpus: keep all ATT&CK chunks (they're fewer and more queryable)
    # and cap KEV to keep the total manageable.
    MAX_KEV = 1600
    MAX_ATTACK = 700

    kev_chunks = kev_chunks[:MAX_KEV]
    attack_chunks = attack_chunks[:MAX_ATTACK]

    all_chunks = kev_chunks + attack_chunks
    print(f"Corpus: {len(kev_chunks)} KEV + {len(attack_chunks)} ATT&CK = {len(all_chunks)} total")

    OUT_FILE.write_text(json.dumps(all_chunks, indent=2))
    print(f"\nWrote {len(all_chunks)} chunks to {OUT_FILE}")

    # Distribution report
    from collections import Counter
    print("Clearance distribution:", dict(Counter(c["clearance_level"] for c in all_chunks)))
    print("Source distribution:", dict(Counter(c["source_file"] for c in all_chunks)))


if __name__ == "__main__":
    main()