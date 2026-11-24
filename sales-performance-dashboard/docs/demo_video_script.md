# Video Demonstration Script & Presentation Guide
**Project 1: Sales Performance Dashboard**
**Duration**: 5 Minutes (300 Seconds)
**Role**: Senior BI & Data Analytics Engineer / Analytics Lead
**Target Audience**: Executive Stakeholders, Technical Evaluators, Hiring Managers

---

## Video Outline & Time Breakdown

```
[00:00 - 00:45] Phase 1: Executive Overview & Problem Context
[00:45 - 01:30] Phase 2: Python Data Engineering & Anomaly Remediation
[01:30 - 02:30] Phase 3: Oracle Star Schema, SQL Window Functions & Analytics Views
[02:30 - 04:00] Phase 4: Power BI Dashboard Walkthrough (5 KPIs, Slicers, Visuals)
[04:00 - 04:45] Phase 5: Reconciled Acceptance Verification & Commercial Insights
[04:45 - 05:00] Phase 6: Conclusion & Repository Deliverables
```

---

## Detailed Scene-by-Scene Script

### [00:00 - 00:45] Phase 1: Executive Overview & Problem Statement
- **Visual**: Title Slide showing project title, architecture diagram, and executive scorecard. Presenter appears in picture-in-picture.
- **Presenter (Speaking)**:
  > *"Hello everyone! Welcome to the walkthrough of the Sales Performance Dashboard project for retail and e-commerce operations. In modern enterprise retail, leadership frequently struggles with fragmented sales figures across channels, inconsistent date standards, and dirty data containing duplicate orders and negative amounts.*
  >
  > *In this project, I engineered an end-to-end analytics solution: ingesting raw retail data, automating data quality remediation in Python, building a high-performance Star Schema in Oracle Database using advanced window functions, and delivering an executive Power BI dashboard with 5 core KPIs and dynamic 3-way slicing. Crucially, all sales metrics reconcile across CSV, Oracle, and Power BI within a strict 0.00% variance. Let's look at the pipeline."*

---

### [00:45 - 01:30] Phase 2: Python Data Engineering & Anomaly Cleaning
- **Visual**: Screen recording of VS Code showing `python/data_cleaning.py` and the Jupyter Notebook `eda_and_cleaning.ipynb`. Highlight test cases being tested in terminal.
- **Presenter (Speaking)**:
  > *"Starting with data ingestion, our raw retail dataset contained 5,055 records with deliberate enterprise anomalies. Here in `data_cleaning.py`, we execute a multi-stage audit.*
  >
  > *First, we resolve 40 exact duplicate rows and 15 secondary key collisions. Next, our multi-format parser standardizes mixed ISO, British, and US date strings while dropping unrecoverable corrupt entries like 'February 31st'.*
  >
  > *We also isolate 50 negative amount and quantity anomalies, separating returns from positive sales transactions to protect revenue integrity. Finally, we recalculate mathematical consistency across gross sales, discounts, net sales, and profit margin. The script outputs conformed dimensions: Dim Date, Dim Product, Dim Customer, Dim Region, and Fact Sales, yielding exactly 4,927 verified records."*

---

### [01:30 - 02:30] Phase 3: Oracle SQL Architecture & Window Functions
- **Visual**: Screen switch to Oracle SQL Developer / DBeaver showing `01_oracle_ddl_star_schema.sql` and `03_oracle_analytics_queries.sql`. Run the query and show the results grid.
- **Presenter (Speaking)**:
  > *"Moving to the database tier, our Oracle DDL implements a Kimball star schema with surrogate integer keys, primary and foreign key constraints, and bitmap indexes for rapid aggregation.*
  >
  > *In `03_oracle_analytics_queries.sql`, we leverage production-grade analytical window functions. Notice Query 2, where we use `DENSE_RANK() OVER` to rank our Top 10 revenue-generating products overall and by merchandise category.*
  >
  > *In Query 3, we analyze our monthly time series using `LAG()` to calculate Month-over-Month growth in dollars and percentages, `SUM() OVER(PARTITION BY YEAR)` for cumulative Year-to-Date revenue, and a 3-month moving average. We also deploy `NTILE(4)` to segment customer lifetime spend into four VIP quartiles, and package these into five reusable Oracle BI analytics views for direct reporting."*

---

### [02:30 - 04:00] Phase 4: Power BI Executive Dashboard Walkthrough
- **Visual**: Full-screen Power BI Dashboard. Cursor interacts with visuals, slicers, and tooltips.
- **Presenter (Speaking)**:
  > *"Now let's examine the executive Power BI dashboard. At the very top, we feature our five primary KPI cards:*
  > 1. *Total Net Revenue: $1,073,808.62*
  > 2. *Total Sales Volume: 4,927 Orders*
  > 3. *Total Units Sold: 11,161 items*
  > 4. *Average Order Value: $217.94*
  > 5. *Gross Profit Margin: 30.74%, totaling over $330,000 in gross margin.*
  >
  > *On the left, we provide three interactive slicers: Date Hierarchy, Geographic Territory, and Product Category. Watch what happens when I filter by the 'West' region: all five KPI cards, the monthly trendline, and product rankings adjust instantaneously. We can drill down from West to California, to Los Angeles, down to individual Store 107.*
  >
  > *In the center, our Combo Chart plots monthly net sales alongside a 3-month moving average, clearly illustrating the seasonal Q4 holiday surges in November and December. To its right, our Top 10 Product bar chart highlights the Smartphone 5G Pro as our #1 revenue driver at $138,500, followed by the 4K Smart TV and Robot Vacuum Cleaner."*

---

### [04:00 - 04:45] Phase 5: Automated Verification & Business Insights
- **Visual**: Terminal executing `python python/verify_reconciliation.py`. Display PASS verification logs and executive insights document.
- **Presenter (Speaking)**:
  > *"To ensure industry-grade reliability, we run our automated audit script: `verify_reconciliation.py`. As you see on screen, it verifies:
  > - Exact row counts across CSV, Oracle, and Power BI at 4,927 records.
  > - Total sales reconciliation discrepancy is exactly $0.00, easily exceeding the 0.1% tolerance threshold.
  > - Top 10 product rankings and 5 KPIs match with 100% precision.*
  >
  > *Strategically, this analysis reveals that Electronics drives 35% of total sales, but high-ticket items carry slightly lower margins. We recommend bundling high-margin accessories to lift AOV above $240 and allocating 40% of Q4 inventory to the West region to capture peak demand."*

---

### [04:45 - 05:00] Phase 6: Wrap-up & Project Deliverables
- **Visual**: VS Code project tree showing complete GitHub repository folder structure and the packaged ZIP file.
- **Presenter (Speaking)**:
  > *"In summary, this project delivers a complete enterprise solution: raw and processed datasets, Python ETL pipeline and Jupyter notebook, Oracle DDL, queries, and views, Power BI DAX formulas and templates, and comprehensive documentation. All assets are packaged and available in this repository. Thank you for watching!"*
