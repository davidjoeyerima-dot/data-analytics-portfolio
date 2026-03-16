select
count(*) as total_users,

sum(signup) as signup_users,
sum(activated) as activated_users,
sum(added_to_cart) as cart_users,
sum(purchased) as purchasers,

round(sum(activated) * 100.0 / nullif(sum(signup), 0), 2) as activation_rate,
round(sum(added_to_cart) * 100.0 / nullif(sum(activated), 0), 2) as cart_rate,
round(sum(purchased) * 100.0 / nullif(sum(added_to_cart), 0), 2) as purchase_rate,

round(100 - (sum(activated) * 100.0 / nullif(sum(signup), 0)), 2) as signup_dropoff,
round(100 - (sum(added_to_cart) * 100.0 / nullif(sum(activated), 0)), 2) as activation_dropoff,
round(100 - (sum(purchased) * 100.0 / nullif(sum(added_to_cart), 0)), 2) as cart_dropoff

from funnel_data;
