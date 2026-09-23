# Platform Architecture Overview

## Core services

The platform consists of:

1. **auth-service** — handles authentication and API key issuance
2. **billing-service** — processes payments and transactions
3. **docs-service** — serves user documentation
4. **analytics-service** — aggregates usage metrics

## Dependencies

All services depend on auth-service for authentication.
billing-service and analytics-service write to the internal Warehouse.