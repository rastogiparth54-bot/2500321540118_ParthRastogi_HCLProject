# Problem Statement & Executive KPI Definitions
**Project 1: Sales Performance Dashboard**
**Domain**: Retail & E-Commerce Operations

---

## 1. Executive Problem Statement
In modern omnichannel retail and e-commerce enterprises, sales data is collected from disparate transactional sources (point-of-sale registers, mobile apps, web storefronts, third-party marketplaces). These raw transactional logs routinely suffer from data hygiene issues, including duplicate transaction entries, corrupted date formats, missing customer demographics, and anomalous negative values arising from unclassified returns or clerical errors.

Without a standardized data engineering pipeline, analytical models produce conflicting revenue figures across business departments. Executive leaders lack a unified "single version of truth" to evaluate merchandise performance, seasonal revenue momentum, and regional store contributions.

### Strategic Business Goals
1. **Unify & Reconcile Data**: Ingest raw retail data, resolve data quality defects, and establish a mathematically reconciled star schema across Python, Oracle SQL, and Power BI with an error tolerance under **0.1%**.
2. **Drive Product Strategy**: Identify the Top 10 revenue-generating products and track margin health across merchandise categories.
3. **Analyze Regional Momentum**: Evaluate geographical territory and store performance to optimize inventory allocation and regional marketing spend.
4. **Deliver Executive Visibility**: Equip leadership with an interactive Power BI dashboard featuring dynamic KPI scorecards, multi-dimensional slicers, and monthly time-series intelligence.

---

## 2. Core Business Questions Answered
- What is our total net sales revenue, total volume of orders, and average transaction value (AOV)?
- Which individual products drive 80% of our enterprise gross profit, and which items are underperforming?
- How is revenue trending month-over-month (MoM) and year-over-year (YoY)? Are sales experiencing seasonal peaks?
- Which geographic regions (East, West, Central, South) demonstrate the highest average basket sizes and profitability?
- What are the customer demographic purchasing patterns across age cohorts and genders?

---

## 3. Executive KPI Definitions & Business Logic

### Primary Scorecard KPIs (Minimum 5 Met)

#### KPI 1: Total Net Sales Revenue ($)
- **Definition**: Total monetary revenue realized from all customer orders after deducting applied discounts.
- **Formula**:
  $$\text{Net Sales} = \sum (\text{Quantity} \times \text{Price Per Unit}) - \sum \text{Discount Amount}$$
- **Benchmark / Target**: Matches verified data source at **$1,073,808.62** (0.00% variance).
- **Measurement Frequency**: Daily / Monthly / Annual roll-up.

#### KPI 2: Total Sales Volume (Orders)
- **Definition**: Total count of unique completed customer sales transactions.
- **Formula**:
  $$\text{Total Orders} = \text{COUNT}(\text{Transaction\_ID})$$
- **Benchmark / Target**: **4,927 Orders**.
- **Role**: Operational throughput and order frequency baseline.

#### KPI 3: Total Units Sold
- **Definition**: Total physical volume of inventory units purchased by customers.
- **Formula**:
  $$\text{Total Units Sold} = \sum \text{Quantity}$$
- **Benchmark / Target**: **11,161 Units**.
- **Role**: Supply chain demand forecasting and inventory velocity.

#### KPI 4: Average Order Value (AOV)
- **Definition**: Average net monetary amount spent by a customer per sales transaction.
- **Formula**:
  $$\text{AOV} = \frac{\text{Total Net Sales}}{\text{Total Orders}}$$
- **Benchmark / Target**: **$217.94**.
- **Role**: Customer basket monetization and promotional effectiveness indicator.

#### KPI 5: Gross Profit Margin (%)
- **Definition**: Percentage of net sales revenue retained after accounting for the Cost of Goods Sold (COGS).
- **Formula**:
  $$\text{Gross Profit Margin} = \frac{\text{Total Net Sales} - \text{Total Cost}}{\text{Total Net Sales}} \times 100$$
- **Benchmark / Target**: **30.74%** ($330,114.20 Gross Profit).
- **Role**: Bottom-line pricing health and merchandise profitability.

---

### Secondary Operational KPIs

#### KPI 6: Month-over-Month (MoM) Growth (%)
- **Definition**: Percentage change in net sales revenue compared to the immediate prior calendar month.
- **Formula**:
  $$\text{MoM Growth \%} = \frac{\text{Net Sales}_{t} - \text{Net Sales}_{t-1}}{\text{Net Sales}_{t-1}} \times 100$$
- **Role**: Short-term commercial momentum and volatility tracking.

#### KPI 7: Effective Discount Rate (%)
- **Definition**: Total markdown dollars granted as a proportion of total gross sales value.
- **Formula**:
  $$\text{Effective Discount \%} = \frac{\text{Total Discount Amount}}{\text{Total Gross Sales}} \times 100$$
- **Benchmark / Actual**: **6.15%** ($70,383.50 total discounts on $1,144,192.12 gross sales).
- **Role**: Promotional discipline and margin leakage audit.

#### KPI 8: Units per Transaction (UPT)
- **Definition**: Average number of distinct product units purchased per customer checkout.
- **Formula**:
  $$\text{UPT} = \frac{\text{Total Units Sold}}{\text{Total Orders}} = \frac{11,161}{4,927} = 2.27 \text{ items/order}$$
- **Role**: Cross-selling and up-selling effectiveness.
