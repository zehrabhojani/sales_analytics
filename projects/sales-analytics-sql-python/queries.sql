-- name: revenue_by_category
SELECT p.category, ROUND(SUM(oi.quantity * p.price), 2) AS revenue
FROM order_items oi JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category ORDER BY revenue DESC;

-- name: monthly_revenue_running_total
WITH monthly AS (
  SELECT substr(o.order_date, 1, 7) AS month, SUM(oi.quantity * p.price) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id GROUP BY month)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS running_total
FROM monthly ORDER BY month;

-- name: top_customers_per_region
SELECT * FROM (
  SELECT c.region, c.name, ROUND(SUM(oi.quantity * p.price), 2) AS spend,
         RANK() OVER (PARTITION BY c.region ORDER BY SUM(oi.quantity * p.price) DESC) AS rnk
  FROM customers c JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY c.region, c.customer_id)
WHERE rnk <= 3 ORDER BY region, rnk;

-- name: repeat_customer_rate
SELECT ROUND(100.0 * SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM (SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id);
