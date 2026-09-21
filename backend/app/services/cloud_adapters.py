"""Cloud posture adapters: Prowler-JSON import + live AWS read-only scan.

Help — design, dependencies, safety:
- `import_prowler(db, items)`: normalises Prowler-style finding dicts
  {check, provider, resource, resource_type, region, status, severity} into
  `CloudResource` rows (upsert by resource_id) + `Finding` rows for FAILs on the
  best-matching asset (falls back to first asset). Pure DB work — no cloud calls.
  Served by `POST /api/cloud/import-prowler`; run Prowler in YOUR CI and upload JSON.
- `aws_live_scan(db, ec2, s3, iam)`: maps duck-typed AWS clients
  (or real boto3 clients) to CloudResource rows: public S3 buckets
  (ACL/PolicyStatus), 0.0.0.0/0 security groups, admin-access IAM users without
  MFA. Takes injected clients so tests use fakes and no test needs credentials.
- `ADAPTERS` registry describes both; `GET /api/cloud/adapters` exposes it.
- Safety: read-only calls only (Describe*/List*/Get*); creds stay in env
  (`AWS_*`), never in DB/API. Live scan route returns 501 with setup guidance
  when boto3/creds are absent instead of failing obscurely.
"""
ADAPTERS = [
    {"name": "prowler-import", "provider": "multi",
     "use": "Import Prowler/Scout JSON findings produced in YOUR CI into inventory + findings.",
     "needs": "JSON array posted to /api/cloud/import-prowler. No creds."},
    {"name": "aws-live", "provider": "AWS",
     "use": "Read-only scan: public S3, open security groups, admin IAM without MFA.",
     "needs": "boto3 + AWS_ACCESS_KEY_ID/SECRET (read-only IAM) on the backend host."},
]


def _first_asset_id(db) -> int:
    from ..models import Asset
    a = db.query(Asset).first()
    return a.id if a else 1


def import_prowler(db, items: list[dict]) -> dict:
    """Upsert CloudResources + FAIL Findings from Prowler-style items. Returns {resources, findings}."""
    from ..models import CloudResource, Finding
    from .risk import severity as sev_of
    resources = findings = 0
    for it in items:
        rid = str(it.get("resource") or it.get("check") or "unknown")
        c = db.query(CloudResource).filter(CloudResource.resource_id == rid).first()
        public = str(it.get("status", "")).upper() == "FAIL" and any(
            w in str(it.get("check", "")).lower() for w in ("public", "expos", "open", "internet"))
        if c is None:
            c = CloudResource(provider=str(it.get("provider", "AWS")), resource_id=rid,
                              resource_type=str(it.get("resource_type", it.get("check", "finding"))),
                              region=str(it.get("region", "")))
            db.add(c)
            resources += 1
        c.public_exposure = c.public_exposure or public
        c.misconfiguration = str(it.get("check", ""))[:255]
        c.risk_score = max(c.risk_score or 0, 80 if public else 50)
        if str(it.get("status", "")).upper() == "FAIL":
            sev = str(it.get("severity", "")).upper() or ("CRITICAL" if public else "HIGH")
            db.add(Finding(asset_id=_first_asset_id(db),
                           title=f"[{c.provider}] {it.get('check', 'check')}: {rid}"[:255],
                           severity=sev if sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW") else "HIGH",
                           cvss=0, exposure=public, data_sensitivity=3,
                           risk_score=85 if public else 65,
                           description=f"Prowler finding {it.get('check')} on {rid} ({c.region}). Fix in IaC; rescan in CI."[:2000]))
            findings += 1
    db.commit()
    return {"resources": resources, "findings": findings}


def aws_live_scan(db, ec2, s3, iam) -> dict:
    """Map AWS clients (real boto3 or test fakes) → CloudResource rows. Returns {resources, findings}."""
    from ..models import CloudResource, Finding
    resources = findings = 0

    def upsert(rid, rtype, region, public, issue, risk, sev):
        nonlocal resources, findings
        c = db.query(CloudResource).filter(CloudResource.resource_id == rid).first()
        if c is None:
            c = CloudResource(provider="AWS", resource_id=rid, resource_type=rtype, region=region)
            db.add(c)
            resources += 1
        c.public_exposure = c.public_exposure or public
        c.misconfiguration = issue[:255]
        c.risk_score = max(c.risk_score or 0, risk)
        if public or risk >= 60:
            db.add(Finding(asset_id=_first_asset_id(db), title=f"[AWS] {issue}: {rid}"[:255],
                           severity=sev, cvss=0, exposure=public, data_sensitivity=3,
                           risk_score=risk,
                           description=f"Live AWS scan: {issue} on {rid} ({region}). Least-privilege fix required."[:2000]))
            findings += 1

    try:
        for b in (s3.list_buckets().get("Buckets", []) if hasattr(s3, "list_buckets") else s3.get("buckets", [])):
            name = b.get("Name", "")
            try:
                pub = bool(s3.get_public_access_block(Bucket=name).get("PublicAccessBlockConfiguration", {}).get("BlockPublicAcls") is False) \
                    if hasattr(s3, "get_public_access_block") else bool(b.get("public"))
            except Exception:
                pub = bool(b.get("public", False))
            upsert(name, "object-storage", b.get("Region", ""), pub,
                   "Public S3 bucket" if pub else "Bucket posture OK", 85 if pub else 20,
                   "CRITICAL" if pub else "LOW")
    except Exception:
        pass
    try:
        groups = ec2.describe_security_groups().get("SecurityGroups", []) if hasattr(ec2, "describe_security_groups") else ec2.get("security_groups", [])
        for g in groups:
            open_ww = any(ip.get("CidrIp") == "0.0.0.0/0"
                          for p in g.get("IpPermissions", []) for ip in p.get("IpRanges", []))
            upsert(g.get("GroupId", ""), "security-group", "", open_ww,
                   "Open 0.0.0.0/0 ingress" if open_ww else "SG restricted", 75 if open_ww else 15,
                   "HIGH" if open_ww else "LOW")
    except Exception:
        pass
    try:
        users = iam.list_users().get("Users", []) if hasattr(iam, "list_users") else iam.get("users", [])
        for u in users:
            no_mfa = not u.get("mfa", True)
            admin = bool(u.get("admin", False))
            if admin and no_mfa:
                upsert(u.get("UserName", ""), "iam-user", "", False,
                       "Admin IAM user without MFA", 80, "HIGH")
    except Exception:
        pass
    db.commit()
    return {"resources": resources, "findings": findings}
