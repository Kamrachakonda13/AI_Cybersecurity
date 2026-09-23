# Slack Thread: Platform Incident #inc-2026-09-14

## Channel: #platform-incidents

**09:15 alice:** Alert: API gateway 5xx rate spiked to 4% in prod

**09:17 bob:** Looking now. Seeing elevated latency on auth-service too.

**09:22 alice:** Checked the last deploy. Nothing landed in the last hour.

**09:35 bob:** Found it. The auth-service session cache is thrashing. Evicting
too aggressively under load.

**09:48 alice:** Bumping cache size from 512MB to 2GB. Rolling restart.

**10:02 bob:** 5xx rate back to 0.1%. Stable.

**10:30 alice:** Post-mortem scheduled for tomorrow. Action item: tune cache
eviction policy.
