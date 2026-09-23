# Service Architecture

The platform consists of five backend services: auth-service, billing-service, docs-service, analytics-service, and notification-service.

**auth-service** handles authentication and API key issuance. It depends on the internal Identity Database and stores session tokens. It is classified INTERNAL.

**billing-service** processes payments and stores customer transaction records. It depends on auth-service for API authentication and on the internal Ledger Database. It is classified CONFIDENTIAL.

**docs-service** serves user documentation and internal runbooks. It depends on auth-service for API authentication and on Object Storage for content. It is classified INTERNAL.

**analytics-service** aggregates usage metrics. It depends on billing-service for transaction data and on the internal Warehouse. It is classified CONFIDENTIAL.

**notification-service** sends emails and alerts. It depends on auth-service for API authentication and on the Message Queue. It is classified PUBLIC.

All services use the standard retry policy. Billing-service and analytics-service must also comply with the data retention policy. Only docs-service and notification-service may be deployed during change freeze windows.