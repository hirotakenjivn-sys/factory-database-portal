#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サンプルデータ生成スクリプト
各テーブルに約200件のサンプルデータを生成します
"""

import random
from datetime import datetime, timedelta

# 日本の企業名サンプル
COMPANY_NAMES = [
    'トヨタ自動車', 'ホンダ', '日産自動車', 'マツダ', 'スバル',
    'ダイハツ工業', 'スズキ', '三菱自動車', 'いすゞ自動車', '日野自動車',
    'パナソニック', 'ソニー', '東芝', '日立製作所', '富士通',
    'NEC', '三菱電機', 'シャープ', 'キヤノン', 'リコー',
    '村田製作所', 'キーエンス', 'オムロン', '日本電産', 'ファナック',
    'デンソー', 'アイシン', '豊田自動織機', 'ジェイテクト', 'KYB',
    '小糸製作所', 'スタンレー電気', '市光工業', '曙ブレーキ', 'ミツバ',
    'カルソニックカンセイ', 'ユニプレス', '日本精工', 'NTN', 'ジャパンマテックス',
]

# 日本の名前サンプル
LAST_NAMES = [
    '佐藤', '鈴木', '高橋', '田中', '渡辺', '伊藤', '山本', '中村', '小林', '加藤',
    '吉田', '山田', '佐々木', '山口', '松本', '井上', '木村', '林', '斎藤', '清水',
    '山崎', '森', '池田', '橋本', '阿部', '石川', '山下', '中島', '石井', '小川',
    '前田', '岡田', '長谷川', '藤田', '後藤', '近藤', '村上', '遠藤', '青木', '坂本',
]

FIRST_NAMES_MALE = [
    '太郎', '次郎', '三郎', '健一', '誠', '修', '勇', '聡', '隆', '浩',
    '和也', '拓也', '雅之', '正樹', '大輔', '翔太', '健太', '竜也', '直樹', '克也',
]

FIRST_NAMES_FEMALE = [
    '花子', '美咲', '愛', '優', '結衣', '陽菜', '美優', '莉子', '彩', '舞',
    '真由美', '由美子', '恵', '幸子', '明美', '久美子', '洋子', '良子', '綾', '静香',
]

# 工程名
PROCESS_NAMES = ['PRESS', 'TAPPING', 'PLATING', 'HEAT_TREATMENT', 'WELDING', 'ASSEMBLY', 'INSPECTION', 'PAINTING', 'ANODIZING', 'COATING', 'POLISHING']

# サプライヤーの業種
SUPPLIER_BUSINESSES = [
    'Metal Processing', 'Plastic Molding', 'Surface Treatment', 'Heat Treatment',
    'Machining', 'Casting', 'Forging', 'Plating', 'Coating', 'Assembly',
]

def generate_date_range(start_date, num_days):
    """日付範囲を生成"""
    base = datetime.strptime(start_date, '%Y-%m-%d')
    return [(base + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(num_days)]

def generate_customers(count=200):
    """顧客データ生成"""
    customers = []
    for i in range(count):
        company = random.choice(COMPANY_NAMES)
        suffix = ['株式会社', '工業株式会社', 'Co., Ltd.', 'Corporation', 'Industries'][i % 5]
        is_active = 'TRUE' if random.random() > 0.1 else 'FALSE'
        customers.append(f"('{company} {suffix} {i+1:03d}', {is_active}, 'admin')")
    return customers

def generate_products(count=200, customer_count=200):
    """製品データ生成"""
    products = []
    prefixes = ['TMC', 'HMC', 'NMC', 'MMC', 'SC', 'DMC', 'SMC', 'MMC', 'IMC', 'HMC']
    for i in range(count):
        prefix = prefixes[i % len(prefixes)]
        product_code = f"{prefix}-{i+1:04d}"
        customer_id = (i % customer_count) + 1
        is_active = 'TRUE' if random.random() > 0.15 else 'FALSE'
        products.append(f"('{product_code}', {customer_id}, {is_active}, 'admin')")
    return products

def generate_employees(count=200):
    """従業員データ生成"""
    employees = []
    for i in range(count):
        last_name = random.choice(LAST_NAMES)
        if i % 2 == 0:
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)
        emp_no = f"EMP{i+1:04d}"
        is_active = 'TRUE' if random.random() > 0.05 else 'FALSE'
        employees.append(f"('{emp_no}', '{last_name} {first_name}', {is_active}, 'admin')")
    return employees

def generate_suppliers(count=200):
    """サプライヤーデータ生成"""
    suppliers = []
    company_suffixes = ['Manufacturing', 'Industries', 'Components', 'Engineering', 'Tech']
    for i in range(count):
        suffix = company_suffixes[i % len(company_suffixes)]
        business = random.choice(SUPPLIER_BUSINESSES)
        suppliers.append(f"('Supplier {chr(65 + i % 26)}{i+1:03d} {suffix}', '{business}', 'admin')")
    return suppliers

def generate_processes(count=800, product_count=200):
    """工程データ生成

    SPM工程（PRESS）：rough_cycletime（秒）と setup_time（分）を設定
    DAY工程（その他）：rough_cycletime（日数）と production_limit（個数）を設定

    プレス工場のため、PRESS工程を60%程度含める
    PRESS X/Y がある場合、必ず 1/Y から Y/Y までの完全なセットが存在する
    """
    processes = []
    process_id = 1

    DAY_PROCESS_NAMES = ['TAPPING', 'PLATING', 'HEAT_TREATMENT', 'WELDING',
                         'ASSEMBLY', 'INSPECTION', 'PAINTING', 'ANODIZING',
                         'COATING', 'POLISHING']

    for product_id in range(1, product_count + 1):
        if process_id > count:
            break

        # 60%の確率でPRESS工程を含む製品
        has_press = random.random() < 0.6

        if has_press:
            # PRESS工程数を決定（2～5工程）
            num_press = random.randint(2, 5)
            process_no = 1

            # PRESS 1/X から X/X までの完全なセットを作成
            for i in range(1, num_press + 1):
                if process_id > count:
                    break
                process_name = f"PRESS {i}/{num_press}"
                rough_cycletime = round(random.uniform(50, 500), 2)
                setup_time = round(random.uniform(10, 120), 2)
                processes.append(f"({product_id}, {process_no}, '{process_name}', {rough_cycletime}, NULL, {setup_time}, 'admin')")
                process_no += 1
                process_id += 1

            # 残りの工程をDAY工程で埋める（1～3工程）
            num_day = random.randint(1, 3)
            for _ in range(num_day):
                if process_id > count:
                    break
                process_name = random.choice(DAY_PROCESS_NAMES)
                rough_cycletime = round(random.uniform(1, 7), 2)
                production_limit = random.randint(1000, 50000)
                processes.append(f"({product_id}, {process_no}, '{process_name}', {rough_cycletime}, {production_limit}, NULL, 'admin')")
                process_no += 1
                process_id += 1
        else:
            # DAY工程のみの製品（2～5工程）
            num_processes = random.randint(2, 5)
            for process_no in range(1, num_processes + 1):
                if process_id > count:
                    break
                process_name = random.choice(DAY_PROCESS_NAMES)
                rough_cycletime = round(random.uniform(1, 7), 2)
                production_limit = random.randint(1000, 50000)
                processes.append(f"({product_id}, {process_no}, '{process_name}', {rough_cycletime}, {production_limit}, NULL, 'admin')")
                process_id += 1

    return processes

def generate_po(count=150, product_count=200):
    """発注データ生成

    納期は今日から30～60日後
    """
    pos = []
    today = datetime.now()
    for i in range(count):
        po_number = f"PO-2025-{i+1:05d}"
        product_id = (i % product_count) + 1
        # 納期は今日から30～60日後
        delivery_date = (today + timedelta(days=random.randint(30, 60))).strftime('%Y-%m-%d')
        # PO受領日は今日から過去7～0日の範囲
        date_receive = (today + timedelta(days=random.randint(-7, 0))).strftime('%Y-%m-%d')
        quantity = random.randint(1000, 50000)
        pos.append(f"('{po_number}', {product_id}, '{delivery_date}', '{date_receive}', {quantity}, 'admin')")
    return pos

def generate_lots(count=200, product_count=200):
    """ロットデータ生成"""
    lots = []
    base_date = datetime(2025, 11, 1)
    for i in range(count):
        lot_number = f"LOT-2025-{i+1:05d}"
        product_id = (i % product_count) + 1
        date_created = (base_date + timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d')
        lots.append(f"('{lot_number}', {product_id}, '{date_created}', 'admin')")
    return lots

def generate_material_rates(count=200, product_count=200):
    """材料レートデータ生成"""
    materials = []
    for i in range(count):
        product_id = (i % product_count) + 1
        thickness = round(random.uniform(0.5, 5.0), 1)
        width = round(random.uniform(50.0, 300.0), 1)
        pitch = round(random.uniform(30.0, 150.0), 1)
        h = round(random.uniform(10.0, 50.0), 1)
        materials.append(f"({product_id}, {thickness}, {width}, {pitch}, {h}, 'admin')")
    return materials

def generate_spm(count=200, product_count=200):
    """SPM設定データ生成"""
    spms = []
    for i in range(count):
        product_id = (i % product_count) + 1
        process_no = random.randint(1, 3)
        press_no = random.randint(1, 5)
        cycle_time = round(random.uniform(100.0, 500.0), 2)
        spms.append(f"({product_id}, {process_no}, {press_no}, {cycle_time}, 'admin')")
    return spms

def generate_finished_products(count=200, product_count=200, lot_count=200):
    """完成品データ生成"""
    finished = []
    base_date = datetime(2025, 11, 1)
    for i in range(count):
        product_id = (i % product_count) + 1
        lot_id = (i % lot_count) + 1
        quantity = random.randint(500, 10000)
        date_finished = (base_date + timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')
        finished.append(f"({product_id}, {lot_id}, {quantity}, '{date_finished}', 'admin')")
    return finished

def generate_machine_list(count=200):
    """機械リストデータ生成"""
    machines = []
    for i in range(count):
        factory_id = (i % 10) + 1  # 10工場を想定
        machine_no = f"M-{i+1:04d}"
        machines.append(f"({factory_id}, '{machine_no}', 'admin')")
    return machines

def write_sql_file():
    """SQLファイルを生成"""
    with open('/workspace/factory-database-portal/database/seed.sql', 'w', encoding='utf-8') as f:
        f.write("""-- Sample Data for Development/Testing (200 records per table)
-- Factory Database Portal
-- Generated by generate_seed_data.py

SET NAMES utf8mb4;

""")

        # Customers
        f.write("-- ================================================\n")
        f.write("-- Customers (顧客) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `customers` (`customer_name`, `is_active`, `user`) VALUES\n")
        customers = generate_customers(200)
        f.write(',\n'.join(customers) + ';\n\n')

        # Products
        f.write("-- ================================================\n")
        f.write("-- Products (製品) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `products` (`product_code`, `customer_id`, `is_active`, `user`) VALUES\n")
        products = generate_products(200, 200)
        f.write(',\n'.join(products) + ';\n\n')

        # Employees
        f.write("-- ================================================\n")
        f.write("-- Employees (従業員) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `employees` (`employee_no`, `name`, `is_active`, `user`) VALUES\n")
        employees = generate_employees(200)
        f.write(',\n'.join(employees) + ';\n\n')

        # Suppliers
        f.write("-- ================================================\n")
        f.write("-- Suppliers (サプライヤー) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `suppliers` (`supplier_name`, `supplier_business`, `user`) VALUES\n")
        suppliers = generate_suppliers(200)
        f.write(',\n'.join(suppliers) + ';\n\n')

        # Process Name Types
        f.write("-- ================================================\n")
        f.write("-- Process Name Types (工程名マスタ)\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `process_name_types` (`process_name`, `day_or_spm`, `user`) VALUES\n")
        process_types = [
            "('PRESS', TRUE, 'admin')",
            "('PRESS 1/2', TRUE, 'admin')",
            "('PRESS 2/2', TRUE, 'admin')",
            "('PRESS 1/3', TRUE, 'admin')",
            "('PRESS 2/3', TRUE, 'admin')",
            "('PRESS 3/3', TRUE, 'admin')",
            "('PRESS 1/4', TRUE, 'admin')",
            "('PRESS 2/4', TRUE, 'admin')",
            "('PRESS 3/4', TRUE, 'admin')",
            "('PRESS 4/4', TRUE, 'admin')",
            "('PRESS 1/5', TRUE, 'admin')",
            "('PRESS 2/5', TRUE, 'admin')",
            "('PRESS 3/5', TRUE, 'admin')",
            "('PRESS 4/5', TRUE, 'admin')",
            "('PRESS 5/5', TRUE, 'admin')",
            "('TAPPING', FALSE, 'admin')",
            "('PLATING', FALSE, 'admin')",
            "('HEAT_TREATMENT', FALSE, 'admin')",
            "('WELDING', FALSE, 'admin')",
            "('ASSEMBLY', FALSE, 'admin')",
            "('INSPECTION', FALSE, 'admin')",
            "('PAINTING', FALSE, 'admin')",
            "('ANODIZING', FALSE, 'admin')",
            "('COATING', FALSE, 'admin')",
            "('POLISHING', FALSE, 'admin')"
        ]
        f.write(',\n'.join(process_types) + ';\n\n')

        # Processes
        f.write("-- ================================================\n")
        f.write("-- Processes (工程) - 800 records (60% PRESS with complete sequences)\n")
        f.write("-- SPM工程（PRESS）：rough_cycletime（秒）と setup_time（分）\n")
        f.write("-- DAY工程（その他）：rough_cycletime（日数）と production_limit（個数）\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `processes` (`product_id`, `process_no`, `process_name`, `rough_cycletime`, `production_limit`, `setup_time`, `user`) VALUES\n")
        processes = generate_processes(800, 200)
        f.write(',\n'.join(processes) + ';\n\n')

        # PO
        f.write("-- ================================================\n")
        f.write("-- PO (発注) - 150 records (delivery dates 30-60 days from today)\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `po` (`po_number`, `product_id`, `delivery_date`, `date_receive_po`, `po_quantity`, `user`) VALUES\n")
        pos = generate_po(150, 200)
        f.write(',\n'.join(pos) + ';\n\n')

        # Lot
        f.write("-- ================================================\n")
        f.write("-- Lot (ロット) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `lot` (`lot_number`, `product_id`, `date_created`, `user`) VALUES\n")
        lots = generate_lots(200, 200)
        f.write(',\n'.join(lots) + ';\n\n')

        # Material Rates
        f.write("-- ================================================\n")
        f.write("-- Material Rates (材料レート) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `material_rates` (`product_id`, `thickness`, `width`, `pitch`, `h`, `user`) VALUES\n")
        materials = generate_material_rates(200, 200)
        f.write(',\n'.join(materials) + ';\n\n')

        # SPM
        f.write("-- ================================================\n")
        f.write("-- SPM Settings (SPM設定) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `spm` (`product_id`, `process_no`, `press_no`, `cycle_time`, `user`) VALUES\n")
        spms = generate_spm(200, 200)
        f.write(',\n'.join(spms) + ';\n\n')

        # Calendar
        f.write("-- ================================================\n")
        f.write("-- Calendar (カレンダー) - 2025年の祝日\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `calendar` (`date_holiday`, `holiday_type_id`, `user`) VALUES\n")
        holidays = [
            "('2025-01-01', 1, 'admin')",
            "('2025-01-13', 1, 'admin')",
            "('2025-02-11', 1, 'admin')",
            "('2025-02-23', 1, 'admin')",
            "('2025-03-20', 1, 'admin')",
            "('2025-04-29', 1, 'admin')",
            "('2025-05-03', 1, 'admin')",
            "('2025-05-04', 1, 'admin')",
            "('2025-05-05', 1, 'admin')",
            "('2025-07-21', 1, 'admin')",
            "('2025-08-11', 1, 'admin')",
            "('2025-09-15', 1, 'admin')",
            "('2025-09-23', 1, 'admin')",
            "('2025-10-13', 1, 'admin')",
            "('2025-11-03', 1, 'admin')",
            "('2025-11-23', 1, 'admin')",
            "('2025-12-29', 2, 'admin')",
            "('2025-12-30', 2, 'admin')",
            "('2025-12-31', 2, 'admin')"
        ]
        f.write(',\n'.join(holidays) + ';\n\n')

        # Finished Products
        f.write("-- ================================================\n")
        f.write("-- Finished Products (完成品) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `finished_products` (`product_id`, `lot_id`, `finished_quantity`, `date_finished`, `user`) VALUES\n")
        finished = generate_finished_products(200, 200, 200)
        f.write(',\n'.join(finished) + ';\n\n')

        # Machine List
        f.write("-- ================================================\n")
        f.write("-- Machine List (機械リスト) - 200 records\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `machine_list` (`factory_id`, `machine_no`, `user`) VALUES\n")
        machines = generate_machine_list(200)
        f.write(',\n'.join(machines) + ';\n\n')

        # Working Hours
        f.write("-- ================================================\n")
        f.write("-- Working Hours (稼働時間)\n")
        f.write("-- ================================================\n")
        f.write("INSERT INTO `working_hours` (`factory_id`, `hours`, `user`) VALUES\n")
        working_hours = []
        for i in range(1, 11):
            hours = random.choice([8.00, 16.00, 24.00])
            working_hours.append(f"({i}, {hours}, 'admin')")
        f.write(',\n'.join(working_hours) + ';\n\n')

if __name__ == '__main__':
    print("サンプルデータを生成中...")
    write_sql_file()
    print("完了！seed.sqlファイルが生成されました。")
