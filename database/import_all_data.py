#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合インポートスクリプト
CSV → SQL変換（Customer, Employee, Product, Process Names, Machine List）
"""

import csv
import os
import sys

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


def generate_factories(csv_path):
    """工場データSQL生成"""
    inserts = ["-- ========== Factories =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM factories;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Factories: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        factory_id = row.get('Factory ID')
        factory_name = row.get('Factory Name')

        if factory_id and factory_name:
            factory_id = factory_id.strip()
            factory_name = factory_name.strip()
            safe_name = escape_sql(factory_name)
            sql = f"INSERT INTO factories (factory_id, factory_name, user) VALUES ({factory_id}, '{safe_name}', 'system');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} factories")
    return inserts


def generate_machine_types(csv_path):
    """機械タイプデータSQL生成"""
    inserts = ["-- ========== Machine Types =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM machine_types;")
    inserts.append("ALTER TABLE machine_types AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Machine Types: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    seen = set()
    count = 0
    for row in reader:
        machine_type = row.get('Machine Type')

        if machine_type:
            machine_type = machine_type.strip()
            if machine_type in seen:
                continue
            seen.add(machine_type)
            safe_type = escape_sql(machine_type)
            sql = f"INSERT INTO machine_types (machine_type_name, user) VALUES ('{safe_type}', 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} machine types")
    return inserts


def generate_holiday_types(csv_path):
    """休日種別データSQL生成"""
    inserts = ["-- ========== Holiday Types =========="]
    inserts.append("-- 既存データを削除")
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
        holiday_type = row.get('Holiday Type')

        if holiday_type:
            holiday_type = holiday_type.strip()
            safe_type = escape_sql(holiday_type)
            sql = f"INSERT INTO holiday_types (date_type) VALUES ('{safe_type}');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} holiday types")
    return inserts


def generate_material_rates(csv_path):
    """材料レートデータSQL生成"""
    inserts = ["-- ========== Material Rates =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM material_rates;")
    inserts.append("ALTER TABLE material_rates AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Material Rates: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    seen = set()
    count = 0
    for row in reader:
        product_code = row.get('Product')
        thickness = row.get('Thickness', '0')
        width = row.get('Width', '0')
        pitch = row.get('Pitch', '0')
        h = row.get('h', '0')

        if not product_code:
            continue

        product_code = product_code.strip()

        # 重複チェック
        if product_code in seen:
            continue
        seen.add(product_code)

        safe_code = escape_sql(product_code)

        # product_idをproductsテーブルから取得
        sql = f"INSERT INTO material_rates (product_id, thickness, width, pitch, h, user) SELECT product_id, {thickness}, {width}, {pitch}, {h}, 'admin' FROM products WHERE product_code = '{safe_code}' LIMIT 1;"
        inserts.append(sql)
        count += 1

    print(f"  → {count} material rates (重複排除済み)")
    return inserts


def generate_calendar(csv_path):
    """カレンダー（休日）データSQL生成"""
    inserts = ["-- ========== Calendar (Holidays) =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM calendar;")
    inserts.append("ALTER TABLE calendar AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Calendar: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        date_str = row.get('Date')
        day_off = row.get('Day Off')

        if date_str and day_off:
            date_str = date_str.strip()
            day_off = day_off.strip()

            # DD/MM/YYYY → YYYY-MM-DD に変換
            parts = date_str.split('/')
            if len(parts) == 3:
                date_sql = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                continue

            safe_day_off = escape_sql(day_off)
            # holiday_type_id = 1 (Ngày Nghỉ)
            sql = f"INSERT INTO calendar (date_holiday, holiday_type_id, user) VALUES ('{date_sql}', 1, 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} calendar entries")
    return inserts


def generate_customers(csv_path):
    """顧客データSQL生成（重複排除）"""
    inserts = ["-- ========== Customers =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM customers;")
    inserts.append("ALTER TABLE customers AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Customers: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    seen = set()
    count = 0
    for row in reader:
        name = row.get('Customer')
        if name:
            name = name.strip()
            if name in seen:
                continue
            seen.add(name)
            safe_name = escape_sql(name)
            sql = f"INSERT INTO customers (customer_name, is_active, user) VALUES ('{safe_name}', 1, 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} customers (重複排除済み)")
    return inserts


def generate_employees(csv_path):
    """従業員データSQL生成（重複排除、admin含む）"""
    inserts = ["-- ========== Employees =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM employees;")
    inserts.append("ALTER TABLE employees AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    print(f"Processing Employees: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    seen = set()
    count = 0
    for row in reader:
        full_name = row.get('FULL NAME')
        member_id = row.get('MEMBER ID')
        password_hash = row.get('PASSWORD_HASH', '')

        if full_name and member_id:
            full_name = full_name.strip()
            member_id = member_id.strip()
            password_hash = password_hash.strip() if password_hash else ''

            if member_id in seen:
                continue
            seen.add(member_id)

            safe_name = escape_sql(full_name)
            safe_id = escape_sql(member_id)

            if password_hash:
                # adminなどパスワード付きユーザー
                safe_hash = escape_sql(password_hash)
                sql = f"INSERT INTO employees (employee_no, name, password_hash, is_active, user) VALUES ('{safe_id}', '{safe_name}', '{safe_hash}', 1, 'system');"
            else:
                # 通常の従業員
                sql = f"INSERT INTO employees (employee_no, name, is_active, user) VALUES ('{safe_id}', '{safe_name}', 1, 'admin');"
            inserts.append(sql)
            count += 1

    print(f"  → {count} employees (重複排除済み)")
    return inserts


def generate_products(csv_path):
    """製品データSQL生成（重複排除）"""
    inserts = ["-- ========== Products =========="]
    inserts.append("-- 既存データを削除")
    inserts.append("DELETE FROM products;")
    inserts.append("ALTER TABLE products AUTO_INCREMENT = 1;")

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

    seen = set()
    count = 0
    for row in reader:
        customer_name = row.get('customer') or row.get('Customer')
        product_code = row.get('Product') or row.get('product')

        if not customer_name or not product_code:
            continue

        customer_name = customer_name.strip()
        product_code = product_code.strip()

        # product_codeで重複チェック
        if product_code in seen:
            continue
        seen.add(product_code)

        # 文字化け修正
        if customer_name in CORRECTIONS:
            customer_name = CORRECTIONS[customer_name]

        safe_code = escape_sql(product_code)
        safe_customer = escape_sql(customer_name)

        sql = f"INSERT INTO products (product_code, customer_id, is_active, user) SELECT '{safe_code}', customer_id, 1, 'admin' FROM customers WHERE customer_name = '{safe_customer}' LIMIT 1;"
        inserts.append(sql)
        count += 1

    print(f"  → {count} products (重複排除済み)")
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


def generate_machine_list(csv_path):
    """機械リストSQL生成（CSVから読み込み）"""
    inserts = ["-- ========== Machine List =========="]
    inserts.append("-- 過去のデータを削除")
    inserts.append("DELETE FROM `machine_list`;")
    inserts.append("ALTER TABLE `machine_list` AUTO_INCREMENT = 1;")

    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} が見つかりません。スキップします。")
        return inserts

    # 工場名 → factory_id マッピング
    FACTORY_MAP = {
        'X1': 1,
        'X2': 2,
    }

    print(f"Processing Machine List: {csv_path}")
    lines = read_csv_robust(csv_path)
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        machine_no = row.get('Machine No')
        factory_name = row.get('Factory Name')
        machine_type = row.get('Machine Type')

        if not machine_no or not factory_name or not machine_type:
            continue

        machine_no = machine_no.strip()
        factory_name = factory_name.strip()
        machine_type = machine_type.strip()

        factory_id = FACTORY_MAP.get(factory_name)
        if not factory_id:
            print(f"  Warning: Unknown factory '{factory_name}', skipping")
            continue

        safe_machine_no = escape_sql(machine_no)
        safe_machine_type = escape_sql(machine_type)

        sql = f"INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`) SELECT {factory_id}, '{safe_machine_no}', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = '{safe_machine_type}';"
        inserts.append(sql)
        count += 1

    print(f"  → {count} machines")
    return inserts


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # CSVファイルパス
    factory_csv = os.path.join(base_dir, 'シードデータ - Factories.csv')
    machine_type_csv = os.path.join(base_dir, 'シードデータ - MachineTypes.csv')
    holiday_type_csv = os.path.join(base_dir, 'シードデータ - HolidayTypes.csv')
    calendar_csv = os.path.join(base_dir, 'シードデータ - Holidays.csv')
    customer_csv = os.path.join(base_dir, 'シードデータ - Customer.csv')
    employee_csv = os.path.join(base_dir, 'シードデータ - employee.csv')
    product_csv = os.path.join(base_dir, 'product-list2.csv')
    machine_csv = os.path.join(base_dir, 'シードデータ - Machine-list.csv')
    material_rate_csv = os.path.join(base_dir, 'シードデータ - MaterialRates.csv')

    # 出力ファイル
    output_sql = os.path.join(base_dir, 'import_all_data.sql')

    print("=" * 50)
    print("統合インポートスクリプト")
    print("=" * 50)

    all_inserts = []
    all_inserts.append("-- Generated by import_all_data.py")
    all_inserts.append("-- 統合シードデータ（Customer, Employee, Product, Process Names, Machine List）")
    all_inserts.append("-- 重複排除済み・クリーンインポート")
    all_inserts.append("SET NAMES utf8mb4;")
    all_inserts.append("USE factory_db;")
    all_inserts.append("")
    all_inserts.append("-- 外部キー制約を一時的に無効化")
    all_inserts.append("SET FOREIGN_KEY_CHECKS = 0;")
    all_inserts.append("")

    # 各データ生成（依存関係順）
    # 1. 基本マスタ（他に依存しない）
    all_inserts.extend(generate_factories(factory_csv))
    all_inserts.append("")
    all_inserts.extend(generate_machine_types(machine_type_csv))
    all_inserts.append("")
    all_inserts.extend(generate_holiday_types(holiday_type_csv))
    all_inserts.append("")
    all_inserts.extend(generate_customers(customer_csv))
    all_inserts.append("")
    all_inserts.extend(generate_employees(employee_csv))
    all_inserts.append("")
    all_inserts.extend(generate_process_names())
    all_inserts.append("")
    # 2. 依存テーブル
    all_inserts.extend(generate_products(product_csv))
    all_inserts.append("")
    all_inserts.extend(generate_machine_list(machine_csv))
    all_inserts.append("")
    all_inserts.extend(generate_material_rates(material_rate_csv))
    all_inserts.append("")
    all_inserts.extend(generate_calendar(calendar_csv))
    all_inserts.append("")
    all_inserts.append("-- 外部キー制約を再有効化")
    all_inserts.append("SET FOREIGN_KEY_CHECKS = 1;")
    all_inserts.append("")
    all_inserts.append("-- 完了確認")
    all_inserts.append("SELECT 'factories' as tbl, COUNT(*) as cnt FROM factories")
    all_inserts.append("UNION ALL SELECT 'machine_types', COUNT(*) FROM machine_types")
    all_inserts.append("UNION ALL SELECT 'holiday_types', COUNT(*) FROM holiday_types")
    all_inserts.append("UNION ALL SELECT 'customers', COUNT(*) FROM customers")
    all_inserts.append("UNION ALL SELECT 'employees', COUNT(*) FROM employees")
    all_inserts.append("UNION ALL SELECT 'products', COUNT(*) FROM products")
    all_inserts.append("UNION ALL SELECT 'process_name_types', COUNT(*) FROM process_name_types")
    all_inserts.append("UNION ALL SELECT 'machine_list', COUNT(*) FROM machine_list")
    all_inserts.append("UNION ALL SELECT 'material_rates', COUNT(*) FROM material_rates")
    all_inserts.append("UNION ALL SELECT 'calendar', COUNT(*) FROM calendar;")

    # ファイル出力
    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_inserts))
        f.write('\n')

    print("=" * 50)
    print(f"完了: {output_sql}")
    print("=" * 50)


if __name__ == "__main__":
    main()
