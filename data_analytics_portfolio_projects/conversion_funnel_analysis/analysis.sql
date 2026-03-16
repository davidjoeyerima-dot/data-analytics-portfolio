SELECT
COUNT(*) AS total_users,
SUM(signup) AS signup_users,
SUM(activated) AS activated_users,
SUM(added_to_cart) AS cart_users,
SUM(purchased) AS purchasers,

ROUND(SUM(activated)*100.0/SUM(signup),2) AS activation_rate,
ROUND(SUM(added_to_cart)*100.0/SUM(activated),2) AS cart_rate,
ROUND(SUM(purchased)*100.0/SUM(added_to_cart),2) AS purchase_rate

FROM funnel_data;
