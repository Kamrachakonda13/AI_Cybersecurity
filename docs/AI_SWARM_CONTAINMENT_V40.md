# VEYRA v4.0 — AI Swarm Containment

Recent 2026 incidents demonstrate that the key failure mode is not only model capability; it is the combination of autonomy, unintended network reachability, non-human credentials, shared infrastructure and machine-speed coordination.

## Defensive pattern

```text
Agent
  |
  +--> Identity policy --> velocity / privilege baseline
  |
  +--> Tool policy ------> allowlist / approval
  |
  +--> Network policy ---> deny-by-default egress
  |
  +--> Web behavior -----> detect public coordination channels
  |
  +--> Runtime telemetry -> swarm correlation
  |
  +--> External kill path -> emergency stop
  |
  +--> Evidence ----------> signed trace + hashes
```

### Controls

1. **Deny-by-default egress:** simulations must not inherit live internet access through proxy, package repository or metadata-service side channels.
2. **Non-human identity behavior:** baseline API velocity, destination diversity, privilege and tool sequences; freeze identities on severe anomalies.
3. **External collaboration detection:** detect unusual public-site write bursts, repeated coordination markers and cross-site communication patterns.
4. **Emergency stop:** an external control path must be able to halt agent/tool execution without relying on the model to cooperate.
5. **Evidence-first containment:** preserve traces, identity events, network telemetry, worker receipts and artifact hashes before destructive cleanup.
6. **Scope binding:** every agent evaluation has explicit target/scope and cannot infer permission from the presence of a network route.

These controls are defensive. VEYRA does not provide a hack-back capability or an unrestricted agent browser/shell.
