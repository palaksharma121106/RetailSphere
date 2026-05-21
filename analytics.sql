-- ═══════════════════════════════════════════════════════
--  RetailSphere — Analytics Queries
--  These are the "impressive" queries you show/explain
-- ═══════════════════════════════════════════════════════
USE retailsphere;

-- ── 1. RFM Customer Segmentation ────────────────────────
-- Recency = how recently did they order
-- Frequency = how many orders
-- Monetary = how much total money spent
-- This classifies customers into Gold / Silver / Bronze

SELECT
    customer_id,
    DATEDIFF(NOW(), MAX(order_date))   AS recency_days,
    COUNT(order_id)                    AS frequency,
    ROUND(SUM(total_amount), 2)        AS monetary,
    CASE
        WHEN SUM(total_amount) > 500000 THEN 'Gold'
        WHEN SUM(total_amount) > 100000 THEN 'Silver'
        ELSE 'Bronze'
    END AS customer_tier
FROM orders
WHERE status = 'delivered'
GROUP BY customer_id
ORDER BY monetary DESC
LIMIT 20;

-- ── 2. Monthly Revenue Trend ────────────────────────────
-- Shows revenue per month across all years
-- Uses DATE_FORMAT to group by month

SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(order_id)                  AS total_orders,
    ROUND(SUM(total_amount), 2)      AS revenue,
    ROUND(AVG(total_amount), 2)      AS avg_order_value
FROM orders
WHERE status = 'delivered'
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- ── 3. Top Selling Products ─────────────────────────────
SELECT
    p.name                       AS product,
    c.name                       AS category,
    SUM(oi.quantity)             AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
FROM order_items oi
JOIN products p  ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY p.product_id
ORDER BY total_revenue DESC
LIMIT 10;

-- ── 4. Low Inventory Alert ──────────────────────────────
-- Finds products below reorder level — triggers restocking
-- This is exactly how Walmart's supply chain works

SELECT
    p.name        AS product,
    w.city        AS warehouse,
    i.quantity    AS current_stock,
    i.reorder_level,
    (i.reorder_level - i.quantity) AS units_needed
FROM inventory i
JOIN products   p ON i.product_id   = p.product_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.quantity < i.reorder_level
ORDER BY units_needed DESC
LIMIT 15;

-- ── 5. Supplier Performance ─────────────────────────────
-- Which supplier's products sell best?

SELECT
    s.name                      AS supplier,
    s.country,
    COUNT(DISTINCT p.product_id) AS products_supplied,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue_generated
FROM suppliers s
JOIN products    p  ON s.supplier_id = p.supplier_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders      o  ON oi.order_id   = o.order_id
WHERE o.status = 'delivered'
GROUP BY s.supplier_id
ORDER BY total_revenue_generated DESC;

-- ── 6. Window Function — Running Revenue Total ──────────
-- Shows cumulative revenue month by month
-- Window functions = advanced SQL — impressive to show

SELECT
    DATE_FORMAT(order_date, '%Y-%m')                       AS month,
    ROUND(SUM(total_amount), 2)                            AS monthly_revenue,
    ROUND(SUM(SUM(total_amount)) OVER (
          ORDER BY DATE_FORMAT(order_date, '%Y-%m')), 2)   AS running_total
FROM orders
WHERE status = 'delivered'
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- ── 7. State-wise Sales Performance ─────────────────────
SELECT
    c.state,
    COUNT(DISTINCT c.customer_id)  AS customers,
    COUNT(o.order_id)              AS orders,
    ROUND(SUM(o.total_amount), 2)  AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.state
ORDER BY revenue DESC;