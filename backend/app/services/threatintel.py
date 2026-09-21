"""Live threat-intel ingestion: CISA KEV catalog + NVD CVE API.

Help — design, dependencies, safety:
- `parse_kev_csv(text)` / `parse_nvd(payload)`: PURE parsers (no I/O), unit-tested.
  KEV columns: cveID, vendorProject, product, vulnerabilityName, dateAdded,
  shortDescription, requiredAction, dueDate. NVD 2.0: vulnerabilities[].cve
  (id, descriptions, metrics.cvssMetricV31/V30/V2, published).
- `refresh_kev(db, fetch)` / `refresh_nvd(db, cve_ids, fetch)`: upsert `CveRecord`
  rows and mirror `ThreatIntel` rows (KEV → exploited=True). `fetch` is injected
  (route passes httpx; tests pass fakes) so no test hits the network.
- Safety: outbound HTTPS ONLY to `ALLOWED_HOSTS` (enforced in route fetchers),
  20–25s timeouts, NVD capped at 20 CVEs/call (API rate limits), optional
  `NVD_API_KEY` env header, every refresh audit-logged. Never executes anything.
- `_auto_refresh_loop()`: background 24h loop for production; started by
  `app.main.lifespan` ONLY when `THREATINTEL_AUTO_REFRESH=true`. Failures are
  swallowed (logged) so boot/scheduler never crash the API.
- Depended on by: `POST /api/threat-intel/refresh`, `GET /api/threat-intel/cves`.
"""
import csv
import io
import logging
import time

log = logging.getLogger("aegisx.threatintel")

CISA_KEV_CSV = "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv"
NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
ALLOWED_HOSTS = {"www.cisa.gov", "services.nvd.nist.gov"}
NVD_MAX_CVES = 20


def parse_kev_csv(text: str) -> list[dict]:
    """Parse CISA KEV CSV text → [{cve_id, vendor, product, name, description, due_date}]."""
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        cid = (r.get("cveID") or "").strip().upper()
        if not cid.startswith("CVE-"):
            continue
        rows.append({"cve_id": cid, "vendor": r.get("vendorProject", "").strip(),
                     "product": r.get("product", "").strip(),
                     "name": r.get("vulnerabilityName", "").strip(),
                     "description": r.get("shortDescription", "").strip(),
                     "due_date": r.get("dueDate", "").strip()})
    return rows


def _nvd_score(cve: dict) -> tuple[float, str]:
    """Best CVSS from NVD metrics (prefers 3.1 → 3.0 → 2.0). Returns (score, severity)."""
    for key in ("cvssMetricV31", "cvssMetricV30"):
        m = (cve.get("metrics", {}).get(key) or [])
        if m:
            d = m[0].get("cvssData", {})
            return float(d.get("baseScore", 0)), str(d.get("baseSeverity", ""))
    m2 = (cve.get("metrics", {}).get("cvssMetricV2") or [])
    if m2:
        return float(m2[0].get("cvssData", {}).get("baseScore", 0)), "LOW"
    return 0.0, ""


def parse_nvd(payload: dict) -> list[dict]:
    """Parse NVD 2.0 response → [{cve_id, description, cvss, severity, published}]."""
    out = []
    for item in payload.get("vulnerabilities", []) or []:
        cve = item.get("cve", {})
        cid = str(cve.get("id", "")).upper()
        if not cid.startswith("CVE-"):
            continue
        descs = cve.get("descriptions", []) or []
        text = next((d.get("value", "") for d in descs if d.get("lang") == "en"), "")
        score, sev = _nvd_score(cve)
        out.append({"cve_id": cid, "description": text[:2000], "cvss": round(score, 1),
                    "severity": sev.upper(), "published": str(cve.get("published", ""))[:10]})
    return out


def upsert_cve(db, cve_id: str, description: str = "", cvss: float = 0,
               severity: str = "", kev: bool = False, published: str = "",
               source: str = "CISA/NVD") -> bool:
    """Insert or update one `CveRecord` + mirror `ThreatIntel` row. Returns True if created."""
    from ..models import CveRecord, ThreatIntel
    rec = db.query(CveRecord).filter(CveRecord.cve_id == cve_id).first()
    created = rec is None
    if created:
        rec = CveRecord(cve_id=cve_id)
        db.add(rec)
    rec.description = description or rec.description
    rec.cvss = cvss or rec.cvss
    rec.severity = severity or rec.severity
    rec.published = published or rec.published
    rec.source = source
    if kev:
        rec.kev = True
    intel = db.query(ThreatIntel).filter(
        ThreatIntel.source == ("CISA KEV" if kev else "NVD"),
        ThreatIntel.indicator == cve_id).first()
    if intel is None:
        db.add(ThreatIntel(source="CISA KEV" if kev else "NVD", indicator=cve_id,
                           indicator_type="CVE", title=description[:255] or cve_id,
                           severity="CRITICAL" if kev or (cvss or 0) >= 9 else "HIGH",
                           exploited=kev, description=description[:2000]))
    elif kev and not intel.exploited:
        intel.exploited = True
        intel.severity = "CRITICAL"
    return created


def refresh_kev(db, fetch) -> dict:
    """Fetch KEV CSV via injected `fetch(url)->text`, upsert all rows. Returns {cves, new}."""
    rows = parse_kev_csv(fetch(CISA_KEV_CSV))
    new = sum(upsert_cve(db, r["cve_id"],
                         description=f"{r['vendor']} {r['product']}: {r['name']}. {r['description']} (due {r['due_date']})",
                         kev=True, source="CISA KEV") for r in rows)
    db.commit()
    return {"cves": len(rows), "new": new}


def refresh_nvd(db, cve_ids: list[str], fetch) -> dict:
    """Fetch NVD details for ≤20 CVE IDs via injected `fetch(url)->dict`. Returns {cves, new}."""
    ids = [c.strip().upper() for c in cve_ids if c.strip().upper().startswith("CVE-")][:NVD_MAX_CVES]
    total = new = 0
    for cid in ids:
        for row in parse_nvd(fetch(f"{NVD_API}?cveId={cid}")):
            total += 1
            new += upsert_cve(db, row["cve_id"], row["description"], row["cvss"],
                              row["severity"], published=row["published"], source="NVD")
    db.commit()
    return {"cves": total, "new": new}


async def _auto_refresh_loop(interval_hours: int = 24):
    """Production background loop: full KEV refresh every 24h. Never raises (logs only)."""
    import httpx
    from ..db import SessionLocal

    def fetch(url: str) -> str:
        with httpx.Client(timeout=25) as c:
            return c.get(url).raise_for_status().text

    while True:
        try:
            db = SessionLocal()
            try:
                stats = refresh_kev(db, fetch)
                db.add(__import__("app.models", fromlist=["AuditEvent"]).AuditEvent(
                    actor="scheduler", action="kev_auto_refresh",
                    target=f"{stats['cves']} cves", outcome="success"))
                db.commit()
            finally:
                db.close()
        except Exception as e:  # noqa: BLE001 — scheduler must never crash the app
            log.warning("KEV auto-refresh failed: %s", e)
        time.sleep(interval_hours * 3600)
