# VEYRA SaaS Platform Ready Plan

*Transforming VEYRA from POC to a multi-tenant security governance SaaS business*

---

## Executive Summary

VEYRA v5.0 possesses strong foundational architecture for a security-governed control plane, with governed execution, approval gating, and evidence provenance already built. This plan outlines the transformation required to take it from a single-user POC to a **multi-tenant SaaS platform** capable of serving enterprises like Tesla, Microsoft, and LinkedIn divisions.

**Timeline**: 12-18 months
**Estimated Investment**: $500K-2M (development + compliance + infra)
**Target Market**: Enterprise security teams, SOCs, DevSecOps groups, regulated industries

---

## 1. Architecture Overview

### 1.1 Multi-Tenant SaaS Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CUSTOMER FACING LAYER                     │
├─────────────────────┬─────────────────────┬───────────────────────┤
│   Web App (React)   │   Customer API      │   Admin Portal        │
│   (per-tenant CSS)  │   (versioned REST)  │   (tenant management) │
└─────────────────────┴─────────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                              │
├─────────────────────┬─────────────────────┬───────────────────────┤
│  Rate Limiting      │  API Versioning     │  Request Validation   │
│  Auth Middleware    │  Throttling         │  Input Sanitization   │
└─────────────────────┴─────────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE APPLICATION LAYER                         │
├─────────────────────┬─────────────────────┬───────────────────────┤
│  Auth Service       │  Tenant Service     │  Job Execution        │
│  (OIDC/SAML)        │ (Tenant isolation) │   Engine (workers)    │
├─────────────────────┼─────────────────────┼───────────────────────┤
│  Billing Service    │  Notification Svc   │  Evidence Ingestion   │
│  (Stripe integration)│ (email/webhook)    │   API                 │
├─────────────────────┼─────────────────────┼───────────────────────┤
│  Monitoring         │  Cache (Redis)      │  Job Queue (RabbitMQ) │
│  (Prometheus/Grafana)│                    │                       │
└─────────────────────┴─────────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                     │
├─────────────────────┬─────────────────────┬───────────────────────┤
│  Primary DB (Postgres)   │  Cache (Redis)    │  Object Storage (S3)  │
│  - Schema per tenant       │  Session store    │  Evidence artifacts   │
│  - Row-level security      │  Rate limits      │  Audit logs           │
│  - Tenant isolation        │                   │                       │
└─────────────────────┴─────────────────────┴───────────────────────┘
```

### 1.2 Key Design Principles

- **Fail-closed by default**: All high-impact actions require explicit approval
- **Tenant isolation**: Complete data and resource isolation between customers
- **Provenance-first**: Every action, evidence artifact, and job has SHA-256 traceability
- **Worker isolation**: Third-party tools run on customer-provisioned or VEYRA-managed isolated workers
- **Auditability**: Immutable audit trail for all operations (SOC 2 requirement)

---

## 2. Multi-Tenant Design

### 2.1 Tenant Isolation Strategies

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Schema-per-tenant** | Separate database schema per tenant | Strongest isolation, easy per-tenant backups | Higher operational overhead |
| **Database-per-tenant** | Individual PostgreSQL database per tenant | Maximum isolation, independent scaling | Highest cost, more DB instances |
| **Row-level security** | Single DB with `tenant_id` column + RLS policies | Cost-effective, simpler ops | Requires careful RLS policy management |
| **Global DB, partitioned data** | Single DB, data partitioned by tenant_id | Simplest ops, good performance | Smaller tenant isolation boundary |

**Recommendation**: **Row-level security with schema-per-tenant for high-security customers**. Start with RLS, add schema-per-tenant for enterprise tier.

### 2.2 Tenant Schema Design

Add `tenant_id` to core tables (via migration):

```sql
-- Core tables needing tenant_id
ALTER TABLE user_accounts ADD COLUMN tenant_id UUID;
ALTER TABLE worker_nodes ADD COLUMN tenant_id UUID;
ALTER TABLE security_tool_jobs ADD COLUMN tenant_id UUID;
ALTER TABLE security_evidence ADD COLUMN tenant_id UUID;
ALTER TABLE tool_definitions ADD COLUMN tenant_id UUID;
ALTER TABLE tool_releases ADD COLUMN tenant_id UUID;

-- Enable RLS
ALTER TABLE user_accountS ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_tool_jobs ENABLE ROW LEVEL SECURITY;
-- ... etc

-- Create policies
CREATE POLICY "users can read own tenant data" ON user_accounts
USING (auth.role() = 'admin' OR tenant_id = current_setting('app.tenant_id')::uuid);
```

### 2.3 Tenant Lifecycle

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Trial    │────▶ │  Active │────▶ │  Paid   │
│ (14-day)  │     │         │     │         │
└─────────┘     └─────────┘     └─────────┘
     │              │              │
     │              │              ▼
     │              └────────────▶ │  Cancelled
     │                   │         │
     │                   └───────────┘
     ▼
└─────────▶ │  Deleted (90-day retention)
```

---

## 3. Infrastructure & Deployment

### 3.1 Kubernetes Architecture

```yaml
# Helm chart structure
veyra/
├── charts/
│   └── veyra/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── _helpers.tpl
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   ├── ingress.yaml
│       │   ├── hpa.yaml
│       │   ├── pdb.yaml
│       │   ├── configmap.yaml
│       │   ├── secret.yaml
│       │   ├── pvc.yaml
│       │   ├── cronjob.yaml (evidence cleanup)
│       │   └── hpa-autoscaler.yaml
│       └── crds/
│           ├── tenant.crd.yaml
│           ├── user.crd.yaml
│           └── job.crd.yaml
├── values-prod.yaml
└── values-staging.yaml
```

### 3.2 Component Deployment

| Component | Resource Requests | Resource Limits | Notes |
|-----------|------------------|-----------------|-------|
| **API Server** | 250m CPU, 512Mi memory | 1 CPU, 1Gi | Autoscale based on job queue depth |
| **Worker Claiming** | 100m CPU, 256Mi memory | 500m CPU, 512Mi | Short-lived, scales on demand |
| **Redis** | 500m CPU, 1Gi memory | 1CPU, 2Gi | Cluster mode, persistence |
| **Postgres** | 1 CPU, 2Gi memory | 2CPU, 4Gi | HA setup, 3 replicas, PgBouncer |
| **MinIO/S3** | 1 CPU, 1Gi memory | 2CPU, 2Gi | Object storage for evidence artifacts |
| **Prometheus** | 500m CPU, 1Gi memory | 1CPU, 2Gi | Scrape API, worker metrics |
| **Grafana** | 250m CPU, 512Mi memory | 500m CPU, 1Gi | Dashboards, alerts |

### 3.3 Environment Parity

```
Development:      Local Docker Compose + MinIO
Staging:          K8s cluster (dedicated) + real infrastructure
Production:       Multi-region K8s + Redis Cluster + Postgres HA + S3
```

### 3.4 Disaster Recovery

- **RPO**: 1 hour (continuous Postgres WAL shipping)
- **RTO**: 4 hours (automated failover to secondary region)
- **Daily backups**: Automated Postgres snapshots to S3 (encrypted, versioned)
- **Cross-region replication**: For enterprise tier
- **Backup retention**: 30 days automated + 90 days on-request

---

## 4. Security & Compliance

### 4.1 Security Controls

| Control | Implementation | Maturity |
|---------|---------------|----------|
| **Transport Security** | TLS 1.3 everywhere, HTTPS-only | ✅ Already in place |
| **Authentication** | OIDC/SAML2, API keys for service-to-service | ❌ Needs building |
| **Authorization** | RBAC + ABAC with tenant scoping | ⚠️ Partial (role-based only) |
| **Secret Management** | HashiCorp Vault or AWS Secrets Manager | ❌ Needs building |
| **Rate Limiting** | Per-tenant limits, global caps | ⚠️ Basic in API gateway |
| **Input Validation** | JSON schema validation on all endpoints | ⚠️ Partial |
| **Dependency Scanning** | Dependabot, Snyk, Trivy on CI | ⚠️ Needs configuring |
| **Container Scanning** | Trivy, Grype on image build | ⚠️ Needs configuring |
| **WAF** | AWS WAF / Cloudflare Bot Management | ❌ Needs configuring |
| **DLP** | Outbound data scanning, classification | ❌ Needs building |

### 4.2 Compliance Framework

| Standard | Requirements | VEYRA Status |
|----------|-------------|--------------|
| **SOC 2 Type II** | Access control, encryption, monitoring | ⚠️ Partial |
| **ISO 27001** | ISMS, risk assessment, A.9-A.18 | ❌ Needs building |
| **GDPR** | Data subject rights, right to deletion | ⚠️ Partial (audit events need retention policy) |
| **HIPAA** | PHI protection, BAAs, access controls | ❌ Needs significant work |
| **PCI-DSS** | If processing payments | ❌ (Stripe handles this) |
| **NIST CSF** | Identify, protect, detect, respond, recover | ⚠️ Partial |

### 4.3 Data Protection

- **Encryption-at-rest**: PostgreSQL pg_encryptor, S3 SSE-KMS
- **Encryption-in-transit**: TLS 1.3 everywhere
- **Key management**: AWS KMS / HashiCorp Vault
- **Data retention**: Configurable per tenant (default: 90 days evidence, 1 year audit logs)
- **Right to delete**: API endpoint to anonymize/remove tenant data (GDPR compliance)
- **Data residency**: Per-tenant region selection (us-east-1, eu-west-1, ap-southeast-1)

---

## 5. Authentication & Authorization

### 5.1 Identity Providers

- **Primary**: OIDC (Auth0, Google Workspace, Azure AD, Okta)
- **Secondary**: SAML 2.0 for enterprise SSO
- **API keys**: For service-to-service (worker-to-API communication)

### 5.2 Multi-Tenant Auth Flow

```
1. User → Identity Provider (Auth0/Okta) → Gets JWT with claims
2. JWT → API Gateway → Verifies signature + tenant claim
3. API → Checks tenant_id matches authenticated user's tenant
4. Action → Executes with tenant-scoped permissions
5. Audit → Logs tenant_id, user_id, action, outcome
```

### 5.3 Permission Model

```
Roles (per-tenant):
- admin: Full access, user/mgmt, job creation, billing view
- operator: Can create/manage jobs, view evidence
- viewer: Read-only, can view jobs and evidence
- auditor: Read-only, compliance-focused views

Permissions (per-tenant, per-resource):
- create:security_tool_jobs
- read:security_tool_jobs/{id}
- update:security_tool_jobs/{id}
- delete:security_tool_jobs/{id} (soft delete + audit)
- evidence:ingest
- evidence:download
- tenant:manage
- user:invite
```

### 5.4 API Authentication

```http
# Bearer token with tenant context
Authorization: Bearer eyJhbGciOiF... . eyJzdWIiOiJ... . tenant_id: tenant-123

# Service-to-service (worker)
X-VEYRA-Worker-Token: worker-signing-secret-hmac
X-VEYRA-Worker-Id: worker-v50-001
```

---

## 6. API Design & Versioning

### 6.1 API Versioning Strategy

```
Current:   /api/v1/ (unstable, rapidly changing)
Target:    /api/v1/ (stable, version-locked)
Deprecation: /api/v1 -> /api/v2 after 12 months notice
```

### 6.2 API Contract Examples

```http
# Create tenant
POST /api/v1/tenancies
Content-Type: application/json
Authorization: Bearer <admin-jwt>

{
  "name": "Acme Corp",
  "plan": "pro",
  "region": "us-east-1",
  "settings": {
    "max_concurrent_jobs": 10,
    "evidence_retention_days": 90
  }
}

# Response
{
  "id": "ten-abc123",
  "status": "creating",
  "endpoint": "https://veyra.acme-corp.com",
  "api_base": "/api/v1",
  "credentials": {
    "client_id": "client-abc123",
    "client_secret": "sk_live_...",
    "webhook_url": "https://veyra.acme-corp.com/webhooks"
  }
}
```

### 6.3 Webhooks for Customer Integration

| Event | Payload | Description |
|-------|---------|-------------|
| `job.created` | `{job_id, tenant_id, status, tool, created_at}` | New governed job created |
| `job.status_changed` | `{job_id, old_status, new_status, tenant_id}` | Status transition |
| `evidence.ready` | `{artifact_id, job_id, sha256, collected_at}` | Evidence available |
| `billing.invoice_generated` | `{invoice_id, amount, period, tenant_id}` | Monthly billing |
| `trial.expiring` | `{tenant_id, days_remaining}` | Trial renewal reminder |

### 6.4 API Rate Limiting

```
Per-tenant limits:
- 1000 requests/minute (burst: 5000)
- 10000 requests/hour
- 100000 requests/day

Per-endpoint overrides:
- /api/v1/tenancies: 10/min (admin only)
- /api/v1/jobs: 100/min per tenant
- /api/v1/evidence: 50/min per tenant
```

---

## 7. Observability & Monitoring

### 7.1 Metrics to Track

| Category | Metric | Purpose |
|----------|--------|---------|
| **Business** | `tenants.active` | Count of active tenants |
| | `tenants.churn_rate` | Monthly churn percentage |
| | `billing.mrr` | Monthly recurring revenue |
| **Security** | `jobs.failed_validation` | Security gate failures |
| | `jobs.worker_timeout` | Worker execution timeouts |
| | `auth.failed_logins` | Authentication attack detection |
| **Performance** | `api.request_duration` | P95/P99 latency |
| | `worker.claim_time` | How fast workers claim jobs |
| | `api.error_rate` | 5xx error rate |
| **SLA** | `sla.job_completion` | % of jobs completed within SLA |
| | `sla.evidence_ingestion` | Evidence turnaround time |

### 7.2 Dashboards

**Executive Dashboard** (C-level):
- MRR, ARR, churn, CAC, LTV
- Active tenants, growth rate
- SLA compliance percentage

**Security Dashboard** (SOC/SecOps):
- Jobs by status (pending/approved/queued/completed)
- Worker health and throughput
- Approval cycle times
- Evidence classification distribution

**Technical Dashboard** (Engineering):
- API latency percentiles
- Error rates by endpoint
- Worker claim rates
- Database connection pool usage
- Queue depths (RabbitMQ)

### 7.3 Alerting Rules

```yaml
# Alert if job stuck in pending_approval > 24h
- alert: JobStuckPendingApproval
  expr: job_status{status="pending_approval"} > 0 and time() - job_created_at > 86400
  for: 1h
  labels: severity critical
  annotations:
    summary: "Job stuck in pending approval for 24h"
    description: "Job {{ $labels.job_id }} has been pending approval for over 24 hours"

# Alert if worker not claiming jobs
- alert: WorkerClaimRateLow
  expr: (count(worker_claimed_total) / count(job_created_total)) < 0.1
  for: 5m
  labels: severity warning
  annotations:
    summary: "Low worker claim rate"
    description: "Only {{ $value | percent }} of jobs are being claimed by workers"
```

### 7.4 Logging Strategy

- **Structured JSON logs**: `{"timestamp", "level", "tenant_id", "user_id", "job_id", "action", "outcome", "duration"}`
- **Correlation IDs**: Trace ID propagated through all async operations
- **Log retention**: 30 days hot storage, 90 days archived, indefinite audit logs
- **Log shipping**: Fluent Bit → S3 → Athena/QuickSight for ad-hoc analysis

---

## 8. Billing & Metering

### 8.1 Pricing Tiers

| Tier | Price/Month | Key Features |
|------|------------|--------------|
| **Free/Trial** | $0 | 14-day trial, 3 jobs/month, lab environment only |
| **Pro** | $99 | Unlimited jobs, approved_worker environment, email support |
| **Enterprise** | $499 | Unlimited everything, isolated workers, phone support, SLA |
| **Custom** | Negotiated | On-premises, dedicated instances, customized SLA |

### 8.2 Metering Events

| Meter | Unit | Calculation |
|-------|------|-------------|
| `jobs_submitted` | per job | Count of `POST /api/v1/jobs` |
| `jobs_completed` | per job | Count of jobs reaching `completed` status |
| `worker_hours` | hours | Sum of worker execution time / 3600 |
| `evidence_gb` | GB | Total evidence data size / (1024^3) |
| `api_calls` | calls | Count of all API requests (per endpoint) |
| `storage_gb` | GB | Total object storage used |

### 8.3 Billing Integration (Stripe)

```yaml
# Stripe products
products:
  free:      "VEYRA Free Trial"
  pro:       "VEYRA Pro Subscription"
  enterprise:"VEYRA Enterprise Subscription"

# Stripe prices (per month)
prices:
  free:      "price_1free_trial"   # trial period 14 days
  pro:       "price_1pro_monthly"
  enterprise:"price_1enterprise_monthly"

# Usage-based metering
metrics:
  jobs_submitted:      "jobs_submitted_monthly"
  worker_hours:        "worker_hours_monthly"
  evidence_gb:         "evidence_gb_monthly"
```

### 8.4 Invoice & Payment Workflow

```
Customer → Stripe Checkout → Stripe Portal → Webhook → VEYRA API → Update tenant status → Send receipt email
```

---

## 9. DevOps & CI/CD

### 9.1 Git Workflow

```
Branch Strategy:
- main: Production-ready code (protected)
- develop: Integration branch
- feature/*: New features
- fix/*: Bug fixes
- hotfix/*: Production critical fixes

Release Process:
1. Feature completed on feature/* 
2. PR to develop (code review required)
3. When develop stable: create release tag vX.Y.Z
4. CI pipeline: test → build → scan → deploy to staging
5. Manual approval: deploy to production
6. Post-deploy: smoke tests + SLA verification
```

### 9.2 CI Pipeline

```
.github/workflows/ci.yml
1. ✓ Lint (ESLint, Prettier)
2. ✓ Typecheck (if TypeScript added)
3. ✓ Unit tests (vitest)
4. ✓ Integration tests (supertest)
5. ✓ Security scan (trivy, npm audit)
6. ✓ Build Docker image
7. ✓ Push to ghcr.io
8. ✓ Deploy to staging (K8s)
9. ✓ End-to-end tests against staging
10. ✓ Publish documentation
```

### 9.3 Infrastructure as Code

- **Terraform**: Cloud resources (AWS/Azure/GCP)
- **Helm**: K8s applications
- **Kustomize**: K8s overlays per environment
- **Pre-commit**: Husky hooks, linting, formatting

### 9.4 Secrets Management

```
CI/CD → HashiCorp Vault → Inject into K8s secrets
↓
Never hardcode in repo
↓
Rotation: 90-day rotation policy
↓
Access: Just-in-time (JIT) via Vault Agent
```

---

## 10. Customer Onboarding

### 10.1 Onboarding Flow

```
1. Sign-up → Email verification → Trial activation
2. Setup wizard:
   a. Company name, domain, billing info
   b. SSO configuration (or password auth)
   c. Worker node provisioning (or use VEYRA-managed)
   c. Tool catalog configuration
   d. Approval workflow setup
3. Import existing assets (optional)
4. Assign team members & roles
5. First governed job creation
6. Success! → Value realization
```

### 10.2 Trial Workflow

```
14-day trial → 3 governed jobs free → Job count resets → Upgrade prompt
- Limit: max 3 concurrent jobs
- Limit: lab environment only
- Limit: no isolated worker execution
- Evidence retained 7 days post-trial
```

### 10.3 Customer Success

- **Onboarding call** (Enterprise tier)
- **Documentation**: Interactive tutorials, API reference, best practices
- **Community forum**: Self-service help
- **SLA reporting**: Monthly health reports to customers
- **Quarterly business reviews** (QBR): Enterprise tier only

---

## 11. Data Protection & Privacy

### 11.1 GDPR Compliance

| Right | Implementation |
|-------|---------------|
| **Right to access** | `GET /api/v1/tenant/data` - export all tenant data as ZIP |
| **Right to rectification** | Update API to correct inaccurate personal data |
| **Right to erasure** | `DELETE /api/v1/tenant` - anonymize data, keep pseudonymized audit records |
| **Data portability** | Export in JSON/CSV format, API for integration |
| **Retention policy** | Configurable per tenant, default 90 days evidence, 1 year audit logs |

### 11.2 Data Classification

```
Classification levels (per tenant):
- public: No restrictions, shareable
- internal: Tenant-internal only
- confidential: Need-to-know, encrypted at rest
- restricted: Legal/compliance, encrypted + access logged
```

### 11.3 Privacy by Design

- **Data minimization**: Only collect what's needed for governance
- **Purpose limitation**: Data used only for stated security governance purposes
- **Storage limitation**: Automatic cleanup per retention policy
- **Integrity**: SHA-256 hashing, checksum verification
- **Confidentiality**: Role-based access, encryption, network isolation

---

## 12. Disaster Recovery & SLA

### 12.2 SLA commitments

| Metric | SLA (Pro) | SLA (Enterprise) |
|--------|-----------|------------------|
| **Uptime** | 99.5% monthly | 99.9% monthly |
| **Job completion** | 4h average | 1h average |
| **Evidence ingestion** | 2h maximum | 30m maximum |
| **Support response** | 24h business hours | 4h any time |
| **Backup RPO** | 24 hours | 1 hour |
| **Backup RTO** | 4 hours | 1 hour |

### 12.3 Incident Response

```
Severity Critical (security breach):
- pager duty alert → 15 min response
- Incident bridge within 30 min
- Root cause within 2h
- Customer notification within 4h
- Resolution within 8h

Severity High (major functionality down):
- 1h response
- Root cause within 4h
- Resolution within 24h

Severity Medium (degraded performance):
- 4h response
- Resolution within 72h

Severity Low (cosmetic/minor):
- 24h response
- Resolution within 5 business days
```

### 12.4 Runbooks

Runbooks stored in wiki, triggered by on-call pager:

```
1. Incident identification (alert → investigation → confirmation)
2. Impact assessment (affected tenants, data at risk)
3. Containment (prevent further escalation)
4. Eradication (remove root cause)
5. Recovery (restore services from backup if needed)
6. Post-mortem (blameless analysis, action items)
7. Communication (status updates to affected customers)
```

---

## 13. Roadmap & Prioritization

### Phase 1: Foundation (0-3 months)
- [ ] PostgreSQL migration with tenant isolation (RLS)
- [ ] OIDC authentication (Auth0 integration)
- [ ] Multi-tenant API endpoints
- [ ] Billing integration (Stripe basic)
- [ ] Basic monitoring (Prometheus + Grafana)
- [ ] Dockerized deployment to K8s
- [ ] CI/CD pipeline

### Phase 2: Core SaaS (3-6 months)
- [ ] Webhook system for customer integrations
- [ ] Role-based access control (RBAC) per tenant
- [ ] Pricing tiers and metering
- [ ] Evidence retention policies
- [ ] Customer onboarding flow
- [ ] Documentation site
- [ ] SLA monitoring dashboards

### Phase 3: Enterprise Features (6-12 months)
- [ ] Schema-per-tenant option for high-security customers
- [ ] On-premises deployment option
- [ ] Advanced compliance (SOC 2 audit prep)
- [ ] GDPR data deletion tools
- [ ] Multi-region deployment
- [ ] Custom branding/white-labeling
- [ ] Advanced RBAC/ABAC

### Phase 4: Scale & Maturity (12-18 months)
- [ ] Kubernetes auto-scaling optimization
- [ ] Predictive scaling (ML-based)
- [ ] Customer success program
- [ ] Partner ecosystem integration
- [ ] Marketplace for extensions/integrations
- [ ] AI-assisted security recommendations
- [ ] Global compliance certifications (ISO 27001)

### Phase 5: Market Expansion (18-24 months)
- [ ] Regional data residency (EU, APAC, Americas)
- [ ] Industry-specific compliance (HIPAA, FINRA)
- [ ] Channel partner program
- [ ] International pricing/localization
- [ ] ABM (Account-Based Marketing) for enterprise
- [ ] Public API developer program

---

## 14. Immediate Action Items (Start Today)

### Week 1-2
1. [ ] Create `tenants` table migration with `tenant_id`
2. [ ] Add `tenant_id` to core entities (user_accounts, jobs, evidence, workers)
3. [ ] Implement basic RLS policies
4. [ ] Set up PostgreSQL on K8s with HA

### Week 3-4
5. [ ] Integrate Auth0 (or Keycloak) for OIDC
6. [ ] Add tenant context to JWT claims
7. [ ] Implement tenant-scoped API middleware
8. [ ] Create tenant API endpoints (CRUD)

### Week 5-6
9. [ ] Set up Stripe integration (basic pricing)
10. [ ] Create webhook endpoints structure
11. [ ] Build monitoring dashboards (basic)
12. [ ] Configure logging (structured JSON)

### Week 7-8
13. [ ] Dockerize and deploy to staging K8s
14. [ ] Set up Helm chart structure
15. [ ] CI/CD pipeline implementation
16. [ ] Disaster recovery backup configuration

### Week 9-10
17. [ ] Customer onboarding flow prototype
18. [ ] Trial workflow implementation
19. [ ] Documentation site skeleton
20. [ ] Security scan pipeline (Trivy)

### Week 11-12
21. [ ] Beta test with internal team
22. [ ] Fix critical bugs from beta
23. [ ] Pricing page development
24. [ ] Launch marketing site

---

## 15. Technology Stack Recommendations

### 15.1 Backend
- **Language**: Python 3.11 (FastAPI) - currently used, keep it
- **Framework**: FastAPI (already architected well)
- **Database**: PostgreSQL 15+ with PgBouncer
- **Cache**: Redis 7+ (cluster mode)
- **Queue**: RabbitMQ or Redis Streams
- **Background tasks**: Celery with Redis broker

### 15.2 Frontend
- **Framework**: React 19 + Vite (already in use)
- **State**: React Query (for server-state management)
- **Auth**: NextAuth.js or custom OIDC
- **UI Library**: shadcn-ui or Mantine (modern, accessible)
- **Charts**: Chart.js or Recharts (for dashboards)

### 15.3 Infrastructure
- **Container orchestration**: Kubernetes (EKS/GKE/AKS)
- **Infrastructure as Code**: Terraform
- **Container registry**: GitHub Container Registry (ghcr.io)
- **Object storage**: Amazon S3 / MinIO (S3-compatible)
- **CDN**: CloudFront / Fastly (for static assets)
- **DNS**: Route 53 / Gandi.NET

### 15.4 Observability
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Logging**: structured JSON → S3 → Athena
- **Alerting**: Alertmanager + PagerDuty
- **Error tracking**: Sentry

### 15.5 Security
- **Secret management**: HashiCorp Vault
- **WAF**: AWS WAF + Cloudflare
- **Scanning**: Trivy (container), Snyk (dependencies)
- **API security**: FastAPI security dependencies
- **Rate limiting**: API gateway (Traefik/Envoy with Lua)

---

## Appendix: Migration Path from Current State

```
Current (POC):
- SQLite database
- Single user (admin)
- Local file storage for evidence
- No tenant isolation
- No authentication (session-based only)
- Docker Compose deployment

Target (SaaS):
- PostgreSQL with tenant isolation
- OIDC authentication + API keys
- S3 object storage with encryption
- Row-level or schema-per-tenant isolation
- JWT + tenant claims in every request
- Kubernetes Helm deployment
- Stripe billing + metering
- Prometheus/Grafana monitoring
- Full audit trail + retention policies
```

---

*This plan requires approximately 1,200-1,800 hours of development work across 12-18 months, depending on team size and existing infrastructure. The core governance architecture of VEYRA provides an excellent foundation - the primary work is around multi-tenancy, enterprise security controls, and operational reliability rather than rebuilding the fundamental assessment workflow.*

*For a small team (2-3 engineers), prioritize Phase 1 items first, then iterate through phases based on customer feedback and market validation.*