# SaaS Analytics Requirements

## Business Context
We run a B2B SaaS platform with multiple subscription tiers. We need analytics on user engagement, subscription lifecycle, and product usage patterns.

## Key Business Questions
1. What is our Monthly Recurring Revenue (MRR) by plan tier?
2. What is our churn rate by cohort (signup month)?
3. Which features are most used by paying vs. free users?
4. What is the average session duration by plan tier?
5. How does feature usage correlate with retention?
6. What are our daily/weekly/monthly active user counts?

## Source Data
- **users**: User accounts with plan info and activity timestamps
- **subscriptions**: Subscription lifecycle (start, end, MRR, status)
- **events**: User activity events (page views, feature usage, API calls, logins)

## Requirements
- Track subscription metrics: MRR, churn, upgrades, downgrades
- Analyze user engagement by event type and feature
- Support cohort analysis by signup date
- Dimension by user, plan tier, date, and event type
- Handle SCD Type 2 for plan changes over time
