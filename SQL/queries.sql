-- ============================================================
--  SALES PERFORMANCE ANALYSIS — SQL QUERIES
--  Author : Ayushi Shukla
--  DB     : MySQL / SQLite compatible
-- ============================================================

-- ── TABLE SCHEMA ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sales (
    order_id         INT PRIMARY KEY,
    date             DATE,
    sales_rep        VARCHAR(100),
    region           VARCHAR(50),
    product_category VARCHAR(50),
    product_name     VARCHAR(150),
    quantity         INT,
    unit_price       DECIMAL(10,2),
    discount_pct     DECIMAL(5,2),
    revenue          DECIMAL(12,2),
    cost             DECIMAL(12,2),
    profit           DECIMAL(12,2),
    customer_segment VARCHAR(50)
);

-- ── SECTION 1: OVERVIEW KPIs ────────────────────────────────

-- Q1: Overall KPIs
SELECT
    ROUND(SUM(revenue), 2)                  AS total_revenue,
    ROUND(SUM(profit),  2)                  AS total_profit,
    ROUND(SUM(profit) / SUM(revenue) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(revenue), 2)                  AS avg_order_value,
    SUM(quantity)                           AS total_units_sold,
    ROUND(AVG(discount_pct), 2)             AS avg_discount_pct,
    COUNT(*)                                AS total_orders
FROM sales;

-- Q2: Monthly Revenue & Order Volume
SELECT
    DATE_FORMAT(date, '%Y-%m')    AS month,   -- MySQL; use strftime('%Y-%m', date) for SQLite
    ROUND(SUM(revenue), 2)        AS monthly_revenue,
    ROUND(SUM(profit), 2)         AS monthly_profit,
    COUNT(*)                      AS orders,
    ROUND(AVG(revenue), 2)        AS avg_order_value
FROM sales
GROUP BY month
ORDER BY month;

-- Q3: Quarter-over-Quarter growth
SELECT
    quarter,
    ROUND(SUM(revenue), 2) AS quarterly_revenue,
    ROUND(SUM(profit),  2) AS quarterly_profit,
    COUNT(*)               AS orders
FROM (
    SELECT *,
        CONCAT('Q', QUARTER(date), ' ', YEAR(date)) AS quarter  -- MySQL
        -- strftime('%Y', date)||'-Q'||(CAST(strftime('%m', date) AS INT)+2)/3 for SQLite
    FROM sales
) t
GROUP BY quarter
ORDER BY MIN(date);

-- ── SECTION 2: REGIONAL ANALYSIS ───────────────────────────

-- Q4: Revenue & Profit by Region
SELECT
    region,
    ROUND(SUM(revenue), 2)                  AS total_revenue,
    ROUND(SUM(profit), 2)                   AS total_profit,
    ROUND(SUM(profit)/SUM(revenue)*100, 1)  AS profit_margin_pct,
    COUNT(*)                                AS num_orders,
    ROUND(AVG(revenue), 2)                  AS avg_order_value
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- Q5: Region × Category cross-analysis
SELECT
    region,
    product_category,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(*)               AS orders
FROM sales
GROUP BY region, product_category
ORDER BY region, revenue DESC;

-- ── SECTION 3: SALES REP PERFORMANCE ────────────────────────

-- Q6: Top reps ranked by profit
SELECT
    sales_rep,
    region,
    ROUND(SUM(profit),   2) AS total_profit,
    ROUND(SUM(revenue),  2) AS total_revenue,
    COUNT(*)                AS orders,
    ROUND(AVG(discount_pct), 1) AS avg_discount,
    ROUND(SUM(profit)/SUM(revenue)*100, 1) AS margin_pct
FROM sales
GROUP BY sales_rep, region
ORDER BY total_profit DESC;

-- Q7: Monthly performance per rep (pivot-style)
SELECT
    sales_rep,
    ROUND(SUM(CASE WHEN MONTH(date)=1  THEN revenue ELSE 0 END), 2) AS Jan,
    ROUND(SUM(CASE WHEN MONTH(date)=2  THEN revenue ELSE 0 END), 2) AS Feb,
    ROUND(SUM(CASE WHEN MONTH(date)=3  THEN revenue ELSE 0 END), 2) AS Mar,
    ROUND(SUM(CASE WHEN MONTH(date)=4  THEN revenue ELSE 0 END), 2) AS Apr,
    ROUND(SUM(CASE WHEN MONTH(date)=5  THEN revenue ELSE 0 END), 2) AS May,
    ROUND(SUM(CASE WHEN MONTH(date)=6  THEN revenue ELSE 0 END), 2) AS Jun,
    ROUND(SUM(revenue), 2)                                           AS total
FROM sales
GROUP BY sales_rep
ORDER BY total DESC;

-- ── SECTION 4: PRODUCT & CATEGORY ANALYSIS ──────────────────

-- Q8: Category revenue, profit, margin
SELECT
    product_category,
    ROUND(SUM(revenue), 2)                   AS total_revenue,
    ROUND(SUM(profit),  2)                   AS total_profit,
    ROUND(SUM(profit)/SUM(revenue)*100, 1)   AS margin_pct,
    SUM(quantity)                            AS units_sold,
    ROUND(AVG(discount_pct), 1)              AS avg_discount
FROM sales
GROUP BY product_category
ORDER BY total_revenue DESC;

-- Q9: Top 10 best-selling products by revenue
SELECT
    product_name,
    product_category,
    SUM(quantity)          AS total_units,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit),  2) AS total_profit
FROM sales
GROUP BY product_name, product_category
ORDER BY total_revenue DESC
LIMIT 10;

-- Q10: Products with negative or zero margin (quality check)
SELECT order_id, product_name, revenue, cost, profit
FROM sales
WHERE profit <= 0
ORDER BY profit ASC;

-- ── SECTION 5: DISCOUNT IMPACT ANALYSIS ─────────────────────

-- Q11: Profit margin by discount band
SELECT
    CASE
        WHEN discount_pct = 0          THEN '0% (No Discount)'
        WHEN discount_pct BETWEEN 1 AND 5  THEN '1–5%'
        WHEN discount_pct BETWEEN 6 AND 10 THEN '6–10%'
        WHEN discount_pct > 10         THEN '>10%'
    END AS discount_band,
    COUNT(*)                                AS orders,
    ROUND(AVG(revenue), 2)                  AS avg_revenue,
    ROUND(SUM(profit)/SUM(revenue)*100, 1)  AS margin_pct
FROM sales
GROUP BY discount_band
ORDER BY MIN(discount_pct);

-- ── SECTION 6: CUSTOMER SEGMENT ANALYSIS ────────────────────

-- Q12: Segment breakdown
SELECT
    customer_segment,
    COUNT(*)               AS orders,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_order_value,
    ROUND(SUM(profit)/SUM(revenue)*100, 1) AS margin_pct
FROM sales
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- ── SECTION 7: OUTLIER DETECTION ────────────────────────────

-- Q13: Flag revenue outliers using a simple percentile approach
SELECT
    order_id,
    date,
    sales_rep,
    product_name,
    revenue,
    CASE
        WHEN revenue > (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) FROM sales) +
                  1.5 * ((SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) FROM sales) -
                         (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) FROM sales))
             THEN 'High Outlier'
        WHEN revenue < (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) FROM sales) -
                  1.5 * ((SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) FROM sales) -
                         (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) FROM sales))
             THEN 'Low Outlier'
        ELSE 'Normal'
    END AS outlier_flag
FROM sales
ORDER BY revenue DESC;
