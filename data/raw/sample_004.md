# Monitoring and Alerting

All services emit structured logs in JSON format. Logs are shipped to a centralized aggregation platform within 5 seconds of emission.

Metrics are collected at 10-second intervals using a pull-based model. Histogram metrics are aggregated with p50, p95, and p99 percentiles computed server-side.

Alerts are classified into three severity levels. P1 alerts page the on-call engineer immediately via PagerDuty. P2 alerts notify the team Slack channel with a 30-minute response SLA. P3 alerts create tickets for the next business day.

Alert thresholds are tuned to achieve a signal-to-noise ratio above 5:1. Any alert that fires more than 10 times per week without action is flagged for review and either retuned or deleted.

Synthetic monitoring runs every 60 seconds from 4 geographic regions. Failures from 2 or more regions trigger a P1 alert.