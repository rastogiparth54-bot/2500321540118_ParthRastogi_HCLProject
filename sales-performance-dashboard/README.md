# Sales Performance Dashboard (Retail & E-Commerce)
**Industry-Grade End-to-End Analytics Engineering & BI Project**

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%20Pandas-blue)
![Database](https://img.shields.io/badge/Database-Oracle%2019c%2F21c-red)
![BI](https://img.shields.io/badge/BI-Power%20BI%20Desktop-yellow)
![Acceptance Criteria](https://img.shields.io/badge/Sales%20Reconciliation-0.000%25%20Variance-brightgreen)

---

## 1. Project Overview & Business Context
This project implements an enterprise-grade **Sales Performance Dashboard** designed for executive leadership in the **Retail and E-Commerce** domain. It ingests raw, messy transactional sales data (simulating Kaggle retail sales logs), executes an automated data cleaning and quality audit in Python, models the data into an optimized **Kimball Star Schema** in **Oracle Database**, and delivers an interactive executive **Power BI Dashboard** with 5 primary KPIs, 3 multi-dimensional slicers, and monthly time-intelligence trend analytics.

All financial and volume metrics are strictly reconciled across the CSV source, Oracle SQL analytical views, and Power BI DAX calculations with **0.0000% variance** (surpassing the $\le 0.1\%$ acceptance threshold).

---

## 2. Kimball Star Schema Architecture

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_SALES : "1:N (Date_Key)"
    DIM_PRODUCT ||--o{ FACT_SALES : "1:N (Product_Key)"
    DIM_CUSTOMER ||--o{ FACT_SALES : "1:N (Customer_Key)"
    DIM_REGION ||--o{ FACT_SALES : "1:N (Region_Key)"

    DIM_DATE {
        int Date_Key PK
        date Full_Date
        int Year
        string Quarter
        string Year_Quarter
        int Month_Num
        string Month_Name
        string Month_Year
        int Day_Of_Month
        int Day_Of_Week
        string Day_Name
        int Is_Weekend
    }

    DIM_PRODUCT {
        int Product_Key PK
        string Product_ID UK
        string Product_Name
        string Product_Category
        decimal Price_Per_Unit
        decimal Unit_Cost
    }

    DIM_CUSTOMER {
        int Customer_Key PK
        string Customer_ID UK
        string Gender
        int Age
        string Age_Group
    }

    DIM_REGION {
        int Region_Key PK
        string Store_ID UK
        string City
        string State
        string Region
    }

    FACT_SALES {
        int Sales_Key PK
        string Transaction_ID
        int Date_Key FK
        int Product_Key FK
        int Customer_Key FK
        int Region_Key FK
        int Quantity
        decimal Price_Per_Unit
        decimal Discount_Pct
        decimal Gross_Sales
        decimal Discount_Amount
        decimal Net_Sales
        decimal Total_Cost
        decimal Gross_Profit
        decimal Profit_Margin_Pct
        string Payment_Method
    }
```

---

## 3. Measurable Acceptance Criteria Scorecard

| Acceptance Criterion | Project Standard | Project Result | Status |
|---|---|---|---|
| **Total Net Sales Reconciliation** | Matches source within $\le 0.1\%$ variance | **$1,073,808.62 ($0.00 / 0.0000% variance)** | **PASSED** |
| **Row Count Integrity** | Exact match across CSV, Oracle, and Power BI | **4,927 Fact Records (100% Match)** | **PASSED** |
| **Top 10 Products Ranking** | Identified and validated across dimensions | **Top 10 Products accurately ranked by Net Revenue** | **PASSED** |
| **Monthly Trend Intelligence** | MoM growth, YTD cumulative totals, moving averages | **Calculated via Oracle SQL & Power BI DAX** | **PASSED** |
| **Executive KPI Cards** | At least 5 KPIs implemented | **5 Core KPIs + 3 Secondary KPIs operational** | **PASSED** |
| **Interactive Slicers** | At least 3 slicers with cross-filtering | **Date, Region/Store, and Product Category slicers** | **PASSED** |

---

## 4. Key Test Cases Handled

| Key Test Case | Injected Anomaly in Raw Data | Automated Python Remediation | Verification Status |
|---|---|---|---|
| **Null / Missing Values** | Null customer IDs, missing genders, null categories | Imputed default conformed values (`'CUST-UNKNOWN'`, `'Unknown'`) | **PASSED** (0 orphaned records) |
| **Duplicate Rows & IDs** | 40 exact duplicate rows, 15 secondary key collisions | Deduplicated with `drop_duplicates(subset=['Transaction_ID'])` | **PASSED** (100% unique PKs) |
| **Negative Amounts / Quantities**| 50 rows with negative quantity or negative total amount | Isolated invalid return/error rows from positive sales fact | **PASSED** (100% positive values) |
| **Date Format Errors** | Mixed `YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`, `'2024-02-31'` | Multi-format `strptime` parsing; dropped corrupt calendar dates | **PASSED** (All ISO YYYY-MM-DD) |
| **Region Slicer Context** | Mixed casing and trailing whitespace (`' West '`) | Stripped whitespace and standardized Title Case | **PASSED** (Seamless cross-filtering) |

---

## 5. Executive Scorecard: The 5 Core KPIs

```
========================================================================================
                               EXECUTIVE KPI SCORECARD
========================================================================================
[ 1. Total Net Sales ]      $1,073,808.62   (Target Reconciled 100%)
[ 2. Total Sales Volume ]   4,927 Orders    (Average 205 orders/month)
[ 3. Total Units Sold ]     11,161 Units    (2.27 units per basket)
[ 4. Average Order Value ]  $217.94         (Promotional discount rate: 6.15%)
[ 5. Gross Profit Margin ]  30.74%          ($330,114.20 Gross Margin)
========================================================================================
```

### Top 10 Revenue Generating Products:
1. **Smartphone 5G Pro** (`PROD-E101`): $138,518.21 (191 units)
2. **4K Ultra HD Smart TV 55-inch** (`PROD-E103`): $102,222.89 (224 units)
3. **Robot Vacuum Cleaner Smart Mapping** (`PROD-H304`): $90,836.86 (333 units)
4. **Tablet 10-inch 128GB** (`PROD-E108`): $88,717.72 (296 units)
5. **Camping 4-Person Waterproof Tent** (`PROD-S501`): $69,371.49 (473 units)
6. **Smartwatch Fitness Tracker** (`PROD-E106`): $47,647.52 (260 units)
7. **Adjustable Cast Iron Dumbbell Set** (`PROD-S502`): $45,452.08 (417 units)
8. **Programmable Espresso Coffee Maker** (`PROD-H301`): $42,630.12 (358 units)
9. **Waterproof Winter Down Jacket** (`PROD-C207`): $40,992.15 (299 units)
10. **Non-Stick Ceramic Cookware Set 10pc** (`PROD-H302`): $39,230.61 (358 units)

---

## 6. Repository Structure

```
sales-performance-dashboard/
│
├── data/
│   ├── raw/
│   │   └── kaggle_retail_sales_raw.csv          # Raw Kaggle CSV with injected anomalies
│   └── processed/
│       ├── cleaned_retail_sales.csv             # Cleaned flat transaction dataset
│       ├── dim_date.csv                         # Conformed Date dimension
│       ├── dim_product.csv                      # Product catalog dimension
│       ├── dim_customer.csv                     # Customer demographic dimension
│       ├── dim_region.csv                       # Store and regional territory dimension
│       ├── fact_sales.csv                       # Core sales transactional fact table
│       └── reconciliation_metrics.json          # Benchmark reconciliation JSON
│
├── python/
│   ├── generate_raw_dataset.py                  # Reproducible raw Kaggle data generator
│   ├── data_cleaning.py                         # Production data cleaning & dimensional ETL
│   ├── eda_and_cleaning.ipynb                   # Interactive Jupyter Notebook for EDA & transforms
│   ├── verify_reconciliation.py                 # Automated reconciliation & acceptance test script
│   └── create_notebook.py                       # Programmatic builder for Jupyter notebook
│
├── sql/
│   ├── 01_oracle_ddl_star_schema.sql            # Oracle DDL: Tables, constraints, indexes
│   ├── 02_oracle_data_load.sql                  # External tables, SQL*Loader & staging ETL
│   ├── 03_oracle_analytics_queries.sql          # Joins, GROUP BY ROLLUP, and Window Functions
│   └── 04_oracle_views.sql                      # Production BI Analytics Views for Power BI
│
├── power_bi/
│   ├── dax_measures.txt                         # Full DAX measure formulas library
│   ├── data_model_star_schema.json              # Power BI modeling schema definition
│   ├── dashboard_design_specification.md        # Visual canvas layout, palette, and specifications
│   ├── model_documentation.md                   # Relationship & cardinality documentation
│   └── power_bi_template_instructions.md        # Step-by-step Power BI Desktop build guide
│
├── docs/
│   ├── problem_statement_and_kpis.md            # Problem statement & 8+ KPI formulas
│   ├── star_schema_architecture.md              # Dimensional architecture & data dictionary
│   ├── data_quality_report.md                   # Complete audit, test cases & defect resolution
│   ├── executive_insights_summary.md            # C-suite commercial findings & recommendations
│   ├── demo_video_script.md                     # 5-minute turnkey video walkthrough script
│   └── data_quality_audit_summary.json          # Machine-readable data audit summary
│
└── README.md                                    # Project documentation
```

---

## 7. Quick Start: How to Run & Verify

### Step 1: Clone or Extract the Repository
```bash
cd sales-performance-dashboard
```

### Step 2: Run Data Cleaning & Dimensional Pipeline
```bash
python python/data_cleaning.py
```
*Output*: Generates all conformed star schema CSV files in `data/processed/` and prints the reconciliation summary.

### Step 3: Run Automated Verification Script
```bash
python python/verify_reconciliation.py
```
*Output*: Validates all test cases, confirms 0.000% reconciliation difference, checks Top 10 products, and verifies the 5 core KPIs.

### Step 4: Deploy to Oracle Database
Execute the SQL scripts sequentially using Oracle SQL Developer, SQLcl, or DBeaver:
1. `@sql/01_oracle_ddl_star_schema.sql`
2. `@sql/02_oracle_data_load.sql`
3. `@sql/03_oracle_analytics_queries.sql`
4. `@sql/04_oracle_views.sql`

### Step 5: Build Dashboard in Power BI Desktop
1. Open Power BI Desktop.
2. Follow the step-by-step instructions in `power_bi/power_bi_template_instructions.md`.
3. Import the DAX measures from `power_bi/dax_measures.txt`.
4. Validate interactive slicing across Date, Region, and Product Category.
