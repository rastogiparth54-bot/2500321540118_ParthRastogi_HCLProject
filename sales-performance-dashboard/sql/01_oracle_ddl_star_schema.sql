-- =============================================================================
-- Project 1: Sales Performance Dashboard (Retail & E-Commerce)
-- Script 01: Oracle DDL - Star Schema Architecture
-- Database Engine: Oracle Database 19c / 21c / 23c Autonomous Database
-- =============================================================================

-- Clean up existing objects safely
BEGIN
    FOR t IN (SELECT table_name FROM user_tables WHERE table_name IN ('FACT_SALES', 'DIM_DATE', 'DIM_PRODUCT', 'DIM_CUSTOMER', 'DIM_REGION')) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
    END LOOP;
END;
/

-- -----------------------------------------------------------------------------
-- 1. DIMENSION TABLE: DIM_DATE
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_DATE (
    DATE_KEY         NUMBER(8)        NOT NULL,   -- e.g., 20230514
    FULL_DATE        DATE             NOT NULL,
    YEAR             NUMBER(4)        NOT NULL,
    QUARTER          VARCHAR2(2)      NOT NULL,   -- 'Q1', 'Q2', etc.
    YEAR_QUARTER     VARCHAR2(7)      NOT NULL,   -- '2023-Q1'
    MONTH_NUM        NUMBER(2)        NOT NULL,
    MONTH_NAME       VARCHAR2(15)     NOT NULL,
    MONTH_YEAR       VARCHAR2(8)      NOT NULL,   -- 'May 2023'
    DAY_OF_MONTH     NUMBER(2)        NOT NULL,
    DAY_OF_WEEK      NUMBER(1)        NOT NULL,   -- 1 = Mon, 7 = Sun
    DAY_NAME         VARCHAR2(15)     NOT NULL,
    IS_WEEKEND       NUMBER(1)        DEFAULT 0 NOT NULL,
    CONSTRAINT PK_DIM_DATE PRIMARY KEY (DATE_KEY),
    CONSTRAINT CK_DATE_IS_WEEKEND CHECK (IS_WEEKEND IN (0, 1))
);

COMMENT ON TABLE DIM_DATE IS 'Conformed Date Dimension supporting multi-calendar slicing and time intelligence.';
COMMENT ON COLUMN DIM_DATE.DATE_KEY IS 'Surrogate Date Key in YYYYMMDD integer format.';

-- -----------------------------------------------------------------------------
-- 2. DIMENSION TABLE: DIM_PRODUCT
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_PRODUCT (
    PRODUCT_KEY      NUMBER(10)       NOT NULL,   -- Surrogate Key
    PRODUCT_ID       VARCHAR2(20)     NOT NULL,   -- Natural Business Key
    PRODUCT_NAME     VARCHAR2(100)    NOT NULL,
    PRODUCT_CATEGORY VARCHAR2(50)     NOT NULL,
    PRICE_PER_UNIT   NUMBER(10, 2)    NOT NULL,
    UNIT_COST        NUMBER(10, 2)    NOT NULL,
    CONSTRAINT PK_DIM_PRODUCT PRIMARY KEY (PRODUCT_KEY),
    CONSTRAINT UQ_PRODUCT_NATURAL_ID UNIQUE (PRODUCT_ID),
    CONSTRAINT CK_PROD_PRICE_POSITIVE CHECK (PRICE_PER_UNIT >= 0),
    CONSTRAINT CK_PROD_COST_POSITIVE CHECK (UNIT_COST >= 0)
);

COMMENT ON TABLE DIM_PRODUCT IS 'Product Dimension holding retail catalog attributes, categorizations, and unit cost baselines.';

-- -----------------------------------------------------------------------------
-- 3. DIMENSION TABLE: DIM_CUSTOMER
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_CUSTOMER (
    CUSTOMER_KEY     NUMBER(10)       NOT NULL,   -- Surrogate Key
    CUSTOMER_ID      VARCHAR2(30)     NOT NULL,   -- Natural Business Key
    GENDER           VARCHAR2(20)     DEFAULT 'Unknown' NOT NULL,
    AGE              NUMBER(3),
    AGE_GROUP        VARCHAR2(20)     DEFAULT 'Unknown' NOT NULL,
    CONSTRAINT PK_DIM_CUSTOMER PRIMARY KEY (CUSTOMER_KEY),
    CONSTRAINT UQ_CUSTOMER_NATURAL_ID UNIQUE (CUSTOMER_ID)
);

COMMENT ON TABLE DIM_CUSTOMER IS 'Customer Demographics Dimension holding age cohorts and gender segments.';

-- -----------------------------------------------------------------------------
-- 4. DIMENSION TABLE: DIM_REGION
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_REGION (
    REGION_KEY       NUMBER(10)       NOT NULL,   -- Surrogate Key
    STORE_ID         VARCHAR2(20)     NOT NULL,   -- Natural Store Key
    CITY             VARCHAR2(50)     NOT NULL,
    STATE            VARCHAR2(10)     NOT NULL,
    REGION           VARCHAR2(30)     NOT NULL,
    CONSTRAINT PK_DIM_REGION PRIMARY KEY (REGION_KEY),
    CONSTRAINT UQ_REGION_STORE_ID UNIQUE (STORE_ID)
);

COMMENT ON TABLE DIM_REGION IS 'Store and Geographic Region Dimension supporting territorial drill-downs.';

-- -----------------------------------------------------------------------------
-- 5. FACT TABLE: FACT_SALES
-- -----------------------------------------------------------------------------
CREATE TABLE FACT_SALES (
    SALES_KEY        NUMBER(12)       NOT NULL,   -- Fact Surrogate Key
    TRANSACTION_ID   VARCHAR2(30)     NOT NULL,   -- Source System Transaction ID
    DATE_KEY         NUMBER(8)        NOT NULL,   -- FK to DIM_DATE
    PRODUCT_KEY      NUMBER(10)       NOT NULL,   -- FK to DIM_PRODUCT
    CUSTOMER_KEY     NUMBER(10)       NOT NULL,   -- FK to DIM_CUSTOMER
    REGION_KEY       NUMBER(10)       NOT NULL,   -- FK to DIM_REGION
    QUANTITY         NUMBER(6)        NOT NULL,
    PRICE_PER_UNIT   NUMBER(10, 2)    NOT NULL,
    DISCOUNT_PCT     NUMBER(4, 2)     DEFAULT 0.00 NOT NULL,
    GROSS_SALES      NUMBER(12, 2)    NOT NULL,
    DISCOUNT_AMOUNT  NUMBER(12, 2)    DEFAULT 0.00 NOT NULL,
    NET_SALES        NUMBER(12, 2)    NOT NULL,
    TOTAL_COST       NUMBER(12, 2)    NOT NULL,
    GROSS_PROFIT     NUMBER(12, 2)    NOT NULL,
    PROFIT_MARGIN_PCT NUMBER(6, 2)    NOT NULL,
    PAYMENT_METHOD   VARCHAR2(30)     NOT NULL,
    LOAD_TIMESTAMP   TIMESTAMP        DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT PK_FACT_SALES PRIMARY KEY (SALES_KEY),
    CONSTRAINT FK_SALES_DATE FOREIGN KEY (DATE_KEY) REFERENCES DIM_DATE(DATE_KEY),
    CONSTRAINT FK_SALES_PRODUCT FOREIGN KEY (PRODUCT_KEY) REFERENCES DIM_PRODUCT(PRODUCT_KEY),
    CONSTRAINT FK_SALES_CUSTOMER FOREIGN KEY (CUSTOMER_KEY) REFERENCES DIM_CUSTOMER(CUSTOMER_KEY),
    CONSTRAINT FK_SALES_REGION FOREIGN KEY (REGION_KEY) REFERENCES DIM_REGION(REGION_KEY),
    CONSTRAINT CK_SALES_QTY_POSITIVE CHECK (QUANTITY > 0),
    CONSTRAINT CK_SALES_NET_POSITIVE CHECK (NET_SALES >= 0)
);

COMMENT ON TABLE FACT_SALES IS 'Core Sales Fact Table storing atomic transactional performance metrics and financial calculations.';

-- -----------------------------------------------------------------------------
-- PERFORMANCE OPTIMIZATION INDEXES
-- -----------------------------------------------------------------------------
CREATE INDEX IDX_FACT_SALES_DATE ON FACT_SALES(DATE_KEY);
CREATE INDEX IDX_FACT_SALES_PRODUCT ON FACT_SALES(PRODUCT_KEY);
CREATE INDEX IDX_FACT_SALES_CUSTOMER ON FACT_SALES(CUSTOMER_KEY);
CREATE INDEX IDX_FACT_SALES_REGION ON FACT_SALES(REGION_KEY);
CREATE INDEX IDX_FACT_SALES_TXN ON FACT_SALES(TRANSACTION_ID);

-- Bitmap Index for high-cardinality aggregation in Oracle Enterprise Edition
CREATE BITMAP INDEX BMI_REGION_TERRITORY ON DIM_REGION(REGION);
CREATE BITMAP INDEX BMI_PROD_CATEGORY ON DIM_PRODUCT(PRODUCT_CATEGORY);
CREATE BITMAP INDEX BMI_CUST_GENDER ON DIM_CUSTOMER(GENDER);
CREATE BITMAP INDEX BMI_CUST_AGE_GROUP ON DIM_CUSTOMER(AGE_GROUP);

COMMIT;
PROMPT >> Oracle Star Schema DDL deployed successfully.
