"""
Automated Chart & Visualization Generator
Project 1: Sales Performance Dashboard
Generates publication-quality charts using Matplotlib and Seaborn:
1. 01_monthly_sales_trend.png (Monthly Revenue & 3-Month Moving Average)
2. 02_top_10_products.png (Top 10 Products by Net Sales with ranks)
3. 03_regional_sales_breakdown.png (Regional Revenue & Volume Share)
4. 04_category_profit_margin.png (Merchandise Category Revenue & Margin %)
5. 05_executive_sales_dashboard.png (Multi-panel Executive Master Scorecard)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
VISUALS_DIR = os.path.join(BASE_DIR, "visuals")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Load data
df_clean = pd.read_csv(os.path.join(PROCESSED_DIR, "cleaned_retail_sales.csv"))
df_fact = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_sales.csv"))
df_prod = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_product.csv"))
df_date = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_date.csv"))
df_region = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_region.csv"))

# Palette
PRIMARY_BLUE = "#1E40AF"
ACCENT_BLUE = "#3B82F6"
EMERALD_GREEN = "#10B981"
DARK_SLATE = "#1E293B"
CORAL_ACCENT = "#F43F5E"
LIGHT_GRAY = "#F1F5F9"

def generate_monthly_trend_chart():
    df_clean['Year_Month'] = pd.to_datetime(df_clean['Date']).dt.to_period('M').astype(str)
    monthly = df_clean.groupby('Year_Month')['Net_Sales'].sum().reset_index()
    monthly['3M_MA'] = monthly['Net_Sales'].rolling(window=3, min_periods=1).mean()

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    
    # Bar Chart for Monthly Net Sales
    bars = ax1.bar(monthly['Year_Month'], monthly['Net_Sales'], color=ACCENT_BLUE, alpha=0.75, width=0.6, label='Monthly Net Sales ($)')
    
    # Highlight peak month
    max_idx = monthly['Net_Sales'].idxmax()
    bars[max_idx].set_color(PRIMARY_BLUE)
    bars[max_idx].set_alpha(1.0)
    
    # Line chart for 3-Month Moving Average
    ax1.plot(monthly['Year_Month'], monthly['3M_MA'], color=CORAL_ACCENT, linewidth=2.5, marker='o', markersize=5, label='3-Month Moving Average')
    
    ax1.set_title("Monthly Net Sales Revenue & 3-Month Trend (2023 - 2024)", fontsize=15, fontweight='bold', pad=15, color=DARK_SLATE)
    ax1.set_xlabel("Year - Month", fontsize=11, fontweight='semibold', labelpad=10, color=DARK_SLATE)
    ax1.set_ylabel("Net Sales Revenue ($)", fontsize=11, fontweight='semibold', labelpad=10, color=DARK_SLATE)
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax1.tick_params(axis='x', rotation=45, labelsize=9)
    ax1.tick_params(axis='y', labelsize=9)
    
    # Legend
    ax1.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=10)
    
    # Annotate peak
    peak_val = monthly.loc[max_idx, 'Net_Sales']
    peak_date = monthly.loc[max_idx, 'Year_Month']
    ax1.annotate(f'Peak: ${peak_val:,.0f}\n({peak_date})', 
                 xy=(max_idx, peak_val), 
                 xytext=(max_idx - 2, peak_val + 3000),
                 arrowprops=dict(facecolor=DARK_SLATE, shrink=0.08, width=1, headwidth=6),
                 fontsize=9, fontweight='bold', color=DARK_SLATE,
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#F59E0B', alpha=0.9))
    
    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "01_monthly_sales_trend.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")

def generate_top_10_products_chart():
    merged = df_fact.merge(df_prod, on="Product_Key")
    top_10 = merged.groupby("Product_Name")["Net_Sales"].sum().sort_values(ascending=True).tail(10)
    
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    colors = [ACCENT_BLUE if i < 9 else PRIMARY_BLUE for i in range(len(top_10))]
    
    bars = ax.barh(top_10.index, top_10.values, color=colors, height=0.65, edgecolor='#CBD5E1')
    
    ax.set_title("Top 10 Products by Net Sales Revenue", fontsize=15, fontweight='bold', pad=15, color=DARK_SLATE)
    ax.set_xlabel("Total Net Sales ($)", fontsize=11, fontweight='semibold', labelpad=10, color=DARK_SLATE)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax.tick_params(axis='both', labelsize=10)
    
    # Value labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1500, bar.get_y() + bar.get_height() / 2, f"${width:,.0f}", 
                va='center', ha='left', fontsize=9, fontweight='bold', color=DARK_SLATE)
        
    ax.set_xlim(0, max(top_10.values) * 1.15)
    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "02_top_10_products.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")

def generate_regional_performance_chart():
    merged = df_fact.merge(df_region, on="Region_Key")
    reg_summary = merged.groupby("Region").agg(
        Net_Sales=('Net_Sales', 'sum'),
        Orders=('Sales_Key', 'count')
    ).sort_values("Net_Sales", ascending=False)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), dpi=300)
    
    # Donut chart
    palette = [PRIMARY_BLUE, ACCENT_BLUE, EMERALD_GREEN, "#F59E0B"]
    wedges, texts, autotexts = ax1.pie(
        reg_summary['Net_Sales'], 
        labels=reg_summary.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=palette,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
        pctdistance=0.75
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
        at.set_fontsize(10)
    ax1.set_title("Revenue Share by Region", fontsize=13, fontweight='bold', pad=10, color=DARK_SLATE)
    
    # Bar chart for Order Volume
    bars = ax2.bar(reg_summary.index, reg_summary['Orders'], color=palette, width=0.55, edgecolor='#CBD5E1')
    ax2.set_title("Order Volume by Region", fontsize=13, fontweight='bold', pad=10, color=DARK_SLATE)
    ax2.set_ylabel("Total Transactions", fontsize=10, fontweight='semibold', color=DARK_SLATE)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.tick_params(axis='both', labelsize=10)
    
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 30, f"{h:,}", ha='center', va='bottom', fontsize=9, fontweight='bold', color=DARK_SLATE)
        
    ax2.set_ylim(0, max(reg_summary['Orders']) * 1.15)
    
    plt.suptitle("Geographic Sales Performance & Territorial Distribution", fontsize=16, fontweight='bold', y=0.98, color=DARK_SLATE)
    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "03_regional_sales_breakdown.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")

def generate_category_margin_chart():
    merged = df_fact.merge(df_prod, on="Product_Key")
    cat_summary = merged.groupby("Product_Category").agg(
        Net_Sales=('Net_Sales', 'sum'),
        Gross_Profit=('Gross_Profit', 'sum')
    ).reset_index()
    cat_summary['Margin_Pct'] = (cat_summary['Gross_Profit'] / cat_summary['Net_Sales']) * 100
    cat_summary = cat_summary.sort_values("Net_Sales", ascending=False)
    
    fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)
    ax2 = ax1.twinx()
    
    x = np.arange(len(cat_summary))
    width = 0.5
    
    bars = ax1.bar(x, cat_summary['Net_Sales'], width=width, color=ACCENT_BLUE, alpha=0.85, label='Net Sales ($)')
    line = ax2.plot(x, cat_summary['Margin_Pct'], color=EMERALD_GREEN, linewidth=3, marker='s', markersize=8, label='Profit Margin (%)')
    
    ax1.set_title("Merchandise Category Revenue & Gross Margin %", fontsize=15, fontweight='bold', pad=15, color=DARK_SLATE)
    ax1.set_xticks(x)
    ax1.set_xticklabels(cat_summary['Product_Category'], rotation=15, ha='right', fontsize=10, fontweight='semibold', color=DARK_SLATE)
    ax1.set_ylabel("Net Sales Revenue ($)", fontsize=11, fontweight='semibold', color=DARK_SLATE)
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    
    ax2.set_ylabel("Gross Profit Margin (%)", fontsize=11, fontweight='semibold', color=EMERALD_GREEN)
    ax2.set_ylim(20, 36)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.1f}%'))
    ax2.grid(False)  # avoid overlapping gridlines
    
    # Value annotations on bars
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 5000, f"${h:,.0f}", ha='center', va='bottom', fontsize=9, fontweight='bold', color=DARK_SLATE)
        
    for i, txt in enumerate(cat_summary['Margin_Pct']):
        ax2.annotate(f"{txt:.1f}%", (x[i], txt), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9, fontweight='bold', color=EMERALD_GREEN)
        
    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', frameon=True, facecolor='white', edgecolor='#E2E8F0')
    
    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "04_category_profit_margin.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")

def generate_master_dashboard_graphic():
    fig = plt.figure(figsize=(16, 11), dpi=250)
    fig.patch.set_facecolor('#F8FAFC')
    
    # Grid specification
    gs = fig.add_gridspec(3, 3, height_ratios=[0.5, 1.2, 1.2], hspace=0.38, wspace=0.25)
    
    # Header Banner
    ax_banner = fig.add_subplot(gs[0, :])
    ax_banner.set_facecolor('#1E293B')
    ax_banner.axis('off')
    
    # Title & Subtitle inside banner
    ax_banner.text(0.02, 0.70, "EXECUTIVE SALES PERFORMANCE DASHBOARD", fontsize=18, fontweight='bold', color='white', va='center')
    ax_banner.text(0.02, 0.32, "Enterprise Retail & E-Commerce Operations Scorecard | Reconciled Kaggle Pipeline", fontsize=11, color='#94A3B8', va='center')
    
    # KPI 1 to 5 boxes inside banner
    kpis = [
        ("TOTAL NET REVENUE", "$1,073,809", "#38BDF8"),
        ("TOTAL ORDERS", "4,927", "#4ADE80"),
        ("UNITS SOLD", "11,161", "#F472B6"),
        ("AVG ORDER VALUE", "$217.94", "#FBBF24"),
        ("PROFIT MARGIN", "30.74%", "#34D399")
    ]
    for i, (title, val, col) in enumerate(kpis):
        x_pos = 0.42 + i * 0.115
        ax_banner.text(x_pos, 0.68, title, fontsize=7.5, fontweight='bold', color='#94A3B8', ha='center')
        ax_banner.text(x_pos, 0.30, val, fontsize=12, fontweight='bold', color=col, ha='center')
        
    # Visual 1: Monthly Trend (row 1, cols 0 & 1)
    ax_trend = fig.add_subplot(gs[1, 0:2])
    ax_trend.set_facecolor('white')
    df_clean['Year_Month'] = pd.to_datetime(df_clean['Date']).dt.to_period('M').astype(str)
    monthly = df_clean.groupby('Year_Month')['Net_Sales'].sum().reset_index()
    monthly['3M_MA'] = monthly['Net_Sales'].rolling(window=3, min_periods=1).mean()
    ax_trend.bar(monthly['Year_Month'], monthly['Net_Sales'], color=ACCENT_BLUE, alpha=0.75, width=0.6, label='Net Sales')
    ax_trend.plot(monthly['Year_Month'], monthly['3M_MA'], color=CORAL_ACCENT, linewidth=2, marker='o', markersize=4, label='3M Avg')
    ax_trend.set_title("Monthly Net Sales Trend ($) with 3-Month Moving Average", fontsize=11, fontweight='bold', color=DARK_SLATE, pad=8)
    ax_trend.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax_trend.tick_params(axis='x', rotation=45, labelsize=7.5)
    ax_trend.tick_params(axis='y', labelsize=8)
    ax_trend.legend(fontsize=8, loc='upper left')
    
    # Visual 2: Regional Share Donut (row 1, col 2)
    ax_donut = fig.add_subplot(gs[1, 2])
    ax_donut.set_facecolor('white')
    merged_reg = df_fact.merge(df_region, on="Region_Key")
    reg_sales = merged_reg.groupby("Region")["Net_Sales"].sum()
    palette = [PRIMARY_BLUE, ACCENT_BLUE, EMERALD_GREEN, "#F59E0B"]
    wedges, texts, autotexts = ax_donut.pie(
        reg_sales, labels=reg_sales.index, autopct='%1.1f%%', startangle=140, colors=palette,
        wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2), pctdistance=0.75
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
        at.set_fontsize(8)
    ax_donut.set_title("Revenue Share by Region", fontsize=11, fontweight='bold', color=DARK_SLATE, pad=8)
    
    # Visual 3: Top 10 Products (row 2, cols 0 & 1)
    ax_top = fig.add_subplot(gs[2, 0:2])
    ax_top.set_facecolor('white')
    merged_prod = df_fact.merge(df_prod, on="Product_Key")
    top_10 = merged_prod.groupby("Product_Name")["Net_Sales"].sum().sort_values(ascending=True).tail(10)
    bars = ax_top.barh(top_10.index, top_10.values, color=ACCENT_BLUE, height=0.65, edgecolor='#CBD5E1')
    bars[-1].set_color(PRIMARY_BLUE)
    ax_top.set_title("Top 10 Products by Net Revenue", fontsize=11, fontweight='bold', color=DARK_SLATE, pad=8)
    ax_top.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax_top.tick_params(axis='both', labelsize=8)
    for bar in bars:
        w = bar.get_width()
        ax_top.text(w + 1000, bar.get_y() + bar.get_height() / 2, f"${w:,.0f}", va='center', ha='left', fontsize=7.5, fontweight='bold', color=DARK_SLATE)
    ax_top.set_xlim(0, max(top_10.values) * 1.18)
    
    # Visual 4: Category Breakdown (row 2, col 2)
    ax_cat = fig.add_subplot(gs[2, 2])
    ax_cat.set_facecolor('white')
    cat_sales = merged_prod.groupby("Product_Category")["Net_Sales"].sum().sort_values(ascending=True)
    ax_cat.barh(cat_sales.index, cat_sales.values, color=EMERALD_GREEN, height=0.55, edgecolor='#CBD5E1')
    ax_cat.set_title("Sales by Product Category", fontsize=11, fontweight='bold', color=DARK_SLATE, pad=8)
    ax_cat.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax_cat.tick_params(axis='both', labelsize=8)
    for p in ax_cat.patches:
        ax_cat.annotate(f"${p.get_width():,.0f}", (p.get_width() + 4000, p.get_y() + 0.15), fontsize=7.5, fontweight='bold', color=DARK_SLATE)
    ax_cat.set_xlim(0, max(cat_sales.values) * 1.25)
    
    out_path = os.path.join(VISUALS_DIR, "05_executive_sales_dashboard.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

def main():
    print("=" * 60)
    print("GENERATING DASHBOARD GRAPHS & VISUALIZATIONS")
    print("=" * 60)
    generate_monthly_trend_chart()
    generate_top_10_products_chart()
    generate_regional_performance_chart()
    generate_category_margin_chart()
    generate_master_dashboard_graphic()
    print("All charts generated successfully.")

if __name__ == "__main__":
    main()
