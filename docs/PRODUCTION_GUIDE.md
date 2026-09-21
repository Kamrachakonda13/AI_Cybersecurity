# VEYRA production guide — scheduler, secrets, cloud, backups

## Environment (backend)

| Var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | sqlite fallback | Postgres in compose; **back up the `aegisx_pg` volume** |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed console origins |
| `COLLECTOR_TOKEN` | empty (= open) | Set to a long random string → all machine ingest + heartbeat require `X-Collector-Token` |
| `NVD_API_KEY` | empty | Optional NVD key (raises rate limit 5/s → 50/s) |
| `THREATINTEL_AUTO_REFRESH` | `false` | `true` → 24h KEV background loop in the API process |
| `AWS_ACCESS_KEY_ID/SECRET` | — | Read-only IAM for `/api/cloud/scan` (else 501 guidance) |

```bash
export COLLECTOR_TOKEN="$(python3 -c 'import secrets;print(secrets.token_hex(24))')"
docker compose up --build -d   # compose forwards the three vars (see docker-compose.yml)
```

## Schedules to set

- KEV: `THREATINTEL_AUTO_REFRESH=true` **or** cron `POST /api/threat-intel/refresh {"sources":["kev"]}` daily.
- Prowler in CI → `POST /api/cloud/import-prowler` per run (service account + token).
- Endpoint agent: `--once` via cron/launchd every 5–15 min **or** `--interval 300` daemon.
- Postgres volume snapshot before upgrades.

## Production checklist

1. Tokens/keys set, `.env` never committed. 2. Postgres persistent + backed up.
3. HTTPS termination in front of :3000/:8000 (compose exposes plain HTTP for lab).
4. Collectors use token headers; audit log reviewed (`GET /api/audit`).
5. KEV age checked (`GET /api/threat-intel/cves` → `updated_at`); MITRE unmapped ≈ 0.
6. SOAR runs show completed approvals; AI eval verdict LOW before gateway release.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
