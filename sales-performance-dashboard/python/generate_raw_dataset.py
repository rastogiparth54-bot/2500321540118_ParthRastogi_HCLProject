"""
Data Generation Script for Retail Sales Performance Dashboard Project
Simulates a real-world raw Kaggle retail sales dataset with typical enterprise dirty-data anomalies:
- Duplicates (exact & key collisions)
- Missing / Null values
- Inconsistent date formats & invalid dates
- Negative quantities and amounts (returns & input errors)
- Discrepancies between unit price, quantity, discount and total amount
- String whitespace and case inconsistencies
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
RAW_FILE_PATH = os.path.join(OUTPUT_DIR, "kaggle_retail_sales_raw.csv")

# Catalog metadata
PRODUCT_CATALOG = {
    "Electronics": [
        ("PROD-E101", "Smartphone 5G Pro", 799.99),
        ("PROD-E102", "Wireless Noise-Cancelling Headphones", 149.99),
        ("PROD-E103", "4K Ultra HD Smart TV 55-inch", 499.99),
        ("PROD-E104", "Mechanical Gaming Keyboard", 89.99),
        ("PROD-E105", "Ergonomic Wireless Mouse", 39.99),
        ("PROD-E106", "Smartwatch Fitness Tracker", 199.99),
        ("PROD-E107", "Portable Bluetooth Speaker", 59.99),
        ("PROD-E108", "Tablet 10-inch 128GB", 329.99),
        ("PROD-E109", "USB-C Multiport Dock", 49.99),
        ("PROD-E110", "Noise-Isolating Earbuds", 29.99),
    ],
    "Clothing": [
        ("PROD-C201", "Men Slim Fit Denim Jeans", 59.99),
        ("PROD-C202", "Women Classic Cotton Blouse", 45.00),
        ("PROD-C203", "Unisex Hooded Sweatshirt", 49.99),
        ("PROD-C204", "Formal Cotton Dress Shirt", 39.50),
        ("PROD-C205", "Breathable Athletic Running Shorts", 29.99),
        ("PROD-C206", "Merino Wool Knit Sweater", 79.99),
        ("PROD-C207", "Waterproof Winter Down Jacket", 149.99),
        ("PROD-C208", "Casual Graphic T-Shirt", 24.99),
    ],
    "Home & Kitchen": [
        ("PROD-H301", "Programmable Espresso Coffee Maker", 129.99),
        ("PROD-H302", "Non-Stick Ceramic Cookware Set 10pc", 119.99),
        ("PROD-H303", "Stainless Steel High-Speed Blender", 79.99),
        ("PROD-H304", "Robot Vacuum Cleaner Smart Mapping", 299.99),
        ("PROD-H305", "Air Fryer Max XL 5.8-Quart", 99.99),
        ("PROD-H306", "Microfiber Luxury Bed Sheet Set", 39.99),
        ("PROD-H307", "Electric Kettle 1.7L", 34.99),
    ],
    "Beauty & Personal Care": [
        ("PROD-B401", "Hydrating Facial Moisturizer Cream", 28.50),
        ("PROD-B402", "Organic Argan Hair Care Shampoo", 18.99),
        ("PROD-B403", "Electric Sonic Toothbrush", 69.99),
        ("PROD-B404", "Vitamin C Radiance Face Serum", 35.00),
        ("PROD-B405", "Mineral Sunscreen SPF 50+", 22.50),
    ],
    "Sports & Outdoors": [
        ("PROD-S501", "Anti-Slip High-Density Yoga Mat", 29.99),
        ("PROD-S502", "Adjustable Cast Iron Dumbbell Set", 119.99),
        ("PROD-S503", "Insulated Stainless Steel Water Bottle", 19.99),
        ("PROD-S504", "Camping 4-Person Waterproof Tent", 159.99),
        ("PROD-S505", "Trail Running Hydration Backpack", 54.99),
    ]
}

STORES = [
    ("STR-101", "New York", "NY", "East"),
    ("STR-102", "Boston", "MA", "East"),
    ("STR-103", "Chicago", "IL", "Central"),
    ("STR-104", "Dallas", "TX", "Central"),
    ("STR-105", "Atlanta", "GA", "South"),
    ("STR-106", "Miami", "FL", "South"),
    ("STR-107", "Los Angeles", "CA", "West"),
    ("STR-108", "San Francisco", "CA", "West"),
    ("STR-109", "Seattle", "WA", "West"),
    ("STR-110", "Denver", "CO", "West"),
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI / Cash App", "PayPal", "Cash"]
GENDERS = ["Male", "Female", "Other"]

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def generate_base_records(n=5000):
    records = []
    customer_ids = [f"CUST-{i:04d}" for i in range(1, 1201)]
    
    for i in range(1, n + 1):
        tx_id = f"TXN-{i:06d}"
        cust_id = random.choice(customer_ids)
        gender = random.choice(GENDERS)
        age = random.randint(18, 70)
        
        # Pick category & product
        cat = random.choice(list(PRODUCT_CATALOG.keys()))
        prod = random.choice(PRODUCT_CATALOG[cat])
        prod_id, prod_name, unit_price = prod
        
        quantity = random.choices([1, 2, 3, 4, 5, 6, 8, 10], weights=[45, 25, 12, 8, 5, 2, 2, 1])[0]
        discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20, 0.25], weights=[50, 15, 15, 10, 7, 3])[0]
        
        gross = round(quantity * unit_price, 2)
        total_amount = round(gross * (1 - discount), 2)
        
        dt = random_date(START_DATE, END_DATE)
        date_str = dt.strftime("%Y-%m-%d")
        
        store = random.choice(STORES)
        store_id, city, state, region = store
        payment = random.choice(PAYMENT_METHODS)
        
        records.append({
            "Transaction_ID": tx_id,
            "Date": date_str,
            "Customer_ID": cust_id,
            "Gender": gender,
            "Age": age,
            "Product_Category": cat,
            "Product_ID": prod_id,
            "Product_Name": prod_name,
            "Quantity": quantity,
            "Price_Per_Unit": unit_price,
            "Discount_Pct": discount,
            "Total_Amount": total_amount,
            "Payment_Method": payment,
            "Store_ID": store_id,
            "City": city,
            "State": state,
            "Region": region
        })
    return records

def inject_anomalies(records):
    """Inject dirty data to simulate Kaggle real-world issues matching test cases."""
    print("Injecting synthetic anomalies into raw dataset...")
    
    # 1. Null / Missing rows & columns (~60 rows)
    for _ in range(20):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Customer_ID"] = np.nan
    for _ in range(15):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Gender"] = ""
    for _ in range(15):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Product_Category"] = None
    for _ in range(15):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Total_Amount"] = np.nan
        
    # 2. Date format errors & edge cases (~90 rows)
    for _ in range(35):
        idx = random.randint(0, len(records) - 1)
        dt_val = records[idx]["Date"]
        if isinstance(dt_val, str) and "-" in dt_val:
            try:
                y, m, d = dt_val.split("-")
                records[idx]["Date"] = f"{d}/{m}/{y}"  # British DD/MM/YYYY
            except:
                pass
    for _ in range(35):
        idx = random.randint(0, len(records) - 1)
        dt_val = records[idx]["Date"]
        if isinstance(dt_val, str) and "-" in dt_val:
            try:
                y, m, d = dt_val.split("-")
                records[idx]["Date"] = f"{m}-{d}-{y}"  # US MM-DD-YYYY
            except:
                pass
    for _ in range(15):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Date"] = "2024-02-31"  # Invalid date
    for _ in range(8):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Date"] = "   "  # Whitespace / Missing date
        
    # 3. Negative quantities and amounts (Returns / human entry errors) (~50 rows)
    for _ in range(25):
        idx = random.randint(0, len(records) - 1)
        records[idx]["Quantity"] = -abs(int(records[idx]["Quantity"]))
        records[idx]["Total_Amount"] = -abs(float(records[idx]["Total_Amount"]) if pd.notnull(records[idx]["Total_Amount"]) else 50.0)
    for _ in range(25):
        idx = random.randint(0, len(records) - 1)
        if pd.notnull(records[idx]["Total_Amount"]):
            records[idx]["Total_Amount"] = -round(abs(float(records[idx]["Total_Amount"])), 2)

    # 4. Inconsistent text formatting (case / trailing spaces) (~50 rows)
    for _ in range(30):
        idx = random.randint(0, len(records) - 1)
        cat = str(records[idx]["Product_Category"])
        if cat and cat != "None":
            records[idx]["Product_Category"] = f"  {cat.lower()}  " if random.random() < 0.5 else cat.upper()
    for _ in range(20):
        idx = random.randint(0, len(records) - 1)
        reg = str(records[idx]["Region"])
        records[idx]["Region"] = f" {reg.strip()} "
        
    # 5. Calculation mismatch (Total_Amount != Quantity * Unit_Price * (1 - Discount)) (~30 rows)
    for _ in range(30):
        idx = random.randint(0, len(records) - 1)
        if pd.notnull(records[idx]["Total_Amount"]) and records[idx]["Quantity"] > 0:
            records[idx]["Total_Amount"] = round(float(records[idx]["Total_Amount"]) + random.choice([15.50, 42.00, -25.00]), 2)
            
    # 6. Duplicates: Exact duplicate rows (~40 rows)
    dup_rows = [dict(records[random.randint(0, 500)]) for _ in range(40)]
    records.extend(dup_rows)
    
    # 7. Duplicate Transaction IDs with differing details (~15 rows)
    for _ in range(15):
        target = dict(records[random.randint(0, 500)])
        target["Total_Amount"] = 999.99
        records.append(target)
        
    return records

def main():
    print("Generating base retail transactions (5,000 records)...")
    base_records = generate_base_records(5000)
    dirty_records = inject_anomalies(base_records)
    
    df = pd.DataFrame(dirty_records)
    df.to_csv(RAW_FILE_PATH, index=False)
    print(f"Successfully generated raw dataset: {RAW_FILE_PATH}")
    print(f"Total raw rows: {len(df)}")
    print(f"Raw shape: {df.shape}")

if __name__ == "__main__":
    main()
