import csv
import re
import os

def load_db_customers(sql_path):
    customers = set()
    content = ""
    try:
        with open(sql_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(sql_path, 'r', encoding='cp932', errors='replace') as f:
            content = f.read()
            
    for line in content.splitlines():
        match = re.search(r"VALUES\s*\('([^']+)'", line)
        if match:
            customers.add(match.group(1))
    return customers

def find_mismatches(csv_path, db_customers):
    mismatches = set()
    
    lines = []
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(csv_path, 'r', encoding='cp932', errors='replace') as f:
            lines = f.readlines()

    reader = csv.DictReader(lines)
    
    for row in reader:
        customer_name = row.get('customer') or row.get('Customer')
        if not customer_name:
            continue
            
        stripped_name = customer_name.strip()
        
        # Check if the stripped name exists in DB
        if stripped_name not in db_customers:
            # Check if the raw name exists (for cases like leading spaces)
            if customer_name not in db_customers:
                mismatches.add(customer_name)
                
    print("--- Mismatched Customers ---")
    for name in sorted(mismatches):
        print(f"'{name}'")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, 'import_customers.sql')
    csv_path = os.path.join(base_dir, 'product-list.csv')
    
    print(f"Loading customers from {sql_path}...")
    db_customers = load_db_customers(sql_path)
    print(f"Found {len(db_customers)} customers in DB.")
    
    print(f"Checking mismatches in {csv_path}...")
    find_mismatches(csv_path, db_customers)
