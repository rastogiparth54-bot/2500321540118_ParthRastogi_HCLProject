-- =============================================================================
-- Project 1: Sales Performance Dashboard (Retail & E-Commerce)
-- Script 03: Production Oracle SQL Analytical Queries & Window Functions
-- Focus: Joins, Complex Aggregations, GROUP BY ROLLUP, and Window Functions
-- =============================================================================

-- =============================================================================
-- QUERY 1: EXECUTIVE 5 CORE KPIS (SCORECARD METRICS)
-- Reconciles against CSV benchmark & Power BI KPI Cards
-- =============================================================================
SELECT 
    COUNT(f.SALES_KEY)                         AS TOTAL_ORDERS,
    SUM(f.QUANTITY)                            AS TOTAL_UNITS_SOLD,
    ROUND(SUM(f.GROSS_SALES), 2)               AS TOTAL_GROSS_SALES_USD,
    ROUND(SUM(f.DISCOUNT_AMOUNT), 2)           AS TOTAL_DISCOUNT_GIVEN_USD,
    ROUND(SUM(f.NET_SALES), 2)                 AS TOTAL_NET_SALES_USD,
    ROUND(SUM(f.GROSS_PROFIT), 2)              AS TOTAL_GROSS_PROFIT_USD,
    ROUND((SUM(f.GROSS_PROFIT) / SUM(f.NET_SALES)) * 100, 2) AS OVERALL_PROFIT_MARGIN_PCT,
    ROUND(AVG(f.NET_SALES), 2)                 AS AVERAGE_ORDER_VALUE_USD,
    ROUND(SUM(f.DISCOUNT_AMOUNT) / SUM(f.GROSS_SALES) * 100, 2) AS EFFECTIVE_DISCOUNT_PCT
FROM FACT_SALES f;

-- =============================================================================
-- QUERY 2: TOP 10 PRODUCTS BY NET REVENUE (WINDOW FUNCTION: DENSE_RANK)
-- Acceptance Criteria: Top 10 products verified
-- =============================================================================
WITH ProductPerformance AS (
    SELECT 
        p.PRODUCT_KEY,
        p.PRODUCT_ID,
        p.PRODUCT_NAME,
        p.PRODUCT_CATEGORY,
        COUNT(f.SALES_KEY)                 AS ORDER_COUNT,
        SUM(f.QUANTITY)                    AS UNITS_SOLD,
        ROUND(SUM(f.NET_SALES), 2)         AS TOTAL_NET_REVENUE,
        ROUND(SUM(f.GROSS_PROFIT), 2)      AS TOTAL_PROFIT,
        ROUND((SUM(f.GROSS_PROFIT) / SUM(f.NET_SALES)) * 100, 2) AS MARGIN_PCT,
        DENSE_RANK() OVER (ORDER BY SUM(f.NET_SALES) DESC) AS REVENUE_RANK,
        DENSE_RANK() OVER (PARTITION BY p.PRODUCT_CATEGORY ORDER BY SUM(f.NET_SALES) DESC) AS CATEGORY_RANK
    FROM FACT_SALES f
    JOIN DIM_PRODUCT p ON f.PRODUCT_KEY = p.PRODUCT_KEY
    GROUP BY p.PRODUCT_KEY, p.PRODUCT_ID, p.PRODUCT_NAME, p.PRODUCT_CATEGORY
)
SELECT 
    REVENUE_RANK,
    CATEGORY_RANK,
    PRODUCT_ID,
    PRODUCT_NAME,
    PRODUCT_CATEGORY,
    ORDER_COUNT,
    UNITS_SOLD,
    TOTAL_NET_REVENUE,
    TOTAL_PROFIT,
    MARGIN_PCT
FROM ProductPerformance
WHERE REVENUE_RANK <= 10
ORDER BY REVENUE_RANK ASC;

-- =============================================================================
-- QUERY 3: MONTHLY TIME-SERIES TREND WITH ADVANCED WINDOW FUNCTIONS
-- Demonstrates: LAG (MoM Growth), Running Total SUM() OVER(), and 3-Month Moving Average
-- =============================================================================
WITH MonthlyAggregates AS (
    SELECT 
        d.YEAR,
        d.MONTH_NUM,
        d.YEAR_QUARTER,
        d.MONTH_YEAR,
        COUNT(f.SALES_KEY)                 AS MONTHLY_ORDERS,
        SUM(f.QUANTITY)                    AS MONTHLY_UNITS,
        ROUND(SUM(f.NET_SALES), 2)         AS MONTHLY_NET_SALES,
        ROUND(SUM(f.GROSS_PROFIT), 2)      AS MONTHLY_PROFIT
    FROM FACT_SALES f
    JOIN DIM_DATE d ON f.DATE_KEY = d.DATE_KEY
    GROUP BY d.YEAR, d.MONTH_NUM, d.YEAR_QUARTER, d.MONTH_YEAR
)
SELECT 
    YEAR,
    MONTH_NUM,
    MONTH_YEAR,
    YEAR_QUARTER,
    MONTHLY_ORDERS,
    MONTHLY_UNITS,
    MONTHLY_NET_SALES,
    -- Running Cumulative Total YTD within each calendar year
    ROUND(SUM(MONTHLY_NET_SALES) OVER (
        PARTITION BY YEAR 
        ORDER BY MONTH_NUM 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS YTD_RUNNING_TOTAL,
    -- Prior Month Net Sales via LAG
    LAG(MONTHLY_NET_SALES, 1) OVER (ORDER BY YEAR, MONTH_NUM) AS PRIOR_MONTH_SALES,
    -- Month-over-Month Growth in USD
    ROUND(MONTHLY_NET_SALES - LAG(MONTHLY_NET_SALES, 1) OVER (ORDER BY YEAR, MONTH_NUM), 2) AS MOM_GROWTH_USD,
    -- Month-over-Month Growth Percentage
    ROUND((
        (MONTHLY_NET_SALES - LAG(MONTHLY_NET_SALES, 1) OVER (ORDER BY YEAR, MONTH_NUM)) / 
        NULLIF(LAG(MONTHLY_NET_SALES, 1) OVER (ORDER BY YEAR, MONTH_NUM), 0)
    ) * 100, 2) AS MOM_GROWTH_PCT,
    -- 3-Month Moving Average of Monthly Revenue
    ROUND(AVG(MONTHLY_NET_SALES) OVER (
        ORDER BY YEAR, MONTH_NUM 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS THREE_MONTH_MOVING_AVG
FROM MonthlyAggregates
ORDER BY YEAR ASC, MONTH_NUM ASC;

-- =============================================================================
-- QUERY 4: REGIONAL SLICER & GEOGRAPHIC DRILL-DOWN (GROUP BY ROLLUP)
-- Hierarchical aggregation: Region -> State -> City -> Store
-- =============================================================================
SELECT 
    NVL(r.REGION, '--- ALL REGIONS (GRAND TOTAL) ---') AS REGION,
    NVL(r.STATE, '--- ALL STATES ---')                 AS STATE,
    NVL(r.CITY, '--- ALL CITIES ---')                   AS CITY,
    NVL(r.STORE_ID, '--- ALL STORES ---')               AS STORE_ID,
    COUNT(f.SALES_KEY)                                  AS TOTAL_TRANSACTIONS,
    SUM(f.QUANTITY)                                     AS UNITS_SOLD,
    ROUND(SUM(f.NET_SALES), 2)                          AS TOTAL_NET_SALES,
    ROUND(AVG(f.NET_SALES), 2)                          AS AVERAGE_TICKET_SIZE,
    ROUND((SUM(f.NET_SALES) / SUM(SUM(f.NET_SALES)) OVER ()) * 100, 2) AS PCT_OF_TOTAL_COMPANY_SALES
FROM FACT_SALES f
JOIN DIM_REGION r ON f.REGION_KEY = r.REGION_KEY
GROUP BY ROLLUP (r.REGION, r.STATE, r.CITY, r.STORE_ID)
ORDER BY 
    GROUPING(r.REGION) ASC,
    GROUPING(r.STATE) ASC,
    TOTAL_NET_SALES DESC;

-- =============================================================================
-- QUERY 5: PRODUCT CATEGORY CONTRIBUTION & MARGIN QUINTILES
-- Slicer 3: Product Category evaluation
-- =============================================================================
SELECT 
    p.PRODUCT_CATEGORY,
    COUNT(f.SALES_KEY)                         AS TRANSACTIONS,
    SUM(f.QUANTITY)                            AS TOTAL_QUANTITY,
    ROUND(SUM(f.NET_SALES), 2)                 AS CATEGORY_NET_SALES,
    ROUND(SUM(f.TOTAL_COST), 2)                AS CATEGORY_COGS,
    ROUND(SUM(f.GROSS_PROFIT), 2)              AS CATEGORY_GROSS_PROFIT,
    ROUND((SUM(f.GROSS_PROFIT) / SUM(f.NET_SALES)) * 100, 2) AS MARGIN_PERCENTAGE,
    ROUND((SUM(f.NET_SALES) / SUM(SUM(f.NET_SALES)) OVER ()) * 100, 2) AS SALES_SHARE_PCT
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.PRODUCT_KEY = p.PRODUCT_KEY
GROUP BY p.PRODUCT_CATEGORY
ORDER BY CATEGORY_NET_SALES DESC;

-- =============================================================================
-- QUERY 6: CUSTOMER SPENDING TIER ANALYSIS (WINDOW FUNCTION: NTILE)
-- Segments customer spend into 4 Quartiles (Top 25% VIP, Core, Mid, Low)
-- =============================================================================
WITH CustomerSpend AS (
    SELECT 
        c.CUSTOMER_KEY,
        c.CUSTOMER_ID,
        c.GENDER,
        c.AGE_GROUP,
        COUNT(f.SALES_KEY)             AS TOTAL_PURCHASES,
        ROUND(SUM(f.NET_SALES), 2)     AS TOTAL_SPENT,
        ROUND(AVG(f.NET_SALES), 2)     AS AVG_SPENT_PER_ORDER
    FROM FACT_SALES f
    JOIN DIM_CUSTOMER c ON f.CUSTOMER_KEY = c.CUSTOMER_KEY
    GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_ID, c.GENDER, c.AGE_GROUP
),
CustomerQuartiles AS (
    SELECT 
        cs.*,
        NTILE(4) OVER (ORDER BY TOTAL_SPENT DESC) AS SPENDING_QUARTILE
    FROM CustomerSpend cs
)
SELECT 
    CASE SPENDING_QUARTILE
        WHEN 1 THEN 'Quartile 1: Platinum VIP (Top 25%)'
        WHEN 2 THEN 'Quartile 2: Gold High-Tier'
        WHEN 3 THEN 'Quartile 3: Silver Mid-Tier'
        WHEN 4 THEN 'Quartile 4: Bronze Entry-Tier'
    END AS CUSTOMER_SEGMENT,
    COUNT(*)                           AS CUSTOMER_COUNT,
    ROUND(SUM(TOTAL_SPENT), 2)         AS SEGMENT_TOTAL_REVENUE,
    ROUND(AVG(TOTAL_SPENT), 2)         AS AVG_CUSTOMER_LIFETIME_VALUE,
    ROUND(AVG(TOTAL_PURCHASES), 1)     AS AVG_ORDERS_PER_CUSTOMER
FROM CustomerQuartiles
GROUP BY SPENDING_QUARTILE
ORDER BY SPENDING_QUARTILE ASC;

-- =============================================================================
-- QUERY 7: WEEKDAY VS WEEKEND SALES VELOCITY
-- =============================================================================
SELECT 
    d.DAY_NAME,
    d.DAY_OF_WEEK,
    d.IS_WEEKEND,
    COUNT(f.SALES_KEY)                 AS TOTAL_ORDERS,
    SUM(f.QUANTITY)                    AS UNITS_SOLD,
    ROUND(SUM(f.NET_SALES), 2)         AS TOTAL_REVENUE,
    ROUND(AVG(f.NET_SALES), 2)         AS AVG_BASKET_VALUE
FROM FACT_SALES f
JOIN DIM_DATE d ON f.DATE_KEY = d.DATE_KEY
GROUP BY d.DAY_NAME, d.DAY_OF_WEEK, d.IS_WEEKEND
ORDER BY d.DAY_OF_WEEK ASC;
