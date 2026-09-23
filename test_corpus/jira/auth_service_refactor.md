# ENG-4521: Refactor auth-service token handling

## Summary

Replace the custom JWT implementation with a standard library to reduce
security surface area and improve auditability.

## Acceptance criteria

- [ ] All existing token tests pass
- [ ] Support RS256 in addition to HS256
- [ ] Token revocation list is checked on every request
- [ ] Migration plan documented for existing tokens

## Priority

High — blocks the compliance audit scheduled for Q4.
