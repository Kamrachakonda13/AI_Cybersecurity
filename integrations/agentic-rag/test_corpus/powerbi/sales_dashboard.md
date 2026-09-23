# Sales Performance Dashboard

## Overview

The Sales Performance Dashboard tracks revenue, deal pipeline, and quota
attainment across all sales regions.

## Datasets

- **Sales_Transactions** (fact table): one row per closed deal
- **Sales_Reps** (dimension): sales rep names, regions, managers
- **Quota_Targets** (dimension): quarterly quotas by region

## Key metrics

- Monthly Recurring Revenue (MRR)
- Pipeline coverage ratio
- Quota attainment percentage
- Average deal size

## Refresh schedule

Refreshes every 4 hours from the data warehouse.