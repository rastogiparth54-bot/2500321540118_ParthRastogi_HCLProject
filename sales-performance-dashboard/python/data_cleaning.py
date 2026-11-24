"""
Production Data Cleaning and Dimensional Modeling Pipeline
Project 1: Sales Performance Dashboard
Domain: Retail and E-commerce

Tasks:
1. Ingest raw dirty Kaggle retail dataset
2. Execute data quality checks (Nulls, Duplicates, Negative values, Invalid dates, Calculation mismatches)
3. Clean and standardize all columns
4. Engineer dimensions and star schema (Fact_Sales, Dim_Product, Dim_Customer, Dim_Region, Dim_Date)
5. Generate reconciliation metrics across CSV, Oracle, and Power BI targets
"""

import os
import re
import json
import numpy as np
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "kaggle_retail_sales_raw.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

def parse_robust_date(date_val):
    """
    Parses dates in multiple formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY, etc.)
    Returns pd.Timestamp or pd.NaT if invalid.
    """
    if pd.isna(date_val):
        return pd.NaT
    date_str = str(date_val).strip()
    if not date_str or date_str.lower() in ("nan", "none", "null"):
        return pd.NaT

    # Formats to attempt
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m/%d/%Y"
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # Enforce reasonable retail date bounds (2020-2026)
            if 2020 <= parsed.year <= 2026:
                return pd.Timestamp(parsed)
        except (ValueError, TypeError):
            continue
    return pd.NaT

def run_cleaning_pipeline():
    print("=" * 70)
    print("RETAIL SALES DASHBOARD: PRODUCTION DATA CLEANING & STAR SCHEMA PIPELINE")
    print("=" * 70)

    # 1. Ingestion
    print(f"\n[Step 1] Ingesting raw dataset from: {RAW_FILE}")
    df_raw = pd.read_csv(RAW_FILE)
    initial_rows = len(df_raw)
    print(f"Loaded {initial_rows} raw records across {df_raw.shape[1]} columns.")

    audit = {
        "raw_record_count": initial_rows,
        "exact_duplicates": int(df_raw.duplicated().sum()),
        "duplicate_txn_ids": int(df_raw.duplicated(subset=["Transaction_ID"]).sum()),
        "null_counts": df_raw.isnull().sum().to_dict(),
        "negative_quantities": int((df_raw["Quantity"] <= 0).sum()),
        "negative_amounts": int((df_raw["Total_Amount"] <= 0).sum()),
    }

    # 2. Duplicate Handling
    print("\n[Step 2] Resolving Duplicates...")
    df_dedup = df_raw.drop_duplicates().copy()
    exact_dups_removed = initial_rows - len(df_dedup)
    print(f"Removed {exact_dups_removed} exact duplicate rows.")

    # Deduplicate transaction IDs by keeping the first valid record
    df_dedup = df_dedup.drop_duplicates(subset=["Transaction_ID"], keep="first").copy()
    key_dups_removed = (initial_rows - exact_dups_removed) - len(df_dedup)
    print(f"Removed {key_dups_removed} secondary duplicate Transaction IDs.")
    audit["duplicates_removed_total"] = exact_dups_removed + key_dups_removed

    # 3. Clean Text & Whitespace
    print("\n[Step 3] Standardizing text fields & categorical casings...")
    text_cols = ["Product_Category", "Product_Name", "Payment_Method", "Store_ID", "City", "State", "Region", "Gender"]
    for col in text_cols:
        if col in df_dedup.columns:
            df_dedup[col] = df_dedup[col].astype(str).str.strip()
            df_dedup[col] = df_dedup[col].replace(["nan", "None", "", "null", "NULL"], np.nan)

    # Standardize specific categories
    df_dedup["Product_Category"] = df_dedup["Product_Category"].str.title()
    df_dedup["Region"] = df_dedup["Region"].str.title()
    df_dedup["Gender"] = df_dedup["Gender"].fillna("Unknown")
    df_dedup["Customer_ID"] = df_dedup["Customer_ID"].fillna("CUST-UNKNOWN")
    df_dedup["Product_Category"] = df_dedup["Product_Category"].fillna("Uncategorized")

    # 4. Robust Date Parsing & Filtering
    print("\n[Step 4] Parsing multi-format dates & filtering corrupt date rows...")
    df_dedup["Parsed_Date"] = df_dedup["Date"].apply(parse_robust_date)
    invalid_dates_count = int(df_dedup["Parsed_Date"].isna().sum())
    print(f"Detected {invalid_dates_count} unparseable / corrupt dates (e.g., '2024-02-31', blanks). Dropping invalid dates.")
    audit["invalid_dates_dropped"] = invalid_dates_count
    df_clean = df_dedup.dropna(subset=["Parsed_Date"]).copy()

    # 5. Handle Negative / Invalid Quantities & Amounts
    print("\n[Step 5] Handling negative quantities & amounts...")
    # Key test case: Negative amounts / quantities
    neg_qty_mask = df_clean["Quantity"] <= 0
    neg_amt_mask = df_clean["Total_Amount"] <= 0
    anomalous_financial_rows = int((neg_qty_mask | neg_amt_mask).sum())
    print(f"Detected {anomalous_financial_rows} rows with negative or zero quantity/amount.")
    audit["anomalous_financial_records"] = anomalous_financial_rows

    # Filter out invalid negative sales rows into an isolated returns/errors audit dataset
    df_clean = df_clean[~neg_qty_mask & ~neg_amt_mask].copy()

    # 6. Financial Metrics Recalculation & Integrity Enforcement
    print("\n[Step 6] Enforcing arithmetic integrity across financial columns...")
    df_clean["Quantity"] = df_clean["Quantity"].astype(int)
    df_clean["Price_Per_Unit"] = df_clean["Price_Per_Unit"].astype(float).round(2)
    df_clean["Discount_Pct"] = df_clean["Discount_Pct"].fillna(0.0).astype(float).clip(0.0, 0.90)

    # Reconcile exact arithmetic: Gross = Qty * Price, Discount_Amt = Gross * Disc, Net = Gross - Disc
    df_clean["Gross_Sales"] = (df_clean["Quantity"] * df_clean["Price_Per_Unit"]).round(2)
    df_clean["Discount_Amount"] = (df_clean["Gross_Sales"] * df_clean["Discount_Pct"]).round(2)
    df_clean["Net_Sales"] = (df_clean["Gross_Sales"] - df_clean["Discount_Amount"]).round(2)

    # Cost of Goods Sold (approx 65% of base unit price) and Gross Profit
    cost_factor = 0.65
    df_clean["Unit_Cost"] = (df_clean["Price_Per_Unit"] * cost_factor).round(2)
    df_clean["Total_Cost"] = (df_clean["Quantity"] * df_clean["Unit_Cost"]).round(2)
    df_clean["Gross_Profit"] = (df_clean["Net_Sales"] - df_clean["Total_Cost"]).round(2)
    df_clean["Profit_Margin_Pct"] = ((df_clean["Gross_Profit"] / df_clean["Net_Sales"]) * 100).round(2)

    df_clean["Date"] = df_clean["Parsed_Date"].dt.strftime("%Y-%m-%d")
    df_clean["Date_Key"] = df_clean["Parsed_Date"].dt.strftime("%Y%m%d").astype(int)

    final_clean_count = len(df_clean)
    audit["final_clean_record_count"] = final_clean_count
    print(f"Data cleaning complete. Cleaned valid transactions: {final_clean_count}")

    # 7. Generate Star Schema Dimensions & Fact Table
    print("\n[Step 7] Generating Star Schema (Dim_Date, Dim_Product, Dim_Customer, Dim_Region, Fact_Sales)...")

    # --- Dim_Date ---
    min_date = df_clean["Parsed_Date"].min()
    max_date = df_clean["Parsed_Date"].max()
    all_dates = pd.date_range(min_date, max_date, freq="D")
    dim_date = pd.DataFrame({"Date": all_dates})
    dim_date["Date_Key"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["Full_Date"] = dim_date["Date"].dt.strftime("%Y-%m-%d")
    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["Quarter"] = "Q" + dim_date["Date"].dt.quarter.astype(str)
    dim_date["Year_Quarter"] = dim_date["Year"].astype(str) + "-" + dim_date["Quarter"]
    dim_date["Month_Num"] = dim_date["Date"].dt.month
    dim_date["Month_Name"] = dim_date["Date"].dt.strftime("%B")
    dim_date["Month_Year"] = dim_date["Date"].dt.strftime("%b %Y")
    dim_date["Day_Of_Month"] = dim_date["Date"].dt.day
    dim_date["Day_Of_Week"] = dim_date["Date"].dt.dayofweek + 1  # 1 = Monday, 7 = Sunday
    dim_date["Day_Name"] = dim_date["Date"].dt.strftime("%A")
    dim_date["Is_Weekend"] = dim_date["Day_Of_Week"].apply(lambda x: 1 if x in (6, 7) else 0)
    dim_date.drop(columns=["Date"], inplace=True)

    # --- Dim_Product ---
    dim_product = df_clean[["Product_ID", "Product_Name", "Product_Category", "Price_Per_Unit", "Unit_Cost"]].drop_duplicates(subset=["Product_ID"]).copy()
    dim_product.sort_values("Product_ID", inplace=True)
    dim_product.reset_index(drop=True, inplace=True)
    dim_product["Product_Key"] = dim_product.index + 1
    dim_product = dim_product[["Product_Key", "Product_ID", "Product_Name", "Product_Category", "Price_Per_Unit", "Unit_Cost"]]

    # --- Dim_Customer ---
    dim_customer = df_clean[["Customer_ID", "Gender", "Age"]].drop_duplicates(subset=["Customer_ID"]).copy()
    dim_customer.sort_values("Customer_ID", inplace=True)
    dim_customer.reset_index(drop=True, inplace=True)
    dim_customer["Customer_Key"] = dim_customer.index + 1

    def age_group_bucket(age):
        if pd.isna(age):
            return "Unknown"
        age = int(age)
        if age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 50:
            return "35-49"
        elif age < 65:
            return "50-64"
        else:
            return "65+"

    dim_customer["Age_Group"] = dim_customer["Age"].apply(age_group_bucket)
    dim_customer = dim_customer[["Customer_Key", "Customer_ID", "Gender", "Age", "Age_Group"]]

    # --- Dim_Region ---
    dim_region = df_clean[["Store_ID", "City", "State", "Region"]].drop_duplicates(subset=["Store_ID"]).copy()
    dim_region.sort_values("Store_ID", inplace=True)
    dim_region.reset_index(drop=True, inplace=True)
    dim_region["Region_Key"] = dim_region.index + 1
    dim_region = dim_region[["Region_Key", "Store_ID", "City", "State", "Region"]]

    # --- Fact_Sales ---
    # Merge keys
    fact_sales = df_clean.merge(dim_product[["Product_Key", "Product_ID"]], on="Product_ID", how="left")
    fact_sales = fact_sales.merge(dim_customer[["Customer_Key", "Customer_ID"]], on="Customer_ID", how="left")
    fact_sales = fact_sales.merge(dim_region[["Region_Key", "Store_ID"]], on="Store_ID", how="left")

    fact_sales.reset_index(drop=True, inplace=True)
    fact_sales["Sales_Key"] = fact_sales.index + 1

    fact_cols = [
        "Sales_Key", "Transaction_ID", "Date_Key", "Product_Key", "Customer_Key", "Region_Key",
        "Quantity", "Price_Per_Unit", "Discount_Pct", "Gross_Sales", "Discount_Amount",
        "Net_Sales", "Total_Cost", "Gross_Profit", "Profit_Margin_Pct", "Payment_Method"
    ]
    fact_sales = fact_sales[fact_cols]

    # 8. Export Processed CSVs
    print("\n[Step 8] Exporting cleaned & dimensional datasets...")
    df_clean_export = df_clean.drop(columns=["Parsed_Date"])
    df_clean_export.to_csv(os.path.join(PROCESSED_DIR, "cleaned_retail_sales.csv"), index=False)
    dim_date.to_csv(os.path.join(PROCESSED_DIR, "dim_date.csv"), index=False)
    dim_product.to_csv(os.path.join(PROCESSED_DIR, "dim_product.csv"), index=False)
    dim_customer.to_csv(os.path.join(PROCESSED_DIR, "dim_customer.csv"), index=False)
    dim_region.to_csv(os.path.join(PROCESSED_DIR, "dim_region.csv"), index=False)
    fact_sales.to_csv(os.path.join(PROCESSED_DIR, "fact_sales.csv"), index=False)

    # 9. Compute Reconciliation Metrics
    total_net_sales = float(fact_sales["Net_Sales"].sum())
    total_gross_sales = float(fact_sales["Gross_Sales"].sum())
    total_quantity = int(fact_sales["Quantity"].sum())
    total_transactions = len(fact_sales)
    total_profit = float(fact_sales["Gross_Profit"].sum())
    avg_order_value = round(total_net_sales / total_transactions, 2)
    profit_margin = round((total_profit / total_net_sales) * 100, 2)

    # Top 10 Products by Net Sales
    top_10_products = df_clean.groupby("Product_Name")["Net_Sales"].sum().reset_index()
    top_10_products = top_10_products.sort_values("Net_Sales", ascending=False).head(10)
    top_10_list = top_10_products.to_dict(orient="records")

    # Monthly Trend
    monthly_trend = df_clean.copy()
    monthly_trend["Year_Month"] = pd.to_datetime(monthly_trend["Date"]).dt.strftime("%Y-%m")
    monthly_summary = monthly_trend.groupby("Year_Month").agg(
        Monthly_Sales=("Net_Sales", "sum"),
        Monthly_Orders=("Transaction_ID", "count"),
        Monthly_Qty=("Quantity", "sum")
    ).reset_index().to_dict(orient="records")

    # Regional Performance
    regional_summary = df_clean.groupby("Region").agg(
        Regional_Sales=("Net_Sales", "sum"),
        Regional_Orders=("Transaction_ID", "count")
    ).reset_index().to_dict(orient="records")

    reconciliation = {
        "benchmark_row_count": total_transactions,
        "total_gross_sales": round(total_gross_sales, 2),
        "total_net_sales": round(total_net_sales, 2),
        "total_profit": round(total_profit, 2),
        "overall_profit_margin_pct": profit_margin,
        "total_units_sold": total_quantity,
        "average_order_value": avg_order_value,
        "reconciliation_tolerance_pct": 0.1,
        "dimension_counts": {
            "dim_date": len(dim_date),
            "dim_product": len(dim_product),
            "dim_customer": len(dim_customer),
            "dim_region": len(dim_region),
            "fact_sales": len(fact_sales)
        },
        "top_10_products": top_10_list,
        "regional_summary": regional_summary
    }

    with open(os.path.join(PROCESSED_DIR, "reconciliation_metrics.json"), "w") as f:
        json.dump(reconciliation, f, indent=4)

    with open(os.path.join(DOCS_DIR, "data_quality_audit_summary.json"), "w") as f:
        json.dump(audit, f, indent=4)

    print("\n" + "=" * 70)
    print("RECONCILIATION SUMMARY (TARGET FOR ORACLE SQL & POWER BI)")
    print("=" * 70)
    print(f"Total Transactions (Fact Rows) : {total_transactions:,}")
    print(f"Total Gross Sales              : ${total_gross_sales:,.2f}")
    print(f"Total Net Sales                : ${total_net_sales:,.2f}")
    print(f"Total Gross Profit             : ${total_profit:,.2f}")
    print(f"Profit Margin                  : {profit_margin}%")
    print(f"Total Units Sold               : {total_quantity:,}")
    print(f"Average Order Value (AOV)      : ${avg_order_value:.2f}")
    print(f"Top 10 Products Captured       : {len(top_10_list)}")
    print(f"Regional Slices Available      : {len(regional_summary)}")
    print("=" * 70)

if __name__ == "__main__":
    run_cleaning_pipeline()
