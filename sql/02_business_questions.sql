-- =====================================================================
-- Lakeshore Provisions Co. | 02: Business questions
-- Fiscal year runs Oct 1 - Sep 30.  FY25 = Oct 2024-Sep 2025, FY26 = Oct 2025-Sep 2026.
-- Run 01_build_and_clean.sql first.
-- =====================================================================

-- Q1. Headline KPIs by fiscal year: revenue, gross margin, orders, avg order value
SELECT CASE WHEN order_date < '2025-10-01' THEN 'FY25' ELSE 'FY26' END AS fiscal_year,
       ROUND(SUM(net_revenue))                                         AS revenue,
       ROUND(100.0 * (SUM(net_revenue) - SUM(cogs)) / SUM(net_revenue), 1) AS gross_margin_pct,
       COUNT(DISTINCT order_id)                                        AS orders,
       ROUND(SUM(net_revenue) / COUNT(DISTINCT order_id), 2)           AS avg_order_value,
       COUNT(DISTINCT customer_id)                                     AS active_customers
FROM sales
GROUP BY 1;

-- Q2. Monthly revenue trend with month-over-month growth
WITH m AS (
    SELECT SUBSTR(order_date,1,7) AS month, SUM(net_revenue) AS revenue
    FROM sales GROUP BY 1
)
SELECT month,
       ROUND(revenue) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM m ORDER BY month;

-- Q3. Revenue by region, FY25 vs FY26, with YoY growth  (-> NW Indiana is the problem)
SELECT r.region_name,
       ROUND(SUM(CASE WHEN s.order_date <  '2025-10-01' THEN s.net_revenue END)) AS fy25,
       ROUND(SUM(CASE WHEN s.order_date >= '2025-10-01' THEN s.net_revenue END)) AS fy26,
       ROUND(100.0 * (SUM(CASE WHEN s.order_date >= '2025-10-01' THEN s.net_revenue END)
                    / SUM(CASE WHEN s.order_date <  '2025-10-01' THEN s.net_revenue END) - 1), 1) AS yoy_pct
FROM sales s
JOIN customers c   ON c.customer_id = s.customer_id
JOIN raw_regions r ON r.region_id  = c.region_id
GROUP BY r.region_name
ORDER BY yoy_pct;

-- Q4. Which customers drove the NW Indiana decline? (biggest FY26 vs FY25 drops)
SELECT c.customer_name, c.segment,
       ROUND(SUM(CASE WHEN s.order_date <  '2025-10-01' THEN s.net_revenue ELSE 0 END)) AS fy25,
       ROUND(SUM(CASE WHEN s.order_date >= '2025-10-01' THEN s.net_revenue ELSE 0 END)) AS fy26,
       MAX(s.order_date) AS last_order_date
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
WHERE c.region_id = 'R2'
GROUP BY c.customer_id
ORDER BY (fy26 - fy25)
LIMIT 10;

-- Q5. Churn-risk list: customers with FY25 revenue > $10K and no order in the last 90 days
SELECT c.customer_name, c.segment, c.region_id,
       ROUND(SUM(s.net_revenue)) AS lifetime_revenue,
       MAX(s.order_date)         AS last_order_date,
       CAST(JULIANDAY('2026-09-30') - JULIANDAY(MAX(s.order_date)) AS INT) AS days_since_order
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
GROUP BY c.customer_id
HAVING SUM(CASE WHEN s.order_date < '2025-10-01' THEN s.net_revenue ELSE 0 END) > 10000
   AND days_since_order > 90
ORDER BY lifetime_revenue DESC;

-- Q6. Sales rep quota attainment, FY26  (-> one rep far below plan)
WITH actual AS (
    SELECT rep_id, SUBSTR(order_date,1,7) || '-01' AS month_start, SUM(net_revenue) AS revenue
    FROM sales GROUP BY 1,2
)
SELECT sr.rep_name, rg.region_name,
       ROUND(SUM(a.revenue))                                    AS fy26_revenue,
       SUM(t.revenue_target)                                    AS fy26_target,
       ROUND(100.0 * SUM(a.revenue) / SUM(t.revenue_target), 1) AS attainment_pct,
       SUM(a.revenue >= t.revenue_target)                       AS months_hit_target
FROM raw_targets t
LEFT JOIN actual a        ON a.rep_id = t.rep_id AND a.month_start = t.month_start
JOIN raw_sales_reps sr    ON sr.rep_id = t.rep_id
JOIN raw_regions rg       ON rg.region_id = sr.region_id
WHERE t.month_start >= '2025-10-01'
GROUP BY sr.rep_id
ORDER BY attainment_pct;

-- Q7. Return rate by product (-> one seafood SKU is a quality problem)
SELECT p.product_name, p.category, p.supplier,
       COUNT(*)                                                   AS lines,
       SUM(o.status = 'Returned')                                 AS returned_lines,
       ROUND(100.0 * SUM(o.status = 'Returned') / COUNT(*), 1)   AS return_rate_pct,
       ROUND(SUM(CASE WHEN o.status = 'Returned' THEN o.net_revenue END)) AS revenue_lost
FROM order_lines o
JOIN raw_products p ON p.product_id = o.product_id
GROUP BY p.product_id
HAVING lines >= 100
ORDER BY return_rate_pct DESC
LIMIT 10;

-- Q8. When did the return problem start? Monthly return rate for the worst SKU
SELECT SUBSTR(o.order_date,1,7) AS month,
       ROUND(100.0 * SUM(o.status = 'Returned') / COUNT(*), 1) AS return_rate_pct
FROM order_lines o
JOIN raw_products p ON p.product_id = o.product_id
WHERE p.product_name LIKE 'Atlantic Salmon%'
GROUP BY 1 ORDER BY 1;

-- Q9. Dairy price increase (Jan 2026): price vs volume, quarterly
SELECT SUBSTR(s.order_date,1,4) || '-Q' || ((CAST(SUBSTR(s.order_date,6,2) AS INT)+2)/3) AS quarter,
       SUM(s.quantity)                               AS units,
       ROUND(SUM(s.net_revenue))                     AS revenue,
       ROUND(SUM(s.net_revenue) / SUM(s.quantity),2) AS avg_net_price
FROM sales s
JOIN raw_products p ON p.product_id = s.product_id
WHERE p.category = 'Dairy'
GROUP BY 1 ORDER BY 1;

-- Q10. Category mix and margin
SELECT p.category,
       ROUND(SUM(s.net_revenue))                                         AS revenue,
       ROUND(100.0 * SUM(s.net_revenue) / (SELECT SUM(net_revenue) FROM sales), 1) AS pct_of_revenue,
       ROUND(100.0 * (SUM(s.net_revenue) - SUM(s.cogs)) / SUM(s.net_revenue), 1)   AS gross_margin_pct
FROM sales s JOIN raw_products p ON p.product_id = s.product_id
GROUP BY p.category ORDER BY revenue DESC;

-- Q11. Customer concentration: share of revenue from top 10% of customers (Pareto)
WITH cr AS (
    SELECT customer_id, SUM(net_revenue) AS rev,
           NTILE(10) OVER (ORDER BY SUM(net_revenue) DESC) AS decile
    FROM sales GROUP BY customer_id
)
SELECT decile, COUNT(*) AS customers, ROUND(SUM(rev)) AS revenue,
       ROUND(100.0 * SUM(rev) / (SELECT SUM(rev) FROM cr), 1) AS pct_of_revenue
FROM cr GROUP BY decile ORDER BY decile;

-- Q12. Fulfillment: average days from order to ship, by region
SELECT r.region_name,
       ROUND(AVG(JULIANDAY(o.ship_date) - JULIANDAY(o.order_date)), 2) AS avg_days_to_ship,
       ROUND(100.0 * SUM(JULIANDAY(o.ship_date) - JULIANDAY(o.order_date) > 3) / COUNT(*), 1) AS pct_late_over_3_days
FROM order_lines o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN raw_regions r ON r.region_id = c.region_id
WHERE o.ship_date IS NOT NULL AND o.ship_date <> ''
GROUP BY r.region_name;

-- Q13. Top 3 products per region (window function)
WITH pr AS (
    SELECT c.region_id, p.product_name, SUM(s.net_revenue) AS rev,
           RANK() OVER (PARTITION BY c.region_id ORDER BY SUM(s.net_revenue) DESC) AS rnk
    FROM sales s
    JOIN customers c    ON c.customer_id = s.customer_id
    JOIN raw_products p ON p.product_id  = s.product_id
    GROUP BY c.region_id, p.product_name
)
SELECT region_id, rnk, product_name, ROUND(rev) AS revenue
FROM pr WHERE rnk <= 3 ORDER BY region_id, rnk;
