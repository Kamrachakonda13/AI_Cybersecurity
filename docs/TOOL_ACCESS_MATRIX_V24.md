# VEYRA Security Tool Access Matrix (v2.4+)

## User-requested core tools

| Tool | Embedded in VEYRA catalog | Access tier | Execution boundary | API/browser execution |
|---|---|---|---|---|
| Nmap | Yes | Admin | lab/approved worker | No direct shell |
| Metasploit Framework | Yes | Privileged Admin | isolated lab only | No direct shell |
| Burp Suite | Yes | Admin | lab/approved worker | No direct shell |
| SQLMap | Yes | Privileged Admin | lab/approved worker | No direct shell |
| Wireshark | Yes | Admin | analyst workstation | No direct shell |
| Hashcat | Yes | Privileged Admin | offline audit only | No direct shell |

## Access tiers

### ADMIN

Visible only after administrator authorization. Suitable for governed security assessment, defensive analysis, evidence collection and approved worker workflows.

### PRIVILEGED_ADMIN

Requires both:
- `X-VEYRA-Admin-Token`
- `X-VEYRA-Privileged-Admin-Token`

The privileged tier is used for high-impact offensive or credential-related tooling. A valid privileged token is still not sufficient to execute a tool: scope, environment, approval ticket, job state and isolated-worker controls remain required.

## Privileged-admin tools

Metasploit Framework, Core Impact, Impacket, NetExec, Certipy, Kerbrute, Hashcat, John the Ripper, Hydra, Medusa, SQLMap, Masscan, RustScan, Naabu, FFUF, Gobuster, Feroxbuster, Dirsearch, Wapiti and kube-hunter.

## Important implementation note

VEYRA **catalogs and governs** these tools; it does not bundle the third-party tool binaries into the application container. Production deployment should install approved tool versions in dedicated isolated security workers and connect them through signed job contracts. The VEYRA API never exposes an unrestricted browser shell and does not directly execute arbitrary security-tool commands.

## Production recommendation

Replace POC shared tokens with enterprise identity controls: OIDC/SSO, MFA, RBAC/ABAC, PAM/JIT elevation, approval workflows, immutable audit logging and per-worker credentials.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
