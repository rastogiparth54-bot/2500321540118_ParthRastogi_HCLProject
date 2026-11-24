"""
Script to generate the complete eda_and_cleaning.ipynb notebook
"""
import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTEBOOK_PATH = os.path.join(BASE_DIR, "python", "eda_and_cleaning.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Project 1: Sales Performance Dashboard (Retail & E-Commerce)\n",
            "## Exploratory Data Analysis, Data Quality Audit & Star-Schema Pipeline\n",
            "\n",
            "### Overview & Objectives\n",
            "This notebook executes a production-grade data engineering pipeline on a retail transactions dataset.\n",
            "It addresses dirty-data edge cases (nulls, duplicates, negative amounts, multi-format dates), establishes financial reconciliation, and builds an enterprise Star Schema (Fact and Dimension tables) ready for Oracle SQL and Power BI modeling.\n",
            "\n",
            "### Key Acceptance Criteria:\n",
            "- Top 10 products and monthly sales trends identified and verified.\n",
            "- Total net sales reconciled across CSV, Oracle SQL, and Power BI within **0.1% tolerance**.\n",
            "- Support at least **5 executive KPIs** and **3 multi-dimensional slicers**.\n",
            "- Rigorous resolution of key test cases: null/duplicate rows, negative amounts, date format errors."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "from datetime import datetime\n",
            "\n",
            "# Paths\n",
            "RAW_CSV_PATH = '../data/raw/kaggle_retail_sales_raw.csv'\n",
            "PROCESSED_DIR = '../data/processed/'\n",
            "os.makedirs(PROCESSED_DIR, exist_ok=True)\n",
            "\n",
            "print('Environment and libraries ready.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Data Ingestion & Initial Quality Audit\n",
            "We inspect the raw CSV dataset and identify nulls, duplicates, date issues, and arithmetic discrepancies."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 2,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_raw = pd.read_csv(RAW_CSV_PATH)\n",
            "print(f'Raw dataset shape: {df_raw.shape}')\n",
            "print('\\nData Types and Non-Null Counts:')\n",
            "print(df_raw.info())\n",
            "df_raw.head(5)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 3,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Key Test Case 1: Detect Duplicates\n",
            "exact_dups = df_raw.duplicated().sum()\n",
            "key_dups = df_raw.duplicated(subset=['Transaction_ID']).sum()\n",
            "print(f'Exact Duplicate Rows: {exact_dups}')\n",
            "print(f'Duplicate Transaction IDs: {key_dups}')\n",
            "\n",
            "# Key Test Case 2: Missing / Null Values\n",
            "print('\\nMissing values count per column:')\n",
            "print(df_raw.isnull().sum()[df_raw.isnull().sum() > 0])\n",
            "\n",
            "# Key Test Case 3: Negative Quantities and Amounts\n",
            "neg_qty = (df_raw['Quantity'] <= 0).sum()\n",
            "neg_amt = (df_raw['Total_Amount'] <= 0).sum()\n",
            "print(f'\\nNegative / Zero Quantities: {neg_qty}')\n",
            "print(f'Negative / Zero Total Amounts: {neg_amt}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Multi-Format Date Parsing & Quality Filtering\n",
            "The raw dataset contains mixed date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`) and corrupt entries (`2024-02-31`, blank spaces)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 4,
        "metadata": {},
        "outputs": [],
        "source": [
            "def parse_multi_format_date(val):\n",
            "    if pd.isna(val):\n",
            "        return pd.NaT\n",
            "    s = str(val).strip()\n",
            "    if not s or s.lower() in ('nan', 'none', 'null'):\n",
            "        return pd.NaT\n",
            "    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y']\n",
            "    for fmt in formats:\n",
            "        try:\n",
            "            p = datetime.strptime(s, fmt)\n",
            "            if 2020 <= p.year <= 2026:\n",
            "                return pd.Timestamp(p)\n",
            "        except (ValueError, TypeError):\n",
            "            continue\n",
            "    return pd.NaT\n",
            "\n",
            "df_raw['Parsed_Date'] = df_raw['Date'].apply(parse_multi_format_date)\n",
            "corrupt_dates = df_raw['Parsed_Date'].isna().sum()\n",
            "print(f'Corrupt or unparseable dates identified: {corrupt_dates}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Data Cleaning Pipeline\n",
            "- Deduplication\n",
            "- Text normalization & whitespace trimming\n",
            "- Imputation of missing customer & category attributes\n",
            "- Filtering invalid negative sales records\n",
            "- Arithmetic recalculation: Gross Sales, Discounts, Net Sales, Cost, Gross Profit"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 5,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 1. Deduplicate\n",
            "df_clean = df_raw.drop_duplicates().copy()\n",
            "df_clean = df_clean.drop_duplicates(subset=['Transaction_ID'], keep='first').copy()\n",
            "\n",
            "# 2. Drop corrupt dates\n",
            "df_clean = df_clean.dropna(subset=['Parsed_Date']).copy()\n",
            "\n",
            "# 3. Filter out negative amounts and quantities\n",
            "df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['Total_Amount'] > 0)].copy()\n",
            "\n",
            "# 4. Text standardization\n",
            "df_clean['Product_Category'] = df_clean['Product_Category'].fillna('Uncategorized').astype(str).str.strip().str.title()\n",
            "df_clean['Region'] = df_clean['Region'].astype(str).str.strip().str.title()\n",
            "df_clean['Customer_ID'] = df_clean['Customer_ID'].fillna('CUST-UNKNOWN').astype(str).str.strip()\n",
            "df_clean['Gender'] = df_clean['Gender'].fillna('Unknown').astype(str).str.strip()\n",
            "\n",
            "# 5. Financial recalculations\n",
            "df_clean['Quantity'] = df_clean['Quantity'].astype(int)\n",
            "df_clean['Price_Per_Unit'] = df_clean['Price_Per_Unit'].astype(float).round(2)\n",
            "df_clean['Discount_Pct'] = df_clean['Discount_Pct'].fillna(0.0).astype(float).clip(0.0, 0.90)\n",
            "df_clean['Gross_Sales'] = (df_clean['Quantity'] * df_clean['Price_Per_Unit']).round(2)\n",
            "df_clean['Discount_Amount'] = (df_clean['Gross_Sales'] * df_clean['Discount_Pct']).round(2)\n",
            "df_clean['Net_Sales'] = (df_clean['Gross_Sales'] - df_clean['Discount_Amount']).round(2)\n",
            "\n",
            "# COGS and Profit\n",
            "df_clean['Unit_Cost'] = (df_clean['Price_Per_Unit'] * 0.65).round(2)\n",
            "df_clean['Total_Cost'] = (df_clean['Quantity'] * df_clean['Unit_Cost']).round(2)\n",
            "df_clean['Gross_Profit'] = (df_clean['Net_Sales'] - df_clean['Total_Cost']).round(2)\n",
            "df_clean['Profit_Margin_Pct'] = ((df_clean['Gross_Profit'] / df_clean['Net_Sales']) * 100).round(2)\n",
            "df_clean['Date_Key'] = df_clean['Parsed_Date'].dt.strftime('%Y%m%d').astype(int)\n",
            "\n",
            "print(f'Cleaned dataset rows: {len(df_clean)}')\n",
            "print(f'Total Net Sales: ${df_clean[\"Net_Sales\"].sum():,.2f}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Star-Schema Dimensional Modeling\n",
            "We normalize the dataset into a high-performance Kimball Star Schema:\n",
            "- `Dim_Date`\n",
            "- `Dim_Product`\n",
            "- `Dim_Customer`\n",
            "- `Dim_Region`\n",
            "- `Fact_Sales`"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 6,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Dim_Product\n",
            "dim_product = df_clean[['Product_ID', 'Product_Name', 'Product_Category', 'Price_Per_Unit', 'Unit_Cost']].drop_duplicates(subset=['Product_ID']).reset_index(drop=True)\n",
            "dim_product['Product_Key'] = dim_product.index + 1\n",
            "\n",
            "# Dim_Customer\n",
            "dim_customer = df_clean[['Customer_ID', 'Gender', 'Age']].drop_duplicates(subset=['Customer_ID']).reset_index(drop=True)\n",
            "dim_customer['Customer_Key'] = dim_customer.index + 1\n",
            "\n",
            "# Dim_Region\n",
            "dim_region = df_clean[['Store_ID', 'City', 'State', 'Region']].drop_duplicates(subset=['Store_ID']).reset_index(drop=True)\n",
            "dim_region['Region_Key'] = dim_region.index + 1\n",
            "\n",
            "# Fact_Sales\n",
            "fact_sales = df_clean.merge(dim_product[['Product_Key', 'Product_ID']], on='Product_ID', how='left')\n",
            "fact_sales = fact_sales.merge(dim_customer[['Customer_Key', 'Customer_ID']], on='Customer_ID', how='left')\n",
            "fact_sales = fact_sales.merge(dim_region[['Region_Key', 'Store_ID']], on='Store_ID', how='left')\n",
            "fact_sales['Sales_Key'] = fact_sales.index + 1\n",
            "\n",
            "print('Dimensional model successfully generated.')\n",
            "print(f'Dim_Product: {len(dim_product)} rows')\n",
            "print(f'Dim_Customer: {len(dim_customer)} rows')\n",
            "print(f'Dim_Region: {len(dim_region)} rows')\n",
            "print(f'Fact_Sales: {len(fact_sales)} rows')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Top 10 Products & Monthly Trend Analysis"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 7,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Top 10 Products by Net Revenue\n",
            "top10 = df_clean.groupby('Product_Name')['Net_Sales'].sum().sort_values(ascending=False).head(10)\n",
            "print('TOP 10 PRODUCTS BY NET SALES:')\n",
            "display(top10.to_frame('Total_Net_Sales_USD'))\n",
            "\n",
            "# Monthly Trend\n",
            "df_clean['Year_Month'] = df_clean['Parsed_Date'].dt.to_period('M').astype(str)\n",
            "monthly = df_clean.groupby('Year_Month').agg(\n",
            "    Monthly_Revenue=('Net_Sales', 'sum'),\n",
            "    Total_Orders=('Transaction_ID', 'count'),\n",
            "    Units_Sold=('Quantity', 'sum')\n",
            ")\n",
            "print('\\nMONTHLY SALES TREND:')\n",
            "display(monthly.head(12))"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Executive KPI Dashboard Summary & Reconciliation"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 8,
        "metadata": {},
        "outputs": [],
        "source": [
            "total_sales = df_clean['Net_Sales'].sum()\n",
            "total_orders = len(df_clean)\n",
            "units_sold = df_clean['Quantity'].sum()\n",
            "aov = total_sales / total_orders\n",
            "total_profit = df_clean['Gross_Profit'].sum()\n",
            "profit_margin = (total_profit / total_sales) * 100\n",
            "\n",
            "print('====================================================')\n",
            "print('       EXECUTIVE KPI SUMMARY SCORECARD              ')\n",
            "print('====================================================')\n",
            "print(f'1. Total Net Sales        : ${total_sales:,.2f}')\n",
            "print(f'2. Total Orders (Volume)  : {total_orders:,}')\n",
            "print(f'3. Total Units Sold       : {units_sold:,}')\n",
            "print(f'4. Average Order Value    : ${aov:,.2f}')\n",
            "print(f'5. Gross Profit Margin    : {profit_margin:.2f}% (${total_profit:,.2f})')\n",
            "print('====================================================')"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Jupyter Notebook successfully created at: {NOTEBOOK_PATH}")
