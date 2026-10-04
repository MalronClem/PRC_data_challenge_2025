# 01 — Billing and budget (Google Cloud)

## Role

Link the Google Cloud project `prc-data-challenge-2025` to an active billing account, which is required to use the Cloud Storage and BigQuery free tier, and keep an eye on spending.

## Why this choice

- The Google Cloud free trial ($300 over 90 days) had already been used and was over: it is available only once per person.
- The free tier ("Always Free") requires an **active** billing account. The expired trial account was therefore upgraded to a full account ("Change" button in the console banner).
- Consequence: there is no safety net anymore. Any usage beyond the free limits is charged to the registered card.

## Configuration

- **Billing account**: "Mon compte de facturation", upgraded to a full account.
- **Project**: `prc-data-challenge-2025`, linked to this billing account.
- **Budget**: "Alerte budget PRC"
  - Period: monthly
  - Scope: the whole billing account (also covers future projects)
  - Amount: €1
  - Thresholds: 50%, 90%, 100%, triggered on **actual** spend
  - Notification: email to billing administrators
- **Spending cap**: not enabled. The "Budgets & caps" feature (in Preview) can pause services when the budget is exceeded. To be studied before enabling.

## Where to find it

Console → Menu ☰ → Billing → Cost control → **Budgets & caps**.

## Costs and limits

- A budget alert **warns but blocks nothing**: services keep running.
- Costs show up in the console with a delay of up to 24 h.
- Google Cloud free tier: no end date, but Google can change it with 30 days' notice.
- Main risk: a handling mistake (resource in a region outside the free tier, forgotten virtual machine), not normal project usage.
