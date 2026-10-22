-- =====================================================================
-- Lakeshore Provisions Co. | 01: Build clean analytics views
-- Raw CSVs are loaded as raw_* tables (see load_sqlite.py).
-- These views fix the data-quality issues found during profiling.
-- =====================================================================

-- ---------- Data-quality profiling (run these first, note the counts) ----------

-- Exact duplicate order lines
SELECT COUNT(*) - COUNT(DISTINCT order_id || '-' || line_number) AS duplicate_lines
FROM raw_order_lines;

-- Inconsistent status values (casing / whitespace)
SELECT status, COUNT(*) AS n FROM raw_order_lines GROUP BY status ORDER BY n DESC;

-- Lines with no sales rep, and lines with zero quantity
SELECT SUM(rep_id IS NULL OR rep_id = '') AS missing_rep,
       SUM(quantity <= 0)                 AS zero_qty
FROM raw_order_lines;

-- Segment name variants
SELECT segment, COUNT(*) FROM raw_customers GROUP BY segment ORDER BY 1;

-- ---------- Clean views ----------

DROP VIEW IF EXISTS customers;
CREATE VIEW customers AS
SELECT customer_id,
       TRIM(customer_name)                                   AS customer_name,
       CASE TRIM(segment)
            WHEN 'Indep. Restaurant' THEN 'Independent Restaurant'
            WHEN 'Rest. Group'       THEN 'Restaurant Group'
            ELSE TRIM(segment) END                           AS segment,
       region_id,
       -- Title-case the city (handles the ALL-CAPS rows)
       UPPER(SUBSTR(TRIM(city),1,1)) || LOWER(SUBSTR(TRIM(city),2)) AS city,
       customer_since,
       rep_id                                                AS account_owner_rep_id
FROM raw_customers;

DROP VIEW IF EXISTS order_lines;
CREATE VIEW order_lines AS
WITH dedup AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id, line_number ORDER BY order_id) AS rn
    FROM raw_order_lines
)
SELECT d.order_id,
       d.line_number,
       d.order_date,
       d.ship_date,
       d.customer_id,
       d.product_id,
       -- Missing rep -> fall back to the customer's account owner
       COALESCE(NULLIF(d.rep_id,''), c.account_owner_rep_id)            AS rep_id,
       d.quantity,
       d.unit_price,
       d.discount_pct,
       UPPER(SUBSTR(TRIM(d.status),1,1)) || LOWER(SUBSTR(TRIM(d.status),2)) AS status,
       ROUND(d.quantity * d.unit_price * (1 - d.discount_pct), 2)         AS net_revenue,
       ROUND(d.quantity * p.unit_cost, 2)                                 AS cogs
FROM dedup d
JOIN customers c ON c.customer_id = d.customer_id
JOIN raw_products p ON p.product_id = d.product_id
WHERE d.rn = 1
  AND d.quantity > 0;          -- drop data-entry errors

-- Revenue-recognized lines only (excludes Cancelled and Returned)
DROP VIEW IF EXISTS sales;
CREATE VIEW sales AS
SELECT * FROM order_lines WHERE status NOT IN ('Cancelled','Returned');
