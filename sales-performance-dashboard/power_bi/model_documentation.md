# Dimensional Data Model Documentation
**Kimball Star Schema Architecture for Sales Performance Dashboard**

## 1. Schema Paradigm
This data model strictly adheres to Ralph Kimball's dimensional modeling standard for enterprise data warehouses and business intelligence systems. It decouples high-volume additive transactional events (Facts) from descriptive contextual hierarchies (Dimensions).

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_SALES : "filters (Date_Key)"
    DIM_PRODUCT ||--o{ FACT_SALES : "filters (Product_Key)"
    DIM_CUSTOMER ||--o{ FACT_SALES : "filters (Customer_Key)"
    DIM_REGION ||--o{ FACT_SALES : "filters (Region_Key)"

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

## 2. Granularity
The atomic grain of `FACT_SALES` is **one individual line-item transaction** placed by a customer for a distinct product at a specific retail store location on a specific date.

## 3. Dimension Specifications

### `DIM_DATE` (Conformed Date Dimension)
- **Role**: Conformed role-playing time intelligence dimension.
- **Grain**: One record per calendar day spanning 2023-01-01 through 2024-12-31 (731 days).
- **Surrogate Key**: `Date_Key` integer formatted as `YYYYMMDD` (e.g., `20230514`).
- **Attributes**: Supports fiscal and calendar quarters, month numbers for sorting, and weekend flags.

### `DIM_PRODUCT` (Catalog Dimension)
- **Role**: Descriptive categorization of merchandise inventory.
- **Grain**: One record per unique SKU / Product ID (34 distinct product SKUs).
- **Attributes**: Product Name, Category, Baseline Catalog Unit Price, Unit COGS.

### `DIM_CUSTOMER` (Demographics Dimension)
- **Role**: Customer segmentation and purchasing behavior analysis.
- **Grain**: One record per unique Customer ID (1,189 unique customers).
- **Attributes**: Gender, Age, Age Group Cohort (`18-24`, `25-34`, `35-49`, `50-64`, `65+`).

### `DIM_REGION` (Territory Dimension)
- **Role**: Geographic hierarchy for physical store networks.
- **Grain**: One record per retail store branch (10 retail locations).
- **Hierarchy**: `Region` -> `State` -> `City` -> `Store_ID`.

---

## 4. Cardinality & Cross-Filtering Strategy
- All dimension-to-fact relationships are **1-to-Many (`1:*`)**.
- Cross-filter direction is strictly **Single Direction** (`Dimension -> Fact`).
- Bi-directional cross-filtering is avoided to eliminate query ambiguity, circular paths, and performance degradation in high-volume enterprise reporting.
