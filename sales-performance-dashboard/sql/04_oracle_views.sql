-- =============================================================================
-- Project 1: Sales Performance Dashboard (Retail & E-Commerce)
-- Script 04: Production Oracle Analytical Views for BI & Power BI Integration
-- Database Engine: Oracle Database 19c / 21c / 23c Autonomous Database
-- =============================================================================

-- -----------------------------------------------------------------------------
-- VIEW 1: V_BI_SALES_FACT_CONFORMED
-- Flattened conformed view optimized for DirectQuery / Power BI Import
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_BI_SALES_FACT_CONFORMED AS
SELECT 
    f.SALES_KEY,
    f.TRANSACTION_ID,
    -- Date Attributes
    f.DATE_KEY,
    d.FULL_DATE,
    d.YEAR,
    d.QUARTER,
    d.YEAR_QUARTER,
    d.MONTH_NUM,
    d.MONTH_NAME,
    d.MONTH_YEAR,
    d.DAY_NAME,
    d.IS_WEEKEND,
    -- Product Attributes
    p.PRODUCT_KEY,
    p.PRODUCT_ID,
    p.PRODUCT_NAME,
    p.PRODUCT_CATEGORY,
    -- Customer Attributes
    c.CUSTOMER_KEY,
    c.CUSTOMER_ID,
    c.GENDER,
    c.AGE,
    c.AGE_GROUP,
    -- Region & Store Attributes
    r.REGION_KEY,
    r.STORE_ID,
    r.CITY,
    r.STATE,
    r.REGION,
    -- Sales & Financial Metrics
    f.QUANTITY,
    f.PRICE_PER_UNIT,
    f.DISCOUNT_PCT,
    f.GROSS_SALES,
    f.DISCOUNT_AMOUNT,
    f.NET_SALES,
    f.TOTAL_COST,
    f.GROSS_PROFIT,
    f.PROFIT_MARGIN_PCT,
    f.PAYMENT_METHOD
FROM FACT_SALES f
JOIN DIM_DATE d ON f.DATE_KEY = d.DATE_KEY
JOIN DIM_PRODUCT p ON f.PRODUCT_KEY = p.PRODUCT_KEY
JOIN DIM_CUSTOMER c ON f.CUSTOMER_KEY = c.CUSTOMER_KEY
JOIN DIM_REGION r ON f.REGION_KEY = r.REGION_KEY;

COMMENT ON VIEW V_BI_SALES_FACT_CONFORMED IS 'Conformed analytical view combining Fact_Sales with all 4 dimensions for Power BI DirectQuery.';

-- -----------------------------------------------------------------------------
-- VIEW 2: V_BI_MONTHLY_SALES_TREND
-- Monthly aggregated summary with MoM growth and running totals
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_BI_MONTHLY_SALES_TREND AS
WITH MonthlyBase AS (
    SELECT 
        d.YEAR,
        d.MONTH_NUM,
        d.MONTH_YEAR,
        d.YEAR_QUARTER,
        COUNT(f.SALES_KEY)                 AS ORDER_COUNT,
        SUM(f.QUANTITY)                    AS UNITS_SOLD,
        ROUND(SUM(f.GROSS_SALES), 2)       AS GROSS_SALES,
        ROUND(SUM(f.DISCOUNT_AMOUNT), 2)   AS DISCOUNT_AMOUNT,
        ROUND(SUM(f.NET_SALES), 2)         AS NET_SALES,
        ROUND(SUM(f.TOTAL_COST), 2)        AS TOTAL_COST,
        ROUND(SUM(f.GROSS_PROFIT), 2)      AS GROSS_PROFIT,
        ROUND(AVG(f.NET_SALES), 2)         AS AVG_ORDER_VALUE
    FROM FACT_SALES f
    JOIN DIM_DATE d ON f.DATE_KEY = d.DATE_KEY
    GROUP BY d.YEAR, d.MONTH_NUM, d.MONTH_YEAR, d.YEAR_QUARTER
)
SELECT 
    m.YEAR,
    m.MONTH_NUM,
    m.MONTH_YEAR,
    m.YEAR_QUARTER,
    m.ORDER_COUNT,
    m.UNITS_SOLD,
    m.GROSS_SALES,
    m.DISCOUNT_AMOUNT,
    m.NET_SALES,
    m.TOTAL_COST,
    m.GROSS_PROFIT,
    ROUND((m.GROSS_PROFIT / m.NET_SALES) * 100, 2) AS MARGIN_PCT,
    m.AVG_ORDER_VALUE,
    -- Running Total YTD
    ROUND(SUM(m.NET_SALES) OVER (
        PARTITION BY m.YEAR 
        ORDER BY m.MONTH_NUM 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS YTD_SALES,
    -- Prior Month Net Sales
    LAG(m.NET_SALES, 1) OVER (ORDER BY m.YEAR, m.MONTH_NUM) AS PRIOR_MONTH_NET_SALES,
    -- MoM Growth
    ROUND(m.NET_SALES - LAG(m.NET_SALES, 1) OVER (ORDER BY m.YEAR, m.MONTH_NUM), 2) AS MOM_GROWTH_AMOUNT,
    ROUND(((m.NET_SALES - LAG(m.NET_SALES, 1) OVER (ORDER BY m.YEAR, m.MONTH_NUM)) / 
          NULLIF(LAG(m.NET_SALES, 1) OVER (ORDER BY m.YEAR, m.MONTH_NUM), 0)) * 100, 2) AS MOM_GROWTH_PCT
FROM MonthlyBase m;

-- -----------------------------------------------------------------------------
-- VIEW 3: V_BI_PRODUCT_PERFORMANCE_RANKING
-- Product level performance ranking with margin & share analysis
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_BI_PRODUCT_PERFORMANCE_RANKING AS
SELECT 
    p.PRODUCT_KEY,
    p.PRODUCT_ID,
    p.PRODUCT_NAME,
    p.PRODUCT_CATEGORY,
    COUNT(f.SALES_KEY)                         AS TOTAL_ORDERS,
    SUM(f.QUANTITY)                            AS TOTAL_QUANTITY_SOLD,
    ROUND(SUM(f.NET_SALES), 2)                 AS TOTAL_NET_SALES,
    ROUND(SUM(f.GROSS_PROFIT), 2)              AS TOTAL_PROFIT,
    ROUND((SUM(f.GROSS_PROFIT) / SUM(f.NET_SALES)) * 100, 2) AS PROFIT_MARGIN_PCT,
    DENSE_RANK() OVER (ORDER BY SUM(f.NET_SALES) DESC) AS OVERALL_REVENUE_RANK,
    DENSE_RANK() OVER (PARTITION BY p.PRODUCT_CATEGORY ORDER BY SUM(f.NET_SALES) DESC) AS CATEGORY_REVENUE_RANK,
    ROUND((SUM(f.NET_SALES) / SUM(SUM(f.NET_SALES)) OVER ()) * 100, 2) AS SHARE_OF_TOTAL_REVENUE_PCT
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.PRODUCT_KEY = p.PRODUCT_KEY
GROUP BY p.PRODUCT_KEY, p.PRODUCT_ID, p.PRODUCT_NAME, p.PRODUCT_CATEGORY;

-- -----------------------------------------------------------------------------
-- VIEW 4: V_BI_REGIONAL_STORE_METRICS
-- Regional territory performance with store count and regional share
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_BI_REGIONAL_STORE_METRICS AS
SELECT 
    r.REGION,
    r.STATE,
    r.CITY,
    r.STORE_ID,
    COUNT(DISTINCT f.SALES_KEY)                AS TOTAL_ORDERS,
    SUM(f.QUANTITY)                            AS TOTAL_UNITS,
    ROUND(SUM(f.NET_SALES), 2)                 AS TOTAL_NET_SALES,
    ROUND(SUM(f.GROSS_PROFIT), 2)              AS TOTAL_GROSS_PROFIT,
    ROUND(AVG(f.NET_SALES), 2)                 AS AVG_TRANSACTION_VALUE,
    ROUND((SUM(f.NET_SALES) / SUM(SUM(f.NET_SALES)) OVER (PARTITION BY r.REGION)) * 100, 2) AS STORE_SHARE_OF_REGION_PCT,
    ROUND((SUM(f.NET_SALES) / SUM(SUM(f.NET_SALES)) OVER ()) * 100, 2) AS STORE_SHARE_OF_TOTAL_PCT
FROM FACT_SALES f
JOIN DIM_REGION r ON f.REGION_KEY = r.REGION_KEY
GROUP BY r.REGION, r.STATE, r.CITY, r.STORE_ID;

-- -----------------------------------------------------------------------------
-- VIEW 5: V_BI_CUSTOMER_DEMOGRAPHIC_METRICS
-- Customer demographics purchase behavior view
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_BI_CUSTOMER_DEMOGRAPHIC_METRICS AS
SELECT 
    c.GENDER,
    c.AGE_GROUP,
    COUNT(DISTINCT c.CUSTOMER_KEY)             AS UNIQUE_CUSTOMERS,
    COUNT(f.SALES_KEY)                         AS TOTAL_ORDERS,
    SUM(f.QUANTITY)                            AS UNITS_PURCHASED,
    ROUND(SUM(f.NET_SALES), 2)                 AS TOTAL_REVENUE,
    ROUND(AVG(f.NET_SALES), 2)                 AS AVG_ORDER_SPEND,
    ROUND(SUM(f.NET_SALES) / COUNT(DISTINCT c.CUSTOMER_KEY), 2) AS REVENUE_PER_CUSTOMER
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.CUSTOMER_KEY = c.CUSTOMER_KEY
GROUP BY c.GENDER, c.AGE_GROUP;

PROMPT >> All 5 Oracle BI Analytics Views deployed successfully.
