#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合インポートスクリプト
全シードデータCSV → SQL変換
"""
import os
import sys
import csv

# UTF-8出力設定
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def read_csv_robust(file_path):
    """複数のエンコーディングを試してCSVを読み込む"""
    encodings = ['utf-8-sig', 'utf-8', 'cp932', 'windows-1258']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
    # フォールバック
    print(f"Warning: {file_path} のエンコーディング検出失敗。cp932で読み込み。")
    with open(file_path, 'r', encoding='cp932', errors='replace') as f:
        return f.readlines()


def escape_sql(value):
    """SQLエスケープ"""
    if value is None:
        return ''
    return str(value).replace("'", "''")


def generate_factories(csv_path):
    """工場データSQL生成"""
    inserts = ["-- ========== Factories =========="]
    inserts.append("DELETE FROM factories;")
    inserts.append("ALTER TABLE factories AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Factories: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        factory_id = row.get('Factory ID', '').strip()
        factory_name = row.get('Factory Name', '').strip()
        if factory_id and factory_name:
            safe_name = escape_sql(factory_name)
            sql = f"INSERT INTO factories (factory_id, factory_name, user) VALUES ({factory_id}, '{safe_name}', 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} factories")
    return inserts


def generate_machine_types(csv_path):
    """機械種類データSQL生成"""
    inserts = ["-- ========== Machine Types =========="]
    inserts.append("DELETE FROM machine_types;")
    inserts.append("ALTER TABLE machine_types AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Machine Types: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        machine_type = row.get('Machine Type', '').strip()
        if machine_type:
            safe_type = escape_sql(machine_type)
            sql = f"INSERT INTO machine_types (machine_type_name, user) VALUES ('{safe_type}', 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} machine types")
    return inserts


def generate_machine_list(csv_path):
    """機械リストSQL生成"""
    inserts = ["-- ========== Machine List =========="]
    inserts.append("DELETE FROM machine_list;")
    inserts.append("ALTER TABLE machine_list AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Machine List: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        machine_no = row.get('Machine No', '').strip()
        factory_name = row.get('Factory Name', '').strip()
        machine_type = row.get('Machine Type', '').strip()

        if machine_no and factory_name and machine_type:
            safe_type = escape_sql(machine_type)
            safe_factory = escape_sql(factory_name)
            sql = f"INSERT INTO machine_list (machine_no, factory_id, machine_type_id, user) SELECT '{machine_no}', f.factory_id, mt.machine_type_id, 'admin' FROM factories f, machine_types mt WHERE f.factory_name = '{safe_factory}' AND mt.machine_type_name = '{safe_type}';"
            inserts.append(sql)
            count += 1

    print(f"  → {count} machines")
    return inserts


def generate_holiday_types(csv_path):
    """休日タイプSQL生成"""
    inserts = ["-- ========== Holiday Types =========="]
    inserts.append("DELETE FROM holiday_types;")
    inserts.append("ALTER TABLE holiday_types AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Holiday Types: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        holiday_type = row.get('Holiday Type', '').strip()
        if holiday_type:
            safe_type = escape_sql(holiday_type)
            sql = f"INSERT INTO holiday_types (date_type) VALUES ('{safe_type}');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} holiday types")
    return inserts


def generate_holidays(csv_path):
    """カレンダー（休日）SQL生成"""
    inserts = ["-- ========== Calendar (Holidays) =========="]
    inserts.append("DELETE FROM calendar;")
    inserts.append("ALTER TABLE calendar AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Holidays: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        date_str = row.get('Date', '').strip()
        day_off = row.get('Day Off', '').strip()

        if date_str and day_off:
            # DD/MM/YYYY → YYYY-MM-DD
            try:
                parts = date_str.split('/')
                if len(parts) == 3:
                    formatted_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                else:
                    formatted_date = date_str
            except:
                formatted_date = date_str

            safe_day_off = escape_sql(day_off)
            sql = f"INSERT INTO calendar (date_holiday, holiday_type_id, user) SELECT '{formatted_date}', ht.holiday_type_id, 'admin' FROM holiday_types ht WHERE ht.date_type = '{safe_day_off}';"
            inserts.append(sql)
            count += 1

    print(f"  → {count} holidays")
    return inserts


def generate_material_rates(csv_path):
    """材料レートSQL生成"""
    inserts = ["-- ========== Material Rates =========="]
    inserts.append("DELETE FROM material_rates;")
    inserts.append("ALTER TABLE material_rates AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Material Rates: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        product = row.get('Product', '').strip()
        thickness = row.get('Thickness', '').strip()
        width = row.get('Width', '').strip()
        pitch = row.get('Pitch', '').strip()
        h = row.get('h', '').strip()

        if product and thickness and width and pitch:
            safe_product = escape_sql(product)
            # hが空の場合はNULL
            h_value = h if h else 'NULL'

            sql = f"INSERT INTO material_rates (product_id, thickness, width, pitch, h, user) SELECT p.product_id, {thickness}, {width}, {pitch}, {h_value}, 'admin' FROM products p WHERE p.product_code = '{safe_product}';"
            inserts.append(sql)
            count += 1

    print(f"  → {count} material rates")
    return inserts


def generate_customers(csv_path):
    """顧客データSQL生成"""
    inserts = ["-- ========== Customers =========="]

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Customers: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        name = row.get('Customer')
        if name:
            name = name.strip()
            safe_name = escape_sql(name)
            sql = f"INSERT IGNORE INTO customers (customer_name, is_active, user) VALUES ('{safe_name}', 1, 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} customers")
    return inserts


def generate_employees(csv_path):
    """従業員データSQL生成"""
    inserts = ["-- ========== Employees =========="]

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Employees: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        full_name = row.get('FULL NAME')
        member_id = row.get('MEMBER ID')

        if full_name and member_id:
            full_name = full_name.strip()
            member_id = member_id.strip()
            safe_name = escape_sql(full_name)
            safe_id = escape_sql(member_id)
            sql = f"INSERT IGNORE INTO employees (employee_no, name, is_active, user) VALUES ('{safe_id}', '{safe_name}', 1, 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} employees")
    return inserts


def generate_products(csv_path):
    """製品データSQL生成"""
    inserts = ["-- ========== Products =========="]

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Products: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    # 文字化け修正マッピング
    CORRECTIONS = {
        'C\ue31eg ty TNHH NIDEC ADVANCED MOTOR (VI?T NAM)': 'Công ty TNHH NIDEC ADVANCED MOTOR (VIỆT NAM)',
        'CﾔNG TY TNHH WAKYO MAGALL': 'CÔNG TY TNHH WAKYO MAGALL',
        'HOﾀNG NGUYﾊN': 'HOÀNG NGUYÊN',
        'NISSEI M? THO': 'NISSEI MỸ THO',
        'NISSEI TH? ﾐ?C': 'NISSEI THỦ ĐỨC',
        'SA`I GO`N PRECISION': 'SÀI GÒN PRECISION',
        'SHARP(Vi?t nam)': 'SHARP(Việt nam)',
        'YUWA VI?T NAM': 'YUWA VIỆT NAM',
    }

    count = 0
    for row in reader:
        customer_name = row.get('customer') or row.get('Customer')
        product_code = row.get('Product') or row.get('product')

        if not customer_name or not product_code:
            continue

        customer_name = customer_name.strip()
        product_code = product_code.strip()

        # 文字化け修正
        if customer_name in CORRECTIONS:
            customer_name = CORRECTIONS[customer_name]

        safe_code = escape_sql(product_code)
        safe_customer = escape_sql(customer_name)

        sql = f"INSERT INTO products (product_code, customer_id, is_active, user) SELECT '{safe_code}', customer_id, 1, 'admin' FROM customers WHERE customer_name = '{safe_customer}' AND NOT EXISTS (SELECT 1 FROM products WHERE product_code = '{safe_code}') LIMIT 1;"
        inserts.append(sql)
        count += 1

    print(f"  → {count} products")
    return inserts


def generate_process_names():
    """工程名マスタSQL生成"""
    inserts = ["-- ========== Process Name Types =========="]
    inserts.append("DELETE FROM process_name_types;")
    inserts.append("ALTER TABLE process_name_types AUTO_INCREMENT = 1;")

    # 工程名データ（タブ区切り: 名前\tタイプ）
    data = [
        ("CNC", "DAY"), ("ĐÓNG GÓI", "DAY"), ("HẠ NHIỆT", "DAY"),
        ("LÀM SẠCH SP", "DAY"), ("NHIỆT LUYỆN", "DAY"), ("NHUỘM ĐEN", "DAY"),
        ("QUAY BÓNG", "DAY"), ("RỬA", "DAY"), ("RỬA SẠCH DẦU", "DAY"),
        ("RUNG BAVIA", "DAY"), ("RUNG BÓNG", "DAY"), ("RUNG SẠCH", "DAY"),
        ("RUNG TẨY DẦU", "DAY"), ("RUNG TẨY TRẮNG", "DAY"), ("SƠN", "DAY"),
        ("IN CHỮ", "DAY"), ("TẨY TRẮNG", "DAY"), ("XI MẠ", "DAY"),
        ("THỬ ỐC 100%", "SPM"), ("VÉT BAVIA LỖ", "SPM"), ("TÁN", "SPM"),
        ("XỬ LÝ BAVIA", "SPM"), ("XỬ LÝ CONG", "SPM"), ("XỬ LÝ MẶT PHẲNG", "SPM"),
        ("XỬ LÝ MÀI CẠNH", "SPM"), ("XỬ LÝ SẠCH SP", "SPM"),
        ("DẬP 1/1", "SPM"), ("DẬP 1/2", "SPM"), ("DẬP 2/2", "SPM"),
        ("DẬP 1/3", "SPM"), ("DẬP 2/3", "SPM"), ("DẬP 3/3", "SPM"),
        ("DẬP 1/4", "SPM"), ("DẬP 2/4", "SPM"), ("DẬP 3/4", "SPM"), ("DẬP 4/4", "SPM"),
        ("DẬP 1/5", "SPM"), ("DẬP 2/5", "SPM"), ("DẬP 3/5", "SPM"), ("DẬP 4/5", "SPM"), ("DẬP 5/5", "SPM"),
        ("DẬP 1/6", "SPM"), ("DẬP 2/6", "SPM"), ("DẬP 3/6", "SPM"), ("DẬP 4/6", "SPM"), ("DẬP 5/6", "SPM"), ("DẬP 6/6", "SPM"),
        ("DẬP 1/7", "SPM"), ("DẬP 2/7", "SPM"), ("DẬP 3/7", "SPM"), ("DẬP 4/7", "SPM"), ("DẬP 5/7", "SPM"), ("DẬP 6/7", "SPM"), ("DẬP 7/7", "SPM"),
        ("DẬP 1/8", "SPM"), ("DẬP 2/8", "SPM"), ("DẬP 3/8", "SPM"), ("DẬP 4/8", "SPM"), ("DẬP 5/8", "SPM"), ("DẬP 6/8", "SPM"), ("DẬP 7/8", "SPM"), ("DẬP 8/8", "SPM"),
        ("TARO 1/1", "SPM"), ("TARO 1/2", "SPM"), ("TARO 1/3", "SPM"), ("TARO 1/4", "SPM"),
        ("TARO 2/2", "SPM"), ("TARO 2/3", "SPM"), ("TARO 2/4", "SPM"),
        ("TARO 3/3", "SPM"), ("TARO 3/4", "SPM"), ("TARO 4/4", "SPM"),
    ]

    print("Processing Process Names (embedded data)")
    for name, type_str in data:
        day_or_spm = 1 if type_str == 'SPM' else 0
        name_escaped = escape_sql(name)
        sql = f"INSERT INTO process_name_types (process_name, day_or_spm, user) VALUES ('{name_escaped}', {day_or_spm}, 'admin');"
        inserts.append(sql)

    print(f"  → {len(data)} process names")
    return inserts


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # CSVファイルパス
    factories_csv = os.path.join(base_dir, 'シードデータ - Factories.csv')
    machine_types_csv = os.path.join(base_dir, 'シードデータ - MachineTypes.csv')
    machine_list_csv = os.path.join(base_dir, 'シードデータ - Machine-list.csv')
    holiday_types_csv = os.path.join(base_dir, 'シードデータ - HolidayTypes.csv')
    holidays_csv = os.path.join(base_dir, 'シードデータ - Holidays.csv')
    material_rates_csv = os.path.join(base_dir, 'シードデータ - MaterialRates.csv')
    customer_csv = os.path.join(base_dir, 'シードデータ - Customer.csv')
    employee_csv = os.path.join(base_dir, 'シードデータ - employee.csv')
    product_csv = os.path.join(base_dir, 'シードデータ - product.csv')

    # 出力ファイル
    output_sql = os.path.join(base_dir, 'import_all_data.sql')

    print("=" * 60)
    print("統合インポートスクリプト - 全シードデータCSV対応")
    print("=" * 60)

    all_inserts = []
    all_inserts.append("-- Generated by import_all_data.py")
    all_inserts.append("-- 統合シードデータ（全テーブル）")
    all_inserts.append("SET NAMES utf8mb4;")
    all_inserts.append("USE factory_db;")
    all_inserts.append("")

    # マスタテーブル（依存関係順）
    all_inserts.extend(generate_factories(factories_csv))
    all_inserts.append("")
    all_inserts.extend(generate_machine_types(machine_types_csv))
    all_inserts.append("")
    all_inserts.extend(generate_machine_list(machine_list_csv))
    all_inserts.append("")
    all_inserts.extend(generate_holiday_types(holiday_types_csv))
    all_inserts.append("")
    all_inserts.extend(generate_holidays(holidays_csv))
    all_inserts.append("")
    all_inserts.extend(generate_material_rates(material_rates_csv))
    all_inserts.append("")
    all_inserts.extend(generate_customers(customer_csv))
    all_inserts.append("")
    all_inserts.extend(generate_employees(employee_csv))
    all_inserts.append("")
    all_inserts.extend(generate_products(product_csv))
    all_inserts.append("")
    all_inserts.extend(generate_process_names())

    # ファイル出力
    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_inserts))
        f.write('\n')

    print("=" * 60)
    print(f"完了: {output_sql}")
    print("=" * 60)


if __name__ == "__main__":
    main()
