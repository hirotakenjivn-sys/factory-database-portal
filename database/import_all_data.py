#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合インポートスクリプト
CSV → SQL変換（Customer, Employee, Product, Process Names, Machine List）
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
    return value.replace("'", "''")


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


def generate_machine_list():
    """機械リストSQL生成（新スキーマ対応）"""
    inserts = ["-- ========== Machine List =========="]

    machines = [
        # Main Factory - PRESS
        (1, 'PRESS-001', 'PRESS'), (1, 'PRESS-002', 'PRESS'),
        (1, 'PRESS-003', 'PRESS'), (1, 'PRESS-004', 'PRESS'),
        (1, 'PRESS-005', 'PRESS'), (1, 'PRESS-006', 'PRESS'),
        (1, 'PRESS-007', 'PRESS'), (1, 'PRESS-008', 'PRESS'),
        # Main Factory - TAP
        (1, 'TAP-001', 'TAP'), (1, 'TAP-002', 'TAP'),
        (1, 'TAP-003', 'TAP'), (1, 'TAP-004', 'TAP'),
        (1, 'TAP-005', 'TAP'), (1, 'TAP-006', 'TAP'),
        # Main Factory - BARREL
        (1, 'BARREL-001', 'BARREL'), (1, 'BARREL-002', 'BARREL'),
        (1, 'BARREL-003', 'BARREL'), (1, 'BARREL-004', 'BARREL'),
        (1, 'BARREL-005', 'BARREL'), (1, 'BARREL-006', 'BARREL'),
        # Sub Factory - PRESS
        (2, 'PRESS-S001', 'PRESS'), (2, 'PRESS-S002', 'PRESS'),
        (2, 'PRESS-S003', 'PRESS'), (2, 'PRESS-S004', 'PRESS'),
        # Sub Factory - TAP
        (2, 'TAP-S001', 'TAP'), (2, 'TAP-S002', 'TAP'), (2, 'TAP-S003', 'TAP'),
        # Sub Factory - BARREL
        (2, 'BARREL-S001', 'BARREL'), (2, 'BARREL-S002', 'BARREL'), (2, 'BARREL-S003', 'BARREL'),
    ]

    print("Processing Machine List (embedded data)")
    for factory_id, machine_no, machine_type in machines:
        sql = f"INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`) SELECT {factory_id}, '{machine_no}', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = '{machine_type}';"
        inserts.append(sql)

    print(f"  → {len(machines)} machines")
    return inserts


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # CSVファイルパス
    customer_csv = os.path.join(base_dir, 'シードデータ - Customer.csv')
    employee_csv = os.path.join(base_dir, 'シードデータ - employee.csv')
    product_csv = os.path.join(base_dir, 'product-list2.csv')

    # 出力ファイル
    output_sql = os.path.join(base_dir, 'import_all_data.sql')

    print("=" * 50)
    print("統合インポートスクリプト")
    print("=" * 50)

    all_inserts = []
    all_inserts.append("-- Generated by import_all_data.py")
    all_inserts.append("-- 統合シードデータ（Customer, Employee, Product, Process Names, Machine List）")
    all_inserts.append("SET NAMES utf8mb4;")
    all_inserts.append("USE factory_db;")
    all_inserts.append("")

    # 各データ生成
    all_inserts.extend(generate_customers(customer_csv))
    all_inserts.append("")
    all_inserts.extend(generate_employees(employee_csv))
    all_inserts.append("")
    all_inserts.extend(generate_products(product_csv))
    all_inserts.append("")
    all_inserts.extend(generate_process_names())
    all_inserts.append("")
    all_inserts.extend(generate_machine_list())

    # ファイル出力
    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_inserts))
        f.write('\n')

    print("=" * 50)
    print(f"完了: {output_sql}")
    print("=" * 50)


if __name__ == "__main__":
    main()
