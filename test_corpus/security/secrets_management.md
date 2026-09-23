# Secrets Management

All secrets must be stored in one of:

- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

No secrets in source code, environment variables in CI logs, or configuration files checked into git.

Rotation: every 90 days for production secrets, 180 days for development.