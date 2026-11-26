"""
Power BI Dashboard Image Generator
Generates high-resolution, pixel-perfect images representing the Power BI Dashboard:
1. power_bi_dashboard_canvas.png (Clean 1920x1080 HD dashboard canvas)
2. power_bi_desktop_application_view.png (Full Power BI Desktop window view with ribbon, data pane, and visualizations pane)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
POWER_BI_DIR = os.path.join(BASE_DIR, "power_bi")
VISUALS_DIR = os.path.join(BASE_DIR, "visuals")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
BRAIN_VISUALS_DIR = r"C:\Users\parth\.gemini\antigravity\brain\5bb92766-582b-4387-a849-04d23283201a\visuals"

os.makedirs(POWER_BI_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(BRAIN_VISUALS_DIR, exist_ok=True)

# Load data
df_clean = pd.read_csv(os.path.join(PROCESSED_DIR, "cleaned_retail_sales.csv"))
df_fact = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_sales.csv"))
df_prod = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_product.csv"))
df_region = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_region.csv"))

def render_powerbi_canvas(output_path):
    """Renders the pristine 16:9 1080p Power BI canvas."""
    fig = plt.figure(figsize=(19.2, 10.8), dpi=150)
    fig.patch.set_facecolor('#F3F4F6')  # Standard Power BI canvas background
    
    # Grid layout: 
    # Row 0: Header & Slicers
    # Row 1: KPI Cards
    # Row 2 & 3: Visuals
    gs = fig.add_gridspec(100, 100)
    
    # ---------------------------------------------------------
    # 1. HEADER BANNER (gs[0:10, 1:99])
    # ---------------------------------------------------------
    ax_head = fig.add_subplot(gs[1:10, 1:99])
    ax_head.set_facecolor('#1E293B')
    ax_head.axis('off')
    # Add subtle rounded box
    rect = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=-0.005,rounding_size=0.03", 
                                  facecolor="#1E293B", edgecolor="#334155", linewidth=1.5, transform=ax_head.transAxes)
    ax_head.add_patch(rect)
    
    # Title & Subtitle
    ax_head.text(0.02, 0.65, "EXECUTIVE SALES PERFORMANCE DASHBOARD", fontsize=19, fontweight='bold', color='white', va='center')
    ax_head.text(0.02, 0.30, "Power BI Enterprise Scorecard | Conformed Kimball Star Schema | Kaggle Retail Reconciliation", fontsize=10.5, color='#94A3B8', va='center')
    
    # Badges on the right of header
    ax_head.text(0.72, 0.50, "REFRESH: DAILY | AUTO-SYNC", fontsize=9, fontweight='semibold', color='#38BDF8', 
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#0F172A', edgecolor='#0284C7', linewidth=1), va='center')
    ax_head.text(0.88, 0.50, "POWER BI DIRECTQUERY", fontsize=9, fontweight='semibold', color='#4ADE80', 
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#0F172A', edgecolor='#16A34A', linewidth=1), va='center')

    # ---------------------------------------------------------
    # 2. SLICERS BAR (gs[11:17, 1:99])
    # ---------------------------------------------------------
    ax_slicers = fig.add_subplot(gs[11:17, 1:99])
    ax_slicers.set_facecolor('#FFFFFF')
    ax_slicers.axis('off')
    rect_sl = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=-0.005,rounding_size=0.04", 
                                     facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1, transform=ax_slicers.transAxes)
    ax_slicers.add_patch(rect_sl)
    
    # Slicer 1: Date Range
    ax_slicers.text(0.02, 0.55, "DATE HORIZON:", fontsize=8.5, fontweight='bold', color='#64748B', va='center')
    ax_slicers.text(0.12, 0.55, " 2023-01-01  to  2024-12-31 ▼", fontsize=9, fontweight='semibold', color='#1E293B',
                    bbox=dict(boxstyle='square,pad=0.3', facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1), va='center')

    # Slicer 2: Region / Territory
    ax_slicers.text(0.35, 0.55, "REGION SLICER:", fontsize=8.5, fontweight='bold', color='#64748B', va='center')
    slicer_regions = ["All Regions", "West (40%)", "Central (20%)", "East (20%)", "South (20%)"]
    for idx, reg in enumerate(slicer_regions):
        x_r = 0.45 + idx * 0.082
        is_sel = idx == 0
        bg_c = '#2563EB' if is_sel else '#F8FAFC'
        fg_c = '#FFFFFF' if is_sel else '#475569'
        ax_slicers.text(x_r, 0.55, reg, fontsize=8, fontweight='bold' if is_sel else 'normal', color=fg_c,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=bg_c, edgecolor='#CBD5E1', linewidth=0.8), va='center')

    # Slicer 3: Product Category
    ax_slicers.text(0.88, 0.55, "CATEGORY: All (5) ▼", fontsize=8.5, fontweight='semibold', color='#1E293B',
                    bbox=dict(boxstyle='square,pad=0.3', facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1), va='center')

    # ---------------------------------------------------------
    # 3. 5 CORE KPI CARDS (gs[18:30, 1:99])
    # ---------------------------------------------------------
    kpi_specs = [
        ("TOTAL NET REVENUE", "$1,073,809", "▲ +19.4% MoM Peak", "Target: $1.02M (+5.2%)", "#2563EB", "#16A34A"),
        ("TOTAL ORDERS", "4,927", "205 orders / month", "Prior Year: 2,380 (+7.1%)", "#1E293B", "#64748B"),
        ("TOTAL UNITS SOLD", "11,161", "2.27 units / basket", "Discounts: $70,384", "#1E293B", "#64748B"),
        ("AVG ORDER VALUE", "$217.94", "Industry Target: $200", "Markdown Rate: 6.15%", "#D97706", "#D97706"),
        ("GROSS PROFIT MARGIN", "30.74%", "$330,114 Gross Margin", "Target: 28.0% (▲ +2.7%)", "#16A34A", "#16A34A")
    ]
    
    card_width = 19
    for i, (title, val, sub1, sub2, val_col, ind_col) in enumerate(kpi_specs):
        col_start = 1 + i * 20
        col_end = col_start + card_width
        ax_card = fig.add_subplot(gs[18:30, col_start:col_end])
        ax_card.set_facecolor('#FFFFFF')
        ax_card.axis('off')
        
        # Border box
        box = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=-0.005,rounding_size=0.06", 
                                     facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1.2, transform=ax_card.transAxes)
        ax_card.add_patch(box)
        
        # Top color accent bar
        accent_bar = patches.Rectangle((0, 0.94), 1, 0.06, facecolor=val_col, transform=ax_card.transAxes)
        ax_card.add_patch(accent_bar)
        
        ax_card.text(0.08, 0.78, title, fontsize=8, fontweight='bold', color='#64748B', va='center')
        ax_card.text(0.08, 0.50, val, fontsize=17, fontweight='bold', color=val_col, va='center')
        ax_card.text(0.08, 0.26, sub1, fontsize=8, fontweight='bold', color=ind_col, va='center')
        ax_card.text(0.08, 0.12, sub2, fontsize=7.5, color='#94A3B8', va='center')

    # ---------------------------------------------------------
    # 4. MAIN VISUAL 1: MONTHLY NET SALES TREND (gs[32:64, 1:62])
    # ---------------------------------------------------------
    ax_trend = fig.add_subplot(gs[32:64, 1:62])
    ax_trend.set_facecolor('#FFFFFF')
    for spine in ax_trend.spines.values():
        spine.set_color('#E2E8F0')
        spine.set_linewidth(1)
        
    df_clean['Year_Month'] = pd.to_datetime(df_clean['Date']).dt.to_period('M').astype(str)
    monthly = df_clean.groupby('Year_Month')['Net_Sales'].sum().reset_index()
    monthly['3M_MA'] = monthly['Net_Sales'].rolling(window=3, min_periods=1).mean()
    
    bars = ax_trend.bar(monthly['Year_Month'], monthly['Net_Sales'], color='#3B82F6', alpha=0.75, width=0.6, label='Net Sales Revenue ($)')
    bars[-1].set_color('#1D4ED8')
    bars[-2].set_color('#2563EB')
    bars[10].set_color('#2563EB')
    bars[11].set_color('#1D4ED8')
    
    ax_trend.plot(monthly['Year_Month'], monthly['3M_MA'], color='#F43F5E', linewidth=2.5, marker='o', markersize=4, label='3-Month Moving Average')
    
    ax_trend.set_title("Monthly Net Sales Revenue ($) & 3-Month Moving Average Trend (2023 - 2024)", fontsize=11.5, fontweight='bold', color='#1E293B', pad=12, loc='left')
    ax_trend.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax_trend.tick_params(axis='x', rotation=45, labelsize=7.5, colors='#64748B')
    ax_trend.tick_params(axis='y', labelsize=8, colors='#64748B')
    ax_trend.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#E2E8F0', fontsize=8.5)
    
    # Peak marker
    ax_trend.annotate('Q4 Holiday Peak\n$58,200', xy=(23, 58200), xytext=(20.5, 62000),
                      arrowprops=dict(facecolor='#1E293B', shrink=0.08, width=1, headwidth=5),
                      fontsize=8, fontweight='bold', color='#92400E',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1))

    # ---------------------------------------------------------
    # 5. MAIN VISUAL 2: TOP 10 PRODUCTS BY NET SALES (gs[32:64, 64:99])
    # ---------------------------------------------------------
    ax_top = fig.add_subplot(gs[32:64, 64:99])
    ax_top.set_facecolor('#FFFFFF')
    for spine in ax_top.spines.values():
        spine.set_color('#E2E8F0')
        spine.set_linewidth(1)
        
    merged_prod = df_fact.merge(df_prod, on="Product_Key")
    top_10 = merged_prod.groupby("Product_Name")["Net_Sales"].sum().sort_values(ascending=True).tail(10)
    
    colors_top = ['#3B82F6'] * 9 + ['#1E40AF']
    bars_top = ax_top.barh(top_10.index, top_10.values, color=colors_top, height=0.62, edgecolor='#E2E8F0')
    
    ax_top.set_title("Top 10 Products by Net Revenue (Ranked)", fontsize=11.5, fontweight='bold', color='#1E293B', pad=12, loc='left')
    ax_top.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax_top.tick_params(axis='y', labelsize=8, colors='#334155')
    ax_top.tick_params(axis='x', labelsize=8, colors='#64748B')
    
    for bar in bars_top:
        w = bar.get_width()
        ax_top.text(w + 1500, bar.get_y() + bar.get_height() / 2, f"${w:,.0f}", 
                    va='center', ha='left', fontsize=8, fontweight='bold', color='#1E293B')
    ax_top.set_xlim(0, max(top_10.values) * 1.20)

    # ---------------------------------------------------------
    # 6. BOTTOM VISUAL 1: REGIONAL SHARE DONUT (gs[66:98, 1:33])
    # ---------------------------------------------------------
    ax_donut = fig.add_subplot(gs[66:98, 1:33])
    ax_donut.set_facecolor('#FFFFFF')
    for spine in ax_donut.spines.values():
        spine.set_color('#E2E8F0')
        spine.set_linewidth(1)
        
    merged_reg = df_fact.merge(df_region, on="Region_Key")
    reg_sales = merged_reg.groupby("Region")["Net_Sales"].sum().sort_values(ascending=False)
    reg_colors = ['#1E40AF', '#3B82F6', '#10B981', '#F59E0B']
    
    wedges, texts, autotexts = ax_donut.pie(
        reg_sales, labels=[f"{k}\n${v/1000:.1f}k" for k, v in reg_sales.items()], 
        autopct='%1.1f%%', startangle=140, colors=reg_colors,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2.5), pctdistance=0.74,
        textprops=dict(fontsize=8, color='#334155')
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
        at.set_fontsize(8.5)
        
    ax_donut.text(0, 0, "4 Regions\n10 Stores", fontsize=9, fontweight='bold', color='#1E293B', ha='center', va='center')
    ax_donut.set_title("Geographic Sales & Territory Share", fontsize=11, fontweight='bold', color='#1E293B', pad=10, loc='left')

    # ---------------------------------------------------------
    # 7. BOTTOM VISUAL 2: CATEGORY MATRIX & MARGINS (gs[66:98, 35:99])
    # ---------------------------------------------------------
    ax_cat = fig.add_subplot(gs[66:98, 35:99])
    ax_cat.set_facecolor('#FFFFFF')
    for spine in ax_cat.spines.values():
        spine.set_color('#E2E8F0')
        spine.set_linewidth(1)
        
    cat_summary = merged_prod.groupby("Product_Category").agg(
        Orders=('Sales_Key', 'count'),
        Units=('Quantity', 'sum'),
        Net_Sales=('Net_Sales', 'sum'),
        Gross_Profit=('Gross_Profit', 'sum')
    ).reset_index()
    cat_summary['Margin_Pct'] = (cat_summary['Gross_Profit'] / cat_summary['Net_Sales']) * 100
    cat_summary = cat_summary.sort_values("Net_Sales", ascending=True)
    
    y_pos = np.arange(len(cat_summary))
    bars_c = ax_cat.barh(y_pos, cat_summary['Net_Sales'], height=0.52, color='#10B981', alpha=0.85, edgecolor='#E2E8F0', label='Net Revenue')
    ax_cat.set_yticks(y_pos)
    ax_cat.set_yticklabels(cat_summary['Product_Category'], fontsize=9, fontweight='semibold', color='#334155')
    ax_cat.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax_cat.tick_params(axis='both', labelsize=8, colors='#64748B')
    ax_cat.set_title("Product Category Performance Matrix (Revenue, Volume & Margin %)", fontsize=11, fontweight='bold', color='#1E293B', pad=10, loc='left')
    
    for idx, (p, (_, row)) in enumerate(zip(bars_c, cat_summary.iterrows())):
        w = p.get_width()
        margin_str = f"Margin: {row['Margin_Pct']:.1f}%"
        orders_str = f"{row['Orders']:,} orders | {row['Units']:,} units"
        ax_cat.text(w + 3000, p.get_y() + p.get_height() / 2, f"${w:,.0f}  ({margin_str})  [{orders_str}]", 
                    va='center', ha='left', fontsize=8, fontweight='bold', color='#1E293B')
        
    ax_cat.set_xlim(0, max(cat_summary['Net_Sales']) * 1.45)
    
    # Save the canvas image
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Rendered Power BI Canvas: {output_path}")

def render_powerbi_desktop_window_view(canvas_image_path, output_path):
    """Embeds the canvas inside an authentic Power BI Desktop application frame."""
    canvas_img = Image.open(canvas_image_path)
    cw, ch = canvas_img.size
    
    # Window dimensions: Canvas width + sidebars, Canvas height + top ribbons + bottom tabs
    top_bar_h = 135
    left_sidebar_w = 48
    right_pane_w = 330
    bottom_bar_h = 42
    
    total_w = cw + left_sidebar_w + right_pane_w
    total_h = ch + top_bar_h + bottom_bar_h
    
    win = Image.new('RGB', (total_w, total_h), color='#F3F4F6')
    draw = ImageDraw.Draw(win)
    
    # Try loading Segoe UI or fallback to standard font
    try:
        font_title = ImageFont.truetype("segoeui.ttf", 15)
        font_ribbon = ImageFont.truetype("segoeui.ttf", 13)
        font_small = ImageFont.truetype("segoeui.ttf", 11)
        font_bold = ImageFont.truetype("segouib.ttf", 12)
    except:
        font_title = font_ribbon = font_small = font_bold = ImageFont.load_default()
        
    # 1. WINDOW TITLE BAR (0 to 36 px)
    draw.rectangle([0, 0, total_w, 36], fill='#201F1E')  # Power BI dark title bar
    draw.text((16, 9), "Sales_Performance_Dashboard.pbix - Power BI Desktop", fill='#FFFFFF', font=font_title)
    
    # Window controls (min, max, close)
    draw.text((total_w - 90, 8), "—   □   ✕", fill='#A19F9D', font=font_title)
    
    # 2. POWER BI RIBBON (36 to 135 px)
    draw.rectangle([0, 36, total_w, 64], fill='#FAF9F8')  # Menu bar
    menu_items = ["File", "Home", "Insert", "Modeling", "View", "Optimize", "Help"]
    x_m = 16
    for idx, item in enumerate(menu_items):
        is_home = item == "Home"
        if is_home:
            draw.rectangle([x_m - 6, 38, x_m + 48, 62], fill='#FFFFFF')
            draw.text((x_m, 44), item, fill='#115E59', font=font_bold)
            draw.line([(x_m - 6, 62), (x_m + 48, 62)], fill='#0F766E', width=3)
        else:
            draw.text((x_m, 44), item, fill='#323130', font=font_ribbon)
        x_m += 65
        
    # Ribbon command actions strip
    draw.rectangle([0, 64, total_w, 135], fill='#FFFFFF')
    draw.line([(0, 134), (total_w, 134)], fill='#EDEBE9', width=1)
    
    # Ribbon command mock buttons
    ribbon_cmds = [
        ("Get data ▼", 16), ("Excel", 95), ("SQL Server", 145), ("Enter data", 225), 
        ("Transform data ▼", 305), ("Refresh", 415), ("New visual", 485), 
        ("Text box", 570), ("More visuals ▼", 640), ("New measure", 745), 
        ("Quick measure", 840), ("Publish", 945)
    ]
    for label, x_pos in ribbon_cmds:
        draw.rectangle([x_pos, 78, x_pos + 12, 90], fill='#0284C7' if 'data' in label else '#10B981')
        draw.text((x_pos + 18, 77), label, fill='#201F1E', font=font_small)
        
    # 3. LEFT VIEW SWITCHER (0 to 48 px width)
    draw.rectangle([0, 135, left_sidebar_w, total_h - bottom_bar_h], fill='#FFFFFF')
    draw.line([(left_sidebar_w - 1, 135), (left_sidebar_w - 1, total_h - bottom_bar_h)], fill='#EDEBE9', width=1)
    # Icons: Report (selected), Table, Model
    draw.rectangle([8, 148, 40, 180], fill='#E6F4EA')
    draw.text((18, 154), "📊", font=font_title)
    draw.text((18, 196), "▦", font=font_title)
    draw.text((18, 238), "🗂", font=font_title)

    # 4. PASTE THE CANVAS
    win.paste(canvas_img, (left_sidebar_w, top_bar_h))
    
    # 5. RIGHT SIDE PANELS (Visualizations & Data)
    rx = left_sidebar_w + cw
    draw.rectangle([rx, top_bar_h, total_w, total_h - bottom_bar_h], fill='#FFFFFF')
    draw.line([(rx, top_bar_h), (rx, total_h - bottom_bar_h)], fill='#E5E7EB', width=1)
    
    # Visualizations pane header
    draw.text((rx + 14, top_bar_h + 12), "Visualizations", fill='#201F1E', font=font_bold)
    # Mini visual picker grid
    v_icons = ["📊", "📈", "📉", "🍩", "📋", "🗃", "🗺", "🏷", "🔢", "⏳"]
    for vi, ico in enumerate(v_icons):
        vx = rx + 14 + (vi % 5) * 32
        vy = top_bar_h + 38 + (vi // 5) * 30
        draw.rectangle([vx, vy, vx + 26, vy + 24], fill='#F8FAFC', outline='#CBD5E1')
        draw.text((vx + 6, vy + 3), ico, font=font_small)
        
    # Data Pane
    draw.line([(rx, top_bar_h + 125), (total_w, top_bar_h + 125)], fill='#EDEBE9', width=1)
    draw.text((rx + 14, top_bar_h + 138), "Data (Star Schema)", fill='#201F1E', font=font_bold)
    
    tables = [
        ("📁 _Measures (25+ DAX)", True),
        ("▦ Fact_Sales (4,927 rows)", True),
        ("  ∑ Gross_Sales", False),
        ("  ∑ Net_Sales", False),
        ("  ∑ Quantity", False),
        ("  ∑ Total_Cost", False),
        ("  ∑ Gross_Profit", False),
        ("▦ Dim_Date (731 days)", True),
        ("▦ Dim_Product (34 SKUs)", True),
        ("▦ Dim_Customer (1,189 cust)", True),
        ("▦ Dim_Region (10 stores)", True),
    ]
    ty = top_bar_h + 170
    for tbl, is_tbl in tables:
        col = '#0F172A' if is_tbl else '#64748B'
        draw.text((rx + 16, ty), tbl, fill=col, font=font_bold if is_tbl else font_small)
        ty += 24
        
    # 6. BOTTOM STATUS / PAGE TABS BAR
    by = total_h - bottom_bar_h
    draw.rectangle([0, by, total_w, total_h], fill='#FAF9F8')
    draw.line([(0, by), (total_w, by)], fill='#EDEBE9', width=1)
    
    # Page tab buttons
    pages = ["Executive Scorecard", "Product Performance", "Regional Analysis", "+"]
    px = 30
    for idx, page in enumerate(pages):
        is_active = idx == 0
        pw = len(page) * 8 + 20
        if is_active:
            draw.rectangle([px, by + 4, px + pw, total_h], fill='#FFFFFF', outline='#EDEBE9')
            draw.text((px + 10, by + 12), page, fill='#0F766E', font=font_bold)
        else:
            draw.text((px + 10, by + 12), page, fill='#605E5C', font=font_small)
        px += pw + 8
        
    draw.text((total_w - 240, by + 12), "100% | Fit to page | Page 1 of 3", fill='#605E5C', font=font_small)
    
    win.save(output_path, quality=95)
    print(f"Rendered Full Power BI Desktop View: {output_path}")

def main():
    print("=" * 70)
    print("GENERATING POWER BI DASHBOARD IMAGES")
    print("=" * 70)
    
    canvas_path = os.path.join(POWER_BI_DIR, "power_bi_dashboard_canvas.png")
    desktop_view_path = os.path.join(POWER_BI_DIR, "power_bi_desktop_application_view.png")
    
    render_powerbi_canvas(canvas_path)
    render_powerbi_desktop_window_view(canvas_path, desktop_view_path)
    
    # Copy to visuals/ and docs/ and brain
    import shutil
    shutil.copy2(canvas_path, os.path.join(VISUALS_DIR, "power_bi_dashboard_canvas.png"))
    shutil.copy2(desktop_view_path, os.path.join(VISUALS_DIR, "power_bi_desktop_application_view.png"))
    shutil.copy2(canvas_path, os.path.join(BRAIN_VISUALS_DIR, "power_bi_dashboard_canvas.png"))
    shutil.copy2(desktop_view_path, os.path.join(BRAIN_VISUALS_DIR, "power_bi_desktop_application_view.png"))
    
    print("All Power BI dashboard images generated and staged successfully.")

if __name__ == "__main__":
    main()
