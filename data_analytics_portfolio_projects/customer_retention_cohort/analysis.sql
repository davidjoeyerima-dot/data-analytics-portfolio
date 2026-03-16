SELECT
signup_month,
activity_month,
COUNT(DISTINCT user_id) AS active_users
FROM retention_data
WHERE active = 1
GROUP BY signup_month, activity_month
ORDER BY signup_month, activity_month;
