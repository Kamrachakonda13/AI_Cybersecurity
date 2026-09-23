# Financial Close Dashboard

## Overview

The Financial Close Dashboard tracks the month-end close process, including
journal entry status, reconciliation completeness, and variance analysis.

## Data sources

- **General_Ledger** (extract): posted transactions and account balances
- **Journal_Entries** (live): pending and posted entries
- **Reconciliation_Status** (extract): account reconciliation progress

## Key metrics

- Days to close
- Unreconciled account count
- Journal entry approval backlog
- Material variance count (>$10K)

## Refresh schedule

Extract refreshes daily at 4 AM UTC.
