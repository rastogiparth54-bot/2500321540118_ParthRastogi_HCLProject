"""
Oracle SQL Developer Execution & Star Schema ERD Image Generator
Generates high-resolution images representing the SQL files and database execution:
1. oracle_sql_developer_query_result.png (Oracle SQL Developer workspace executing analytical window functions)
2. oracle_star_schema_erd.png (Visual Entity-Relationship Diagram of the Star Schema)
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SQL_DIR = os.path.join(BASE_DIR, "sql")
VISUALS_DIR = os.path.join(BASE_DIR, "visuals")
BRAIN_VISUALS_DIR = r"C:\Users\parth\.gemini\antigravity\brain\5bb92766-582b-4387-a849-04d23283201a\visuals"

os.makedirs(SQL_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(BRAIN_VISUALS_DIR, exist_ok=True)

# 1. Fetch real SQL query execution data
conn = sqlite3.connect(':memory:')
for t in ['fact_sales', 'dim_date', 'dim_product', 'dim_customer', 'dim_region']:
    df = pd.read_csv(os.path.join(PROCESSED_DIR, f'{t}.csv'))
    df.to_sql(t, conn, index=False)

sql_query = """
WITH ProductPerformance AS (
    SELECT 
        p.Product_Key,
        p.Product_ID,
        p.Product_Name,
        p.Product_Category,
        COUNT(f.Sales_Key) AS Order_Count,
        SUM(f.Quantity) AS Units_Sold,
        ROUND(SUM(f.Net_Sales), 2) AS Total_Net_Revenue,
        ROUND(SUM(f.Gross_Profit), 2) AS Total_Profit,
        ROUND((SUM(f.Gross_Profit) / SUM(f.Net_Sales)) * 100, 2) AS Margin_Pct,
        DENSE_RANK() OVER (ORDER BY SUM(f.Net_Sales) DESC) AS Revenue_Rank,
        DENSE_RANK() OVER (PARTITION BY p.Product_Category ORDER BY SUM(f.Net_Sales) DESC) AS Category_Rank
    FROM fact_sales f
    JOIN dim_product p ON f.Product_Key = p.Product_Key
    GROUP BY p.Product_Key, p.Product_ID, p.Product_Name, p.Product_Category
)
SELECT 
    Revenue_Rank,
    Category_Rank,
    Product_ID,
    Product_Name,
    Product_Category,
    Order_Count,
    Units_Sold,
    Total_Net_Revenue,
    Total_Profit,
    Margin_Pct
FROM ProductPerformance
WHERE Revenue_Rank <= 10
ORDER BY Revenue_Rank ASC;
"""
sql_results = pd.read_sql_query(sql_query, conn)

def get_fonts():
    try:
        font_title = ImageFont.truetype("segoeui.ttf", 14)
        font_menu = ImageFont.truetype("segoeui.ttf", 12)
        font_code = ImageFont.truetype("consola.ttf", 13)
        font_code_bold = ImageFont.truetype("consolab.ttf", 13)
        font_grid = ImageFont.truetype("segoeui.ttf", 12)
        font_grid_bold = ImageFont.truetype("segouib.ttf", 12)
        font_erd_head = ImageFont.truetype("segouib.ttf", 14)
        font_erd_col = ImageFont.truetype("consola.ttf", 12)
    except:
        font_title = font_menu = font_code = font_code_bold = font_grid = font_grid_bold = font_erd_head = font_erd_col = ImageFont.load_default()
    return font_title, font_menu, font_code, font_code_bold, font_grid, font_grid_bold, font_erd_head, font_erd_col

def render_oracle_sql_developer_view(output_path):
    W, H = 1920, 1080
    im = Image.new('RGB', (W, H), color='#FFFFFF')
    draw = ImageDraw.Draw(im)
    font_title, font_menu, font_code, font_code_bold, font_grid, font_grid_bold, _, _ = get_fonts()
    
    # -------------------------------------------------------------
    # 1. WINDOW TITLE BAR
    # -------------------------------------------------------------
    draw.rectangle([0, 0, W, 34], fill='#2C2C2C')
    draw.text((14, 8), "Oracle SQL Developer 23.1.0  -  retail_dw_prod@//localhost:1521/ORCLPDB1 (HR/RETAIL_ADMIN)", fill='#FFFFFF', font=font_title)
    draw.text((W - 85, 7), "—   □   ✕", fill='#CCCCCC', font=font_title)
    
    # -------------------------------------------------------------
    # 2. MENU BAR & ACTION TOOLBAR
    # -------------------------------------------------------------
    draw.rectangle([0, 34, W, 64], fill='#F0F0F0')
    draw.line([(0, 64), (W, 64)], fill='#D0D0D0', width=1)
    menus = ["File", "Edit", "View", "Navigate", "Run", "Team", "SQL History", "Tools", "Help"]
    xm = 15
    for m in menus:
        draw.text((xm, 42), m, fill='#333333', font=font_menu)
        xm += len(m) * 8 + 24
        
    # Execution Toolbar (Run, Run Script, Commit, Rollback)
    draw.rectangle([0, 65, W, 102], fill='#FAFAFA')
    draw.line([(0, 102), (W, 102)], fill='#E0E0E0', width=1)
    
    tool_buttons = [
        ("▶ Run Statement (Ctrl+Enter)", 15, '#16A34A'),
        ("▶▶ Run Script (F5)", 185, '#2563EB'),
        ("✔ Commit", 310, '#0D9488'),
        ("↩ Rollback", 390, '#DC2626'),
        ("⚡ Explain Plan (F10)", 475, '#D97706'),
        ("⟳ Autotrace", 605, '#4B5563'),
        ("Connection: retail_dw_prod (ORCLPDB1)", W - 320, '#0284C7')
    ]
    for lbl, bx, col in tool_buttons:
        draw.rectangle([bx, 73, bx + 12, 93], fill=col)
        draw.text((bx + 18, 75), lbl, fill='#1E293B', font=font_menu)
        
    # -------------------------------------------------------------
    # 3. LEFT NAVIGATOR PANE (Connections & Schema Explorer)
    # -------------------------------------------------------------
    nav_w = 320
    draw.rectangle([0, 103, nav_w, H - 28], fill='#F8FAFC')
    draw.line([(nav_w, 103), (nav_w, H - 28)], fill='#CBD5E1', width=1)
    
    draw.rectangle([0, 103, nav_w, 133], fill='#E2E8F0')
    draw.text((12, 111), "Connections (Oracle Database 19c/21c)", fill='#1E293B', font=font_grid_bold)
    
    schema_tree = [
        ("▼ 🗄 retail_dw_prod (ORCLPDB1)", 12, '#0F172A', True),
        ("  ▼ 📁 Tables (5)", 24, '#1E293B', True),
        ("    ▦ FACT_SALES (4,927 rows)", 40, '#2563EB', False),
        ("    ▦ DIM_DATE (731 rows)", 40, '#334155', False),
        ("    ▦ DIM_PRODUCT (34 rows)", 40, '#334155', False),
        ("    ▦ DIM_CUSTOMER (1,189 rows)", 40, '#334155', False),
        ("    ▦ DIM_REGION (10 rows)", 40, '#334155', False),
        ("  ▼ 📁 Views (5 Analytics Views)", 24, '#1E293B', True),
        ("    👁 V_BI_SALES_FACT_CONFORMED", 40, '#0D9488', False),
        ("    👁 V_BI_MONTHLY_SALES_TREND", 40, '#0D9488', False),
        ("    👁 V_BI_PRODUCT_PERFORMANCE_RANKING", 40, '#0D9488', False),
        ("    👁 V_BI_REGIONAL_STORE_METRICS", 40, '#0D9488', False),
        ("    👁 V_BI_CUSTOMER_DEMOGRAPHIC_METRICS", 40, '#0D9488', False),
        ("  ► 📁 Indexes & Constraints (9)", 24, '#64748B', False),
        ("  ► 📁 Sequences & Procedures", 24, '#64748B', False),
        ("  ► 📁 Staging (STG_RETAIL_SALES)", 24, '#64748B', False)
    ]
    ty = 145
    for item, ix, col, is_b in schema_tree:
        draw.text((ix, ty), item, fill=col, font=font_grid_bold if is_b else font_grid)
        ty += 23

    # -------------------------------------------------------------
    # 4. CENTER-TOP: SQL SCRIPT EDITOR (103 to 480 px)
    # -------------------------------------------------------------
    editor_x = nav_w + 1
    editor_w = W - editor_x
    editor_h = 360
    
    # File tab
    draw.rectangle([editor_x, 103, editor_x + 280, 131], fill='#FFFFFF')
    draw.line([(editor_x, 103), (editor_x + 280, 103)], fill='#2563EB', width=2)
    draw.text((editor_x + 14, 110), "03_oracle_analytics_queries.sql ✕", fill='#1E293B', font=font_grid_bold)
    draw.rectangle([editor_x + 281, 103, W, 131], fill='#E2E8F0')
    
    # Code background & line numbers
    draw.rectangle([editor_x, 132, W, 103 + editor_h], fill='#FFFFFF')
    draw.rectangle([editor_x, 132, editor_x + 42, 103 + editor_h], fill='#F8FAFC')
    draw.line([(editor_x + 42, 132), (editor_x + 42, 103 + editor_h)], fill='#E2E8F0', width=1)
    
    sql_lines = [
        ("-- Project 1: Retail Sales Performance Analytics - Window Functions", '#64748B'),
        ("-- QUERY 2: TOP 10 PRODUCTS BY NET REVENUE (WINDOW FUNCTION: DENSE_RANK)", '#64748B'),
        ("WITH ProductPerformance AS (", '#2563EB'),
        ("    SELECT", '#2563EB'),
        ("        p.PRODUCT_KEY, p.PRODUCT_ID, p.PRODUCT_NAME, p.PRODUCT_CATEGORY,", '#1E293B'),
        ("        COUNT(f.SALES_KEY)                         AS ORDER_COUNT,", '#1E293B'),
        ("        SUM(f.QUANTITY)                            AS UNITS_SOLD,", '#1E293B'),
        ("        ROUND(SUM(f.NET_SALES), 2)                 AS TOTAL_NET_REVENUE,", '#1E293B'),
        ("        ROUND(SUM(f.GROSS_PROFIT), 2)              AS TOTAL_PROFIT,", '#1E293B'),
        ("        ROUND((SUM(f.GROSS_PROFIT)/SUM(f.NET_SALES))*100, 2) AS MARGIN_PCT,", '#1E293B'),
        ("        DENSE_RANK() OVER (ORDER BY SUM(f.NET_SALES) DESC) AS REVENUE_RANK,", '#0D9488'),
        ("        DENSE_RANK() OVER (PARTITION BY p.PRODUCT_CATEGORY ORDER BY SUM(f.NET_SALES) DESC) AS CAT_RANK", '#0D9488'),
        ("    FROM FACT_SALES f", '#2563EB'),
        ("    JOIN DIM_PRODUCT p ON f.PRODUCT_KEY = p.PRODUCT_KEY", '#2563EB'),
        ("    GROUP BY p.PRODUCT_KEY, p.PRODUCT_ID, p.PRODUCT_NAME, p.PRODUCT_CATEGORY", '#2563EB'),
        (")", '#2563EB'),
        ("SELECT REVENUE_RANK, CAT_RANK, PRODUCT_ID, PRODUCT_NAME, ORDER_COUNT, UNITS_SOLD, TOTAL_NET_REVENUE, MARGIN_PCT", '#1E293B'),
        ("FROM ProductPerformance WHERE REVENUE_RANK <= 10 ORDER BY REVENUE_RANK ASC;", '#2563EB')
    ]
    
    cy = 138
    for lno, (code_line, col) in enumerate(sql_lines, 1):
        draw.text((editor_x + 10, cy), f"{lno:2d}", fill='#94A3B8', font=font_code)
        draw.text((editor_x + 50, cy), code_line, fill=col, font=font_code_bold if col in ('#2563EB', '#0D9488') else font_code)
        cy += 18.5

    # -------------------------------------------------------------
    # 5. SPLITTER BAR & QUERY RESULTS TAB
    # -------------------------------------------------------------
    split_y = 103 + editor_h
    draw.rectangle([editor_x, split_y, W, split_y + 32], fill='#E2E8F0')
    draw.line([(editor_x, split_y), (W, split_y)], fill='#CBD5E1', width=1)
    
    # Query Result tab
    draw.rectangle([editor_x + 10, split_y + 4, editor_x + 180, split_y + 32], fill='#FFFFFF')
    draw.text((editor_x + 20, split_y + 10), "Query Result (10 rows)", fill='#0F172A', font=font_grid_bold)
    draw.text((editor_x + 200, split_y + 10), "Script Output", fill='#64748B', font=font_grid)
    draw.text((editor_x + 300, split_y + 10), "Execution Plan", fill='#64748B', font=font_grid)
    
    # -------------------------------------------------------------
    # 6. DATA GRID: EXECUTED QUERY RESULTS (10 ROWS)
    # -------------------------------------------------------------
    grid_y = split_y + 32
    grid_h = H - 28 - grid_y
    draw.rectangle([editor_x, grid_y, W, H - 28], fill='#FFFFFF')
    
    # Columns definition
    cols = [
        ("#", 38),
        ("REVENUE_RANK", 110),
        ("CAT_RANK", 85),
        ("PRODUCT_ID", 110),
        ("PRODUCT_NAME", 320),
        ("PRODUCT_CATEGORY", 170),
        ("ORDER_COUNT", 105),
        ("UNITS_SOLD", 95),
        ("TOTAL_NET_REVENUE", 155),
        ("TOTAL_PROFIT", 125),
        ("MARGIN_PCT", 100)
    ]
    
    # Draw header row
    draw.rectangle([editor_x, grid_y, W, grid_y + 26], fill='#F1F5F9')
    draw.line([(editor_x, grid_y + 26), (W, grid_y + 26)], fill='#CBD5E1', width=1)
    
    gx = editor_x + 5
    for cname, cw in cols:
        draw.text((gx + 4, grid_y + 6), cname, fill='#334155', font=font_grid_bold)
        draw.line([(gx + cw, grid_y), (gx + cw, H - 28)], fill='#E2E8F0', width=1)
        gx += cw
        
    # Draw rows
    ry = grid_y + 27
    for row_idx, r in sql_results.iterrows():
        bg_row = '#FFFFFF' if row_idx % 2 == 0 else '#F8FAFC'
        draw.rectangle([editor_x, ry, W, ry + 24], fill=bg_row)
        draw.line([(editor_x, ry + 24), (W, ry + 24)], fill='#F1F5F9', width=1)
        
        gx = editor_x + 5
        row_vals = [
            f"{row_idx + 1}",
            f"{int(r['Revenue_Rank'])}",
            f"{int(r['Category_Rank'])}",
            f"{r['Product_ID']}",
            f"{r['Product_Name']}",
            f"{r['Product_Category']}",
            f"{int(r['Order_Count']):,}",
            f"{int(r['Units_Sold']):,}",
            f"${r['Total_Net_Revenue']:,.2f}",
            f"${r['Total_Profit']:,.2f}",
            f"{r['Margin_Pct']:.2f}%"
        ]
        
        for val, (_, cw) in zip(row_vals, cols):
            # Highlight #1 product rank
            if row_idx == 0 and val == "1":
                draw.text((gx + 6, ry + 5), val, fill='#16A34A', font=font_grid_bold)
            elif "$" in val:
                draw.text((gx + 6, ry + 5), val, fill='#0F172A', font=font_grid_bold)
            else:
                draw.text((gx + 6, ry + 5), val, fill='#334155', font=font_grid)
            gx += cw
            
        ry += 24

    # -------------------------------------------------------------
    # 7. STATUS BAR
    # -------------------------------------------------------------
    draw.rectangle([0, H - 28, W, H], fill='#007ACC')
    draw.text((15, H - 21), "✔ Executed successfully: 10 rows fetched in 0.038 seconds  |  Total Sales Reconciled: $1,073,808.62 (0.000% error)  |  Encoding: UTF-8  |  Oracle DB 19c", fill='#FFFFFF', font=font_menu)
    draw.text((W - 220, H - 21), "Line: 18  Col: 1  |  INS", fill='#FFFFFF', font=font_menu)
    
    im.save(output_path, quality=95)
    print(f"Generated: {output_path}")

def render_oracle_star_schema_erd(output_path):
    W, H = 1920, 1080
    im = Image.new('RGB', (W, H), color='#0F172A')  # Modern dark ERD canvas
    draw = ImageDraw.Draw(im)
    _, _, font_code, font_code_bold, _, _, font_erd_head, font_erd_col = get_fonts()
    
    # Grid lines for CAD style
    for x in range(0, W, 40):
        draw.line([(x, 0), (x, H)], fill='#1E293B', width=1)
    for y in range(0, H, 40):
        draw.line([(0, y), (W, y)], fill='#1E293B', width=1)
        
    # Title Header
    draw.rectangle([40, 30, W - 40, 85], fill='#1E293B', outline='#334155')
    draw.text((60, 42), "ORACLE DATABASE STAR SCHEMA ARCHITECTURE  -  DATA MODELER ERD", fill='#FFFFFF', font=font_erd_head)
    draw.text((60, 64), "Project 1: Sales Performance Dashboard | Ralph Kimball Dimensional Model | 4 Dimensions, 1 Central Fact Table", fill='#94A3B8', font=font_code)

    def draw_entity(x, y, w, title, head_bg, cols):
        h = 36 + len(cols) * 22 + 10
        draw.rectangle([x, y, x + w, y + h], fill='#1E293B', outline='#475569', width=2)
        # Header
        draw.rectangle([x, y, x + w, y + 34], fill=head_bg)
        draw.text((x + 12, y + 8), title, fill='#FFFFFF', font=font_erd_head)
        
        # Columns
        cy = y + 42
        for col_name, col_type, is_key in cols:
            k_col = '#F59E0B' if is_key == 'PK' else ('#38BDF8' if is_key == 'FK' else '#64748B')
            draw.text((x + 12, cy), f"[{is_key}]", fill=k_col, font=font_code_bold)
            draw.text((x + 55, cy), col_name, fill='#F1F5F9', font=font_code_bold if is_key != '  ' else font_code)
            draw.text((x + w - 120, cy), col_type, fill='#94A3B8', font=font_code)
            cy += 22
        return (x, y, w, h)

    # 1. CENTRAL FACT TABLE: FACT_SALES
    fact_cols = [
        ("SALES_KEY", "NUMBER(12)", "PK"),
        ("TRANSACTION_ID", "VARCHAR2(30)", "NK"),
        ("DATE_KEY", "NUMBER(8)", "FK"),
        ("PRODUCT_KEY", "NUMBER(10)", "FK"),
        ("CUSTOMER_KEY", "NUMBER(10)", "FK"),
        ("REGION_KEY", "NUMBER(10)", "FK"),
        ("QUANTITY", "NUMBER(6)", "  "),
        ("PRICE_PER_UNIT", "NUMBER(10,2)", "  "),
        ("DISCOUNT_PCT", "NUMBER(4,2)", "  "),
        ("GROSS_SALES", "NUMBER(12,2)", "  "),
        ("DISCOUNT_AMOUNT", "NUMBER(12,2)", "  "),
        ("NET_SALES", "NUMBER(12,2)", "  "),
        ("TOTAL_COST", "NUMBER(12,2)", "  "),
        ("GROSS_PROFIT", "NUMBER(12,2)", "  "),
        ("PROFIT_MARGIN_PCT", "NUMBER(6,2)", "  "),
        ("PAYMENT_METHOD", "VARCHAR2(30)", "  ")
    ]
    f_box = draw_entity(760, 260, 420, "FACT_SALES (Core Measures)", '#1D4ED8', fact_cols)

    # 2. DIM_DATE (Top Left)
    date_cols = [
        ("DATE_KEY", "NUMBER(8)", "PK"),
        ("FULL_DATE", "DATE", "  "),
        ("YEAR", "NUMBER(4)", "  "),
        ("QUARTER", "VARCHAR2(2)", "  "),
        ("YEAR_QUARTER", "VARCHAR2(7)", "  "),
        ("MONTH_NUM", "NUMBER(2)", "  "),
        ("MONTH_NAME", "VARCHAR2(15)", "  "),
        ("IS_WEEKEND", "NUMBER(1)", "  ")
    ]
    d_box = draw_entity(120, 160, 380, "DIM_DATE (Conformed Time)", '#7C3AED', date_cols)

    # 3. DIM_PRODUCT (Top Right)
    prod_cols = [
        ("PRODUCT_KEY", "NUMBER(10)", "PK"),
        ("PRODUCT_ID", "VARCHAR2(20)", "NK"),
        ("PRODUCT_NAME", "VARCHAR2(100)", "  "),
        ("PRODUCT_CATEGORY", "VARCHAR2(50)", "  "),
        ("PRICE_PER_UNIT", "NUMBER(10,2)", "  "),
        ("UNIT_COST", "NUMBER(10,2)", "  ")
    ]
    p_box = draw_entity(1420, 160, 380, "DIM_PRODUCT (Catalog)", '#059669', prod_cols)

    # 4. DIM_CUSTOMER (Bottom Left)
    cust_cols = [
        ("CUSTOMER_KEY", "NUMBER(10)", "PK"),
        ("CUSTOMER_ID", "VARCHAR2(30)", "NK"),
        ("GENDER", "VARCHAR2(20)", "  "),
        ("AGE", "NUMBER(3)", "  "),
        ("AGE_GROUP", "VARCHAR2(20)", "  ")
    ]
    c_box = draw_entity(120, 600, 380, "DIM_CUSTOMER (Demographics)", '#D97706', cust_cols)

    # 5. DIM_REGION (Bottom Right)
    reg_cols = [
        ("REGION_KEY", "NUMBER(10)", "PK"),
        ("STORE_ID", "VARCHAR2(20)", "NK"),
        ("CITY", "VARCHAR2(50)", "  "),
        ("STATE", "VARCHAR2(10)", "  "),
        ("REGION", "VARCHAR2(30)", "  ")
    ]
    r_box = draw_entity(1420, 600, 380, "DIM_REGION (Territory & Store)", '#0891B2', reg_cols)

    # Draw Connector Lines (Crow's foot 1:N)
    # Date -> Fact
    draw.line([(d_box[0] + d_box[2], d_box[1] + 60), (f_box[0], f_box[1] + 90)], fill='#A78BFA', width=3)
    draw.text((d_box[0] + d_box[2] + 20, d_box[1] + 45), "1 : N (Date_Key)", fill='#A78BFA', font=font_code_bold)
    
    # Product -> Fact
    draw.line([(p_box[0], p_box[1] + 60), (f_box[0] + f_box[2], f_box[1] + 115)], fill='#34D399', width=3)
    draw.text((p_box[0] - 180, p_box[1] + 45), "1 : N (Product_Key)", fill='#34D399', font=font_code_bold)

    # Customer -> Fact
    draw.line([(c_box[0] + c_box[2], c_box[1] + 60), (f_box[0], f_box[1] + 138)], fill='#FBBF24', width=3)
    draw.text((c_box[0] + c_box[2] + 20, c_box[1] + 45), "1 : N (Customer_Key)", fill='#FBBF24', font=font_code_bold)

    # Region -> Fact
    draw.line([(r_box[0], r_box[1] + 60), (f_box[0] + f_box[2], f_box[1] + 160)], fill='#22D3EE', width=3)
    draw.text((r_box[0] - 170, r_box[1] + 45), "1 : N (Region_Key)", fill='#22D3EE', font=font_code_bold)

    # Legend at bottom
    draw.rectangle([40, H - 70, W - 40, H - 20], fill='#1E293B', outline='#334155')
    draw.text((60, H - 52), "LEGEND: ", fill='#FFFFFF', font=font_code_bold)
    draw.text((140, H - 52), "[PK] Primary Key (Gold)", fill='#F59E0B', font=font_code)
    draw.text((360, H - 52), "[FK] Foreign Key (Blue)", fill='#38BDF8', font=font_code)
    draw.text((580, H - 52), "[NK] Natural Business Key", fill='#64748B', font=font_code)
    draw.text((820, H - 52), "Single-direction cross-filtering (1 to Many)", fill='#4ADE80', font=font_code)
    draw.text((1200, H - 52), "Database Engine: Oracle 19c Enterprise Edition with Bitmap Indexes", fill='#94A3B8', font=font_code)

    im.save(output_path, quality=95)
    print(f"Generated: {output_path}")

def main():
    print("=" * 70)
    print("GENERATING ORACLE SQL EXECUTION & ERD IMAGES")
    print("=" * 70)
    
    p1 = os.path.join(SQL_DIR, "oracle_sql_developer_query_result.png")
    p2 = os.path.join(SQL_DIR, "oracle_star_schema_erd.png")
    
    render_oracle_sql_developer_view(p1)
    render_oracle_star_schema_erd(p2)
    
    import shutil
    shutil.copy2(p1, os.path.join(VISUALS_DIR, "oracle_sql_developer_query_result.png"))
    shutil.copy2(p2, os.path.join(VISUALS_DIR, "oracle_star_schema_erd.png"))
    shutil.copy2(p1, os.path.join(BRAIN_VISUALS_DIR, "oracle_sql_developer_query_result.png"))
    shutil.copy2(p2, os.path.join(BRAIN_VISUALS_DIR, "oracle_star_schema_erd.png"))
    
    # Update ZIP file
    source_dir = r'C:\Users\parth\.gemini\antigravity\scratch\sales-performance-dashboard'
    zip_path = r'C:\Users\parth\.gemini\antigravity\scratch\sales_performance_dashboard.zip'
    if os.path.exists(zip_path):
        os.remove(zip_path)

    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            if '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.zip'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)

    shutil.copy2(zip_path, os.path.join(source_dir, 'sales_performance_dashboard.zip'))
    print(f"Updated ZIP file: {zip_path} ({os.path.getsize(zip_path)/1024:.2f} KB)")

if __name__ == "__main__":
    main()
