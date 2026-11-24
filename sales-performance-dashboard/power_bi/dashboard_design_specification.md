# Executive Sales Performance Dashboard: Design Specification

## 1. Visual Canvas Overview
- **Resolution**: 16:9 Standard High-Definition Canvas (1920 x 1080 px or 1280 x 720 px)
- **Design Theme**: Modern Executive Analytics (Dark Slate / Corporate Blue & Emerald Accents)
- **Primary Color Palette**:
  - Primary Brand Dark: `#1E293B` (Slate 800)
  - Secondary Brand Blue: `#2563EB` (Royal Blue)
  - Accent / Positive Growth: `#10B981` (Emerald Green)
  - Accent / Negative Variance: `#EF4444` (Coral Red)
  - Neutral Background: `#F8FAFC` (Off-white / Slate 50)
  - Visual Card Background: `#FFFFFF` (White with subtle drop-shadow)

---

## 2. Header & Global Navigation Strip (Top: 0 to 90 px)
- **Title Block**:
  - Main Title: **Executive Retail Sales Performance Dashboard** (Segoe UI Semibold, 22pt, `#1E293B`)
  - Subtitle: *Enterprise Financial & Operational Scorecard | Automated Kaggle Pipeline* (Segoe UI, 11pt, `#64748B`)
- **Dynamic Context Header**:
  - Displays selected slicer filters dynamically using `[Selected Time Horizon Label]` and `[Selected Region Label]`.
- **Last Refreshed Badge**: Displays data pipeline execution timestamp and benchmark validation tag.

---

## 3. Executive KPI Scorecard Strip (Top: 100 to 220 px)
Contains **5 Interactive KPI Cards** satisfying the acceptance criteria:

| Card # | KPI Name | Primary DAX Measure | Secondary / Context Measure | Target / Status Indicator |
|---|---|---|---|---|
| **Card 1** | **Total Net Revenue** | `[Total Net Sales]` ($1,073,808.62) | `[Sales MoM Growth %]` | `[KPI Status Indicator]` (Green on track) |
| **Card 2** | **Total Sales Volume** | `[Total Orders]` (4,927 Orders) | `[Average Units per Order]` (2.27 items/order) | Target vs Prior Year (SPLY) |
| **Card 3** | **Units Sold** | `[Total Units Sold]` (11,161 Units) | `[Total Discount Amount]` ($70,383.50) | Inventory Turn Indicator |
| **Card 4** | **Average Order Value** | `[Average Order Value (AOV)]` ($217.94) | `[Effective Discount Rate %]` (6.15%) | Industry Retail Benchmark ($200) |
| **Card 5** | **Gross Profit Margin** | `[Gross Profit Margin %]` (30.74%) | `[Total Gross Profit]` ($330,114.20) | Target Margin Threshold (>= 28.0%) |

---

## 4. Multi-Dimensional Interactive Slicers Bar (Left or Horizontal Ribbon)
Satisfies acceptance criteria: **at least 3 slicers** with seamless cross-filtering:

1. **Slicer 1: Temporal Horizon (Date)**
   - Type: Hierarchy Dropdown / Relative Date Slider
   - Fields: `Dim_Date[Year]` -> `Dim_Date[Quarter]` -> `Dim_Date[Month_Name]`
   - Range: Full 2-year calendar (2023 - 2024).

2. **Slicer 2: Geographic Territory (Region & Store)**
   - Type: Tile / Multi-Select Dropdown
   - Fields: `Dim_Region[Region]` (East, Central, South, West)
   - Drill-down: `Dim_Region[Region]` -> `Dim_Region[State]` -> `Dim_Region[City]` -> `Dim_Region[Store_ID]`.

3. **Slicer 3: Product Category**
   - Type: Horizontal Button Strip / Dropdown
   - Fields: `Dim_Product[Product_Category]` (Electronics, Clothing, Home & Kitchen, Beauty & Personal Care, Sports & Outdoors).

---

## 5. Main Analytics Visual Layout

### Visual 1: Monthly Sales Trend & Momentum (Middle Left)
- **Visual Type**: Clustered Column & Line Chart (Combo Chart)
- **X-Axis**: `Dim_Date[Month_Year]` (Sorted chronologically by `Dim_Date[Year]`, `Dim_Date[Month_Num]`)
- **Column Y-Axis**: `[Total Net Sales]` ($) (Fill Color: `#2563EB`)
- **Line Y-Axis**: `[Sales 3M Rolling Avg]` and `[Sales MoM Growth %]`
- **Features**: Data labels enabled on high-point peaks, tooltip showing `[Sales MoM Variance]` and `[Sales Prior Month]`.

### Visual 2: Top 10 Products by Net Revenue (Middle Right)
- **Visual Type**: Horizontal Clustered Bar Chart
- **Y-Axis**: `Dim_Product[Product_Name]`
- **X-Axis**: `[Total Net Sales]`
- **Filters**: Visual-level filter `[Product Rank by Revenue] <= 10` (or `[Is Top 10 Product] = 1`)
- **Data Labels**: Positioned outside end, formatted as `$#,##0`
- **Tooltip**: `[Product_Category]`, `[Units Sold]`, `[Gross Profit Margin %]`, `[Product Rank by Revenue]`.

### Visual 3: Regional Sales Share & Store Hierarchy (Bottom Left)
- **Visual Type**: Donut Chart / Decomposition Tree / Filled Shape Map
- **Legend / Category**: `Dim_Region[Region]`
- **Values**: `[Total Net Sales]`
- **Drill-down Action**: Click on a Region slice to filter the entire dashboard and drill down into individual retail store locations (`Store_ID`).

### Visual 4: Product Category Financial Matrix (Bottom Right)
- **Visual Type**: Power BI Matrix Visual with conditional data bars
- **Rows**: `Dim_Product[Product_Category]`
- **Values**:
  - `[Total Orders]`
  - `[Total Units Sold]`
  - `[Total Net Sales]`
  - `[Share of Total Sales %]` (Rendered as inline data bars)
  - `[Gross Profit Margin %]` (Conditional color formatting: Green >= 30%, Amber 25-30%, Red < 25%)

---

## 6. Key Test Cases Verification in Dashboard
1. **Null / Duplicate Rows**: Resolved in Python ETL before ingestion; Fact table contains zero null foreign keys and zero duplicate transaction IDs.
2. **Negative Amounts**: Cleaned and filtered; no negative sales skewing totals; returns tracked separately.
3. **Date Format Errors**: Fully normalized into conformed integer `Date_Key` (`YYYYMMDD`) joining cleanly to `Dim_Date`.
4. **Region Slicer**: Interactive cross-filtering verified across all 4 regions (East, West, Central, South).
