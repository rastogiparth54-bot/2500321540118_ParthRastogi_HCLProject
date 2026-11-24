# Enterprise Data Quality Audit & Reconciliation Report
**Project 1: Sales Performance Dashboard**
**Pipeline**: Automated Python Ingestion & Oracle Data Cleansing

---

## 1. Executive Summary
This Data Quality Audit details the systematic remediation of real-world retail transactional anomalies found in the raw Kaggle retail sales dataset. Through our production cleaning pipeline (`python/data_cleaning.py`), 5,055 raw transactional records were rigorously audited, sanitized, and conformed into 4,927 validated star-schema records.

### Key Quality Metrics:
- **Raw Input Rows**: 5,055 records
- **Cleaned Fact Rows**: 4,927 records (128 corrupted / duplicate records resolved)
- **Net Sales Reconciliation Discrepancy**: **$0.00 (0.0000% variance)** vs cleaned benchmark
- **Acceptance Criteria Standard**: Exceeds requirement of $\le 0.1\%$ discrepancy.

---

## 2. Key Test Cases & Defect Resolution Matrix

| Test Case # | Anomaly Type | Occurrences Identified | Root Cause in Enterprise Retail | Remediation Strategy | Post-Cleaning Validation Status |
|---|---|---|---|---|---|
| **TC-01** | **Exact Duplicate Rows** | 40 rows | Network retries, POS offline synchronization re-transmission | Deduplicated using `pandas.drop_duplicates()` retaining single primary instance. | **PASS**: 0 duplicate rows remaining. |
| **TC-02** | **Duplicate Transaction IDs** | 15 rows | Re-used transaction numbering across regional cash drawers | Deduplicated across `Transaction_ID` primary key keeping the first valid record. | **PASS**: 100% unique `Transaction_ID` integrity. |
| **TC-03** | **Corrupt & Multi-Format Dates** | 23 rows | Disparate locale settings (`DD/MM/YYYY`, `MM-DD-YYYY`, invalid days like `2024-02-31`) | Multi-format parsing using `strptime` fallback hierarchy; invalid calendar dates dropped. | **PASS**: All dates conformed to ISO `YYYY-MM-DD` and integer `Date_Key`. |
| **TC-04** | **Negative Quantities & Amounts** | 50 rows | Unlinked customer returns, cashier reversal errors, system bugs | Negative values quarantined to audited returns log; excluded from net positive sales fact. | **PASS**: Zero negative quantities or negative revenues in `Fact_Sales`. |
| **TC-05** | **Null / Missing Demographics** | 35 rows | Anonymous guest checkouts, optional loyalty sign-ups | Imputed `Customer_ID` to `'CUST-UNKNOWN'`, `Gender` to `'Unknown'`, `Age_Group` to `'Unknown'`. | **PASS**: Zero orphaned foreign keys or null strings in BI filters. |
| **TC-06** | **Inconsistent Text & Whitespace** | 50 rows | Manual cashier entry, mixed casing (`' electronics '`, `'CLOTHING'`) | Applied `.strip()` and standardized Title Case (`str.title()`) across Categories and Regions. | **PASS**: Conformed dimension members across all slicers. |
| **TC-07** | **Financial Arithmetic Mismatch** | 30 rows | Legacy POS rounding errors between gross price, discount %, and net amount | Recomputed arithmetic: `Gross = Qty * Price`, `Net = Gross * (1 - Disc)`, `Profit = Net - COGS`. | **PASS**: 100% mathematical integrity across every transaction row. |

---

## 3. End-to-End Reconciliation Table

The table below demonstrates the reconciliation across all four data stages (Raw CSV, Cleaned CSV, Oracle SQL Warehouse, and Power BI Model):

| Metric / Dimension | Raw Kaggle CSV | Cleaned CSV | Oracle SQL Warehouse | Power BI Model | Variance | Status |
|---|---|---|---|---|---|---|
| **Total Record Count** | 5,055 | **4,927** | **4,927** | **4,927** | **0 rows** | **100% Match** |
| **Total Net Sales Revenue** | $1,102,419.12 (Dirty) | **$1,073,808.62** | **$1,073,808.62** | **$1,073,808.62** | **$0.00 (0.00%)** | **PASS (<0.1%)** |
| **Total Gross Sales** | $1,151,320.40 | **$1,144,192.12** | **$1,144,192.12** | **$1,144,192.12** | **$0.00 (0.00%)** | **PASS** |
| **Total Discount Dollars** | N/A (Inconsistent) | **$70,383.50** | **$70,383.50** | **$70,383.50** | **$0.00 (0.00%)** | **PASS** |
| **Total Physical Units Sold** | 10,950 (with negs) | **11,161** | **11,161** | **11,161** | **0 units** | **PASS** |
| **Average Order Value (AOV)** | $218.08 | **$217.94** | **$217.94** | **$217.94** | **$0.00 (0.00%)** | **PASS** |
| **Gross Profit Margin (%)** | Undefined | **30.74%** | **30.74%** | **30.74%** | **0.00%** | **PASS** |

---

## 4. Star-Schema Referential Integrity Validation

An automated script evaluated the foreign key constraints to confirm zero orphaned records:
- `FACT_SALES.DATE_KEY` $\rightarrow$ `DIM_DATE.DATE_KEY`: **0 orphans (100% integrity)**
- `FACT_SALES.PRODUCT_KEY` $\rightarrow$ `DIM_PRODUCT.PRODUCT_KEY`: **0 orphans (100% integrity)**
- `FACT_SALES.CUSTOMER_KEY` $\rightarrow$ `DIM_CUSTOMER.CUSTOMER_KEY`: **0 orphans (100% integrity)**
- `FACT_SALES.REGION_KEY` $\rightarrow$ `DIM_REGION.REGION_KEY`: **0 orphans (100% integrity)**

---

## 5. Automated Audit Script Output Log
```text
================================================================================
AUTOMATED RECONCILIATION & QUALITY AUDIT REPORT
Project: Sales Performance Dashboard (Retail & E-Commerce)
================================================================================
--- 1. RECORD COUNT RECONCILIATION ---
Raw Source Rows               : 5,055
Cleaned Denormalized Rows      : 4,927
Fact Table Rows (Fact_Sales)   : 4,927
Target Benchmark Rows          : 4,927
>> PASS: Cleaned CSV and Star-Schema Fact_Sales have identical row counts (100% Match).

--- 2. FINANCIAL INTEGRITY & SALES RECONCILIATION ---
Cleaned CSV Net Sales          : $1,073,808.62
Fact Table Net Sales           : $1,073,808.62
Benchmark Net Sales            : $1,073,808.62
Absolute Discrepancy           : $0.00
Percentage Discrepancy         : 0.0000%
>> PASS: Sales reconciliation is within acceptance criteria threshold (<= 0.1% tolerance).
================================================================================
```
