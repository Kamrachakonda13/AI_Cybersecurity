# Authentication Policy

The system requires multi-factor authentication for all administrative accounts. Administrative accounts include any user with write access to production systems, billing, or user management.

Passwords must be at least 12 characters and rotated every 90 days. The system rejects passwords that appear in the last five rotation histories for the same user.

Failed login attempts trigger a 15-minute lockout after 5 consecutive failures. Lockouts are per-user, per-IP; a user locked out from one IP can still log in from another.

API keys are issued per service and rotate automatically every 30 days. Revoked keys remain valid for a 24-hour grace period to allow in-flight requests to complete. Key rotation is enforced at the gateway layer, not at the service layer.

Session tokens expire after 8 hours of inactivity or 24 hours absolute, whichever comes first. Refresh tokens are single-use and tied to the originating device fingerprint.