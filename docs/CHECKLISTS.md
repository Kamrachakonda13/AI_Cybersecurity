# VEYRA Checklist Registry

**Total:** 74 checklists across 11 domains.  
**Source of truth:** `backend/app/services/checklist_registry.py`  
**Chip states:** green → amber → yellow → semi_red → red (worst result in a run wins)

Adding a checklist: edit the Python module, then run `pytest backend/tests/services/test_checklist_registry.py`.

## Summary

| Domain | Count | Essential | Recommended | Optional |
|---|---|---|---|---|
| live_monitoring | 8 | 5 | 3 | 0 |
| identity | 6 | 3 | 3 | 0 |
| endpoint | 7 | 5 | 2 | 0 |
| network_defense | 9 | 4 | 5 | 0 |
| cloud_container | 10 | 5 | 5 | 0 |
| ai_agent | 6 | 4 | 2 | 0 |
| dfir | 5 | 2 | 3 | 0 |
| governance | 8 | 4 | 4 | 0 |
| supply_chain | 5 | 5 | 0 | 0 |
| red_team | 5 | 3 | 2 | 0 |
| blue_team | 5 | 3 | 2 | 0 |
| **Total** | **74** | **43** | **31** | **0** |

## Domains

### live_monitoring (8)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `wifi-ap-baseline-drift` | Wi-Fi AP baseline drift | security_operator | realtime | essential |
| `wifi-tamper-detection` | Wi-Fi tamper detection | security_operator | realtime | essential |
| `ethernet-link-monitor` | Ethernet link monitoring | security_operator | realtime | recommended |
| `device-join-leave-monitor` | New connected device watch | security_operator | realtime | essential |
| `connection-drop-diagnosis` | Connection drop diagnosis | security_operator | realtime | essential |
| `rogue-ap-correlation` | Rogue AP correlation | analyst | realtime | essential |
| `wired-traffic-anomaly` | Wired traffic anomaly | analyst | hourly | recommended |
| `baseline-snapshot-freshness` | Baseline snapshot freshness | security_operator | daily | recommended |

### identity (6)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `mfa-coverage` | MFA coverage | security_admin | daily | essential |
| `privileged-account-review` | Privileged account review | security_admin | weekly | essential |
| `brute-force-detection` | Brute-force detection | security_operator | realtime | essential |
| `session-anomaly` | Session anomaly | analyst | hourly | recommended |
| `service-account-review` | Service account review | security_admin | weekly | recommended |
| `token-expiry` | Long-lived token audit | security_admin | weekly | recommended |

### endpoint (7)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `endpoint-patch-level` | Endpoint patch level | security_operator | daily | essential |
| `endpoint-services-baseline` | Listening services baseline | security_operator | realtime | essential |
| `endpoint-usb-dlp` | USB & DLP event review | security_operator | daily | essential |
| `endpoint-edr-health` | EDR/AV health | security_operator | daily | essential |
| `endpoint-autorun-review` | Autorun / startup review | analyst | daily | recommended |
| `vulnerability-scan-coverage` | Vuln scan coverage | security_operator | weekly | essential |
| `edr-signature-freshness` | EDR signature freshness | security_operator | daily | recommended |

### network_defense (9)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `ids-health` | IDS/NSM health (Suricata) | security_operator | realtime | essential |
| `dns-anomaly-review` | DNS anomaly review | analyst | hourly | recommended |
| `tls-cert-expiry` | TLS certificate expiry | security_operator | daily | essential |
| `network-segmentation-check` | Network segmentation check | analyst | daily | recommended |
| `flow-baseline-drift` | Flow baseline drift | analyst | hourly | recommended |
| `firewall-rule-audit` | Firewall rule audit | security_operator | weekly | essential |
| `waf-health-check` | WAF health check | security_operator | daily | recommended |
| `vpc-flow-log-coverage` | VPC flow log coverage | security_operator | weekly | essential |
| `network-acl-review` | Network ACL review | analyst | weekly | recommended |

### cloud_container (10)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `cloud-public-exposure` | Cloud public exposure review | security_operator | daily | essential |
| `cloud-iam-privilege-drift` | Cloud IAM privilege drift | security_admin | daily | essential |
| `container-image-digest` | Container image digest pinning | security_operator | daily | recommended |
| `k8s-rbac-baseline` | Kubernetes RBAC baseline | security_operator | weekly | recommended |
| `secret-scan-repo` | Secret scan in repos | security_operator | realtime | essential |
| `cloudtrail-coverage` | CloudTrail / audit log coverage | security_operator | daily | essential |
| `encryption-at-rest-audit` | Encryption-at-rest audit | security_operator | weekly | essential |
| `key-rotation-audit` | Key rotation audit | security_admin | monthly | recommended |
| `workload-identity-audit` | Workload identity audit | security_admin | weekly | recommended |
| `cis-benchmark-scan` | CIS benchmark scan | analyst | weekly | recommended |

### ai_agent (6)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `prompt-injection-battery` | Prompt injection battery | analyst | weekly | essential |
| `rag-retrieval-audit` | RAG retrieval audit | analyst | daily | essential |
| `mcp-server-inventory` | MCP server inventory | security_operator | daily | recommended |
| `tool-allowlist-drift` | Agent tool allowlist drift | analyst | realtime | essential |
| `agent-identity-mfa` | Agent identity coverage | security_admin | weekly | essential |
| `trajectory-assurance` | Trajectory assurance | analyst | daily | recommended |

### dfir (5)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `evidence-custody-check` | Evidence chain of custody | analyst | daily | essential |
| `case-sla-tracker` | Case SLA tracker | security_operator | daily | recommended |
| `yara-rule-health` | YARA rule health | analyst | weekly | recommended |
| `timeline-completeness` | Timeline completeness | analyst | daily | recommended |
| `hash-verification` | Evidence hash verification | analyst | weekly | essential |

### governance (8)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `policy-attestation-review` | Policy attestation review | security_admin | monthly | essential |
| `exception-registry` | Exception registry review | security_admin | weekly | essential |
| `control-mapping-coverage` | Control mapping coverage | security_admin | monthly | recommended |
| `evidence-retention-check` | Evidence retention compliance | analyst | monthly | recommended |
| `third-party-risk-review` | Third-party risk review | security_admin | monthly | essential |
| `board-reporting-freshness` | Board & exec reporting freshness | sudo | monthly | recommended |
| `phishing-simulation-results` | Phishing simulation results | security_operator | monthly | recommended |
| `backup-restore-test` | Backup restore test | security_operator | monthly | essential |

### supply_chain (5)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `sbom-freshness` | SBOM freshness | security_operator | daily | essential |
| `dependency-cve-triage` | Dependency CVE triage | analyst | daily | essential |
| `build-provenance-check` | Build provenance verification | security_operator | daily | essential |
| `vendor-access-review` | Vendor access review | security_admin | weekly | essential |
| `ci-cd-pipeline-integrity` | CI/CD pipeline integrity | security_operator | daily | essential |

### red_team (5)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `engagement-scope-verification` | Engagement scope verification | analyst | weekly | essential |
| `roe-boundary-enforcement` | ROE boundary enforcement | analyst | realtime | essential |
| `tooling-hygiene` | Red-team tooling hygiene | analyst | weekly | recommended |
| `cleanup-verification` | Post-engagement cleanup verification | analyst | weekly | essential |
| `finding-handoff-completeness` | Finding handoff completeness | analyst | weekly | recommended |

### blue_team (5)

| ID | Name | Owner | Cadence | Tier |
|---|---|---|---|---|
| `detection-rule-coverage` | Detection rule coverage (ATT&CK) | analyst | weekly | essential |
| `runbook-currency` | Runbook currency | security_operator | monthly | essential |
| `tabletop-cadence` | Tabletop exercise cadence | security_operator | monthly | recommended |
| `purple-feedback-loop` | Purple-team feedback loop | analyst | weekly | recommended |
| `mttd-mttr-tracking` | MTTD / MTTR tracking | security_operator | weekly | essential |
