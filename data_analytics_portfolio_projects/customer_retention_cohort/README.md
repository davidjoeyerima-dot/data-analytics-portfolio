
# Customer Retention Cohort Analysis

## Goal
Measure user retention over time using cohort analysis.

## Tasks
1. Group users by signup_month.
2. Calculate retention rate across activity_month.
3. Visualize retention matrix using Python or Tableau.

## Example SQL
SELECT signup_month, activity_month, COUNT(DISTINCT user_id)
FROM retention_data
WHERE active=1
GROUP BY signup_month, activity_month;

## Skills Demonstrated
- Cohort Analysis
- Retention Metrics
- Customer Analytics
