# Security corpora

This directory holds corpus data for the Security RAG (Phase 5) and the
prompt injection firewall (Phase 9).

## Committed files (hand-crafted, our work)

- `injections_train.jsonl` — 78 hand-crafted injection prompts (train split)
- `injections_test.jsonl` — 18 hand-crafted injection prompts (held-out test)
- `benign_test.jsonl` — 239 benign prompts (mixed sources)

Regenerate with:
    python -m src.security.generate_corpus

## Gitignored files (public data, fetched separately)

These are large (~50 MB total) and produced from public sources. They are
not committed to keep the repo small.

### `attack.json` — MITRE ATT&CK Enterprise (STIX 2.1)
- Source: https://github.com/mitre-attack/attack-stix-data
- License: MITRE's ATT&CK Terms of Use (public release)
- Fetch:
      curl -L -o data/security/attack.json \\
        https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json

### `kev.json` — CISA Known Exploited Vulnerabilities
- Source: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- License: US Government public domain
- Fetch:
      curl -L -o data/security/kev.json \\
        https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json

### `security_corpus.json` — derived corpus for Security RAG
Produced by the Phase 5 ingestion pipeline from the two sources above.
Regenerate with:
    python -m src.security_ingest

### Runtime files (gitignored)

- `blocked.jsonl` — append-only log of blocked injection attempts
- `training_embeddings.npz` — cached embeddings for the injection classifier

Both are regenerated at runtime and not committed.
