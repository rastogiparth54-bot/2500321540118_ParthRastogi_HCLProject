# Power BI Implementation & Dashboard Build Guide
**Project 1: Sales Performance Dashboard**

This guide provides end-to-end, click-by-click instructions to recreate the industry-grade **Sales Performance Dashboard** in Power BI Desktop using the cleaned CSV datasets and DAX measure library included in this repository.

---

## Step 1: Open Power BI Desktop & Load Cleaned Data

1. Launch **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to the `data/processed/` directory and import the following 5 CSV files:
   - `fact_sales.csv`
   - `dim_date.csv`
   - `dim_product.csv`
   - `dim_customer.csv`
   - `dim_region.csv`
4. In the Power Query Navigator window, select **Transform Data** to inspect types:
   - Verify `Date_Key`, `Product_Key`, `Customer_Key`, `Region_Key`, and `Sales_Key` are formatted as **Whole Number**.
   - Verify `Gross_Sales`, `Discount_Amount`, `Net_Sales`, `Total_Cost`, and `Gross_Profit` are formatted as **Fixed Decimal Number / Currency**.
   - Verify `Discount_Pct` and `Profit_Margin_Pct` are formatted as **Decimal Number**.
5. Click **Close & Apply**.

---

## Step 2: Configure the Star Schema Relationships

Navigate to the **Model View** (icon on the left navigation panel):
Ensure the following 1-to-Many (`1:*`) relationships are configured with **Single** cross-filter direction:

| From Table (Dimension) | From Column (Primary Key) | To Table (Fact) | To Column (Foreign Key) | Cardinality | Cross Filter |
|---|---|---|---|---|---|
| `Dim_Date` | `Date_Key` | `Fact_Sales` | `Date_Key` | 1 to Many (1:*) | Single |
| `Dim_Product` | `Product_Key` | `Fact_Sales` | `Product_Key` | 1 to Many (1:*) | Single |
| `Dim_Customer` | `Customer_Key` | `Fact_Sales` | `Customer_Key` | 1 to Many (1:*) | Single |
| `Dim_Region` | `Region_Key` | `Fact_Sales` | `Region_Key` | 1 to Many (1:*) | Single |

*Mark `Dim_Date` as a Date Table:*
- Right-click `Dim_Date` -> **Mark as Date Table** -> Select `Full_Date`.

---

## Step 3: Create Central DAX Measures Table

1. On the **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Open `power_bi/dax_measures.txt`.
4. Right-click `_Measures` -> **New Measure**, and paste each measure from `dax_measures.txt`:
   - `Total Net Sales`
   - `Total Orders`
   - `Total Units Sold`
   - `Average Order Value (AOV)`
   - `Gross Profit Margin %`
   - `Sales MoM Growth %`
   - `Sales YoY Growth %`
   - `Sales 3M Rolling Avg`
   - `Product Rank by Revenue`
   - `Is Top 10 Product`
   - `KPI Status Indicator`
5. Delete the default blank column in `_Measures` so it becomes a dedicated measure group icon.

---

## Step 4: Build Canvas Visuals & Layout

### 1. Canvas Settings
- Set canvas size to **16:9** (1280 x 720 px).
- Canvas background: `#F8FAFC`, transparency 0%.

### 2. Header
- Insert a text box at the top:
  - Text: **Executive Retail Sales Performance Dashboard** (Bold, 20pt)
  - Subtitle: *Retail & E-commerce Operations Scorecard* (10pt, grey)

### 3. Add 5 KPI Cards (Top Banner)
- Add 5 **Card** or **New Card (Preview)** visuals across the top:
  - **Card 1**: `[Total Net Sales]` -> Format as Currency `$#,##0.00`
  - **Card 2**: `[Total Orders]` -> Format as Whole Number `#,##0`
  - **Card 3**: `[Total Units Sold]` -> Format as Whole Number `#,##0`
  - **Card 4**: `[Average Order Value (AOV)]` -> Format as Currency `$#,##0.00`
  - **Card 5**: `[Gross Profit Margin %]` -> Format as Percentage `0.00%`

### 4. Add 3 Slicers
- **Slicer 1 (Date)**: `Dim_Date[Year]`, `Dim_Date[Quarter]`, `Dim_Date[Month_Name]`
- **Slicer 2 (Region)**: `Dim_Region[Region]` (Values: Central, East, South, West)
- **Slicer 3 (Product Category)**: `Dim_Product[Product_Category]`

### 5. Main Trend Chart
- Visual: **Line and Clustered Column Chart**
- X-axis: `Dim_Date[Month_Year]` (sort by `Year`, `Month_Num`)
- Column Y-axis: `[Total Net Sales]`
- Line Y-axis: `[Sales 3M Rolling Avg]`

### 6. Top 10 Products Chart
- Visual: **Clustered Bar Chart**
- Y-axis: `Dim_Product[Product_Name]`
- X-axis: `[Total Net Sales]`
- Visual Filter: Set `[Is Top 10 Product]` is 1 (or Top N by `Total Net Sales` = 10).

### 7. Regional Performance Visual
- Visual: **Donut Chart**
- Legend: `Dim_Region[Region]`
- Values: `[Total Net Sales]`

---

## Step 5: Test & Validate

1. Click on **Region Slicer**: Select `West`. Notice how all 5 KPI cards, the monthly trend, and product rankings adjust dynamically.
2. Verify Total Net Sales matches `$1,073,808.62` when all filters are cleared (Reconciliation target met within 0.000%).
3. Save the report as `Sales_Performance_Dashboard.pbix`.
