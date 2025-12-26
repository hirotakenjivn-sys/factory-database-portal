import os

def check_sql_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for line in content.splitlines():
        if 'NISSEI MỸ THO' in line or 'NISSEI THỦ ĐỨC' in line or 'SHARP(Việt nam)' in line:
            print(f"Found corrected: {line.strip()}")
        elif 'NISSEI M? THO' in line:
            print(f"Found corrupted (BAD): {line.strip()}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, 'import_products.sql')
    check_sql_content(sql_path)
