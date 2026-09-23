# Platform Overview Wiki

## Summary

The Acme platform is a multi-tenant SaaS offering for enterprise workflow
automation. It consists of five backend services and a unified API gateway.

## Architecture

- **API Gateway**: single entry point, handles authentication and rate limiting
- **Workflow Engine**: executes customer-defined workflows
- **Integration Service**: connects to third-party systems via webhooks and REST
- **Analytics Service**: aggregates usage metrics and generates reports
- **Notification Service**: sends emails, SMS, and webhook callbacks

## Environments

- dev.acme.internal
- staging.acme.internal
- production.acme.com
