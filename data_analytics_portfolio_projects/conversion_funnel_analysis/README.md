
# User Conversion Funnel Analysis

## Goal
Analyze product funnel stages from signup → activation → add_to_cart → purchase to identify drop-off points.

## Tasks
1. Calculate conversion rates between funnel stages.
2. Identify the stage with the largest drop-off.
3. Visualize funnel performance in Power BI or Tableau.

## Example SQL
SELECT
SUM(signup) AS signup_users,
SUM(activated) AS activated_users,
SUM(added_to_cart) AS cart_users,
SUM(purchased) AS purchasers
FROM funnel_data;

## Skills Demonstrated
- Funnel Analysis
- SQL Aggregation
- Dashboard Visualization
