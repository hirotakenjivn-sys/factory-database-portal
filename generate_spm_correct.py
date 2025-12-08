#!/usr/bin/env python3
"""
SPMデータ生成スクリプト（正しい版）
- process_name: process_name_typesのprocess_name（PRESS 1/4など）
- press_no: machine_listのmachine_no（PRESS-001など）
"""
import random

output_file = "database/insert_spm_correct.sql"

sql_lines = []
sql_lines.append("-- ================================================")
sql_lines.append("-- SPM Data (正しい版)")
sql_lines.append("-- process_name: 工程名（PRESS 1/4等）")
sql_lines.append("-- press_no: 機械番号（PRESS-001等）")
sql_lines.append("-- ================================================")
sql_lines.append("")

# 既存のspmデータを削除
sql_lines.append("DELETE FROM spm;")
sql_lines.append("")

sql_lines.append("INSERT INTO `spm` (`product_id`, `process_name`, `press_no`, `cycle_time`, `user`) VALUES")

values = []

# PRESS機械リスト（machine_list_sample.sqlから）
press_machines = [
    'PRESS-001', 'PRESS-002', 'PRESS-003', 'PRESS-004',
    'PRESS-005', 'PRESS-006', 'PRESS-007', 'PRESS-008',
    'PRESS-S001', 'PRESS-S002', 'PRESS-S003', 'PRESS-S004'
]

# 工程名のパターン（process_name_typesから）
press_process_patterns = [
    'PRESS',
    'PRESS 1/2', 'PRESS 2/2',
    'PRESS 1/3', 'PRESS 2/3', 'PRESS 3/3',
    'PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4',
    'PRESS 1/5', 'PRESS 2/5', 'PRESS 3/5', 'PRESS 4/5', 'PRESS 5/5',
]

# 製品とその工程パターン
# (product_id, [process_names])
product_processes = [
    (2, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (3, ['PRESS 1/3', 'PRESS 2/3', 'PRESS 3/3']),
    (5, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (6, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (7, ['PRESS 1/2', 'PRESS 2/2']),
    (8, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (10, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (11, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (13, ['PRESS 1/3', 'PRESS 2/3', 'PRESS 3/3']),
    (14, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (15, ['PRESS 1/3', 'PRESS 2/3', 'PRESS 3/3']),
    (16, ['PRESS 1/2', 'PRESS 2/2']),
    (17, ['PRESS 1/5', 'PRESS 2/5', 'PRESS 3/5', 'PRESS 4/5', 'PRESS 5/5']),
    (18, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
    (19, ['PRESS 1/3', 'PRESS 2/3', 'PRESS 3/3']),
    (20, ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']),
]

# さらに製品を追加（21-50）
for pid in range(21, 51):
    num_processes = random.choice([2, 3, 4, 5])
    if num_processes == 2:
        processes = ['PRESS 1/2', 'PRESS 2/2']
    elif num_processes == 3:
        processes = ['PRESS 1/3', 'PRESS 2/3', 'PRESS 3/3']
    elif num_processes == 4:
        processes = ['PRESS 1/4', 'PRESS 2/4', 'PRESS 3/4', 'PRESS 4/4']
    else:  # 5
        processes = ['PRESS 1/5', 'PRESS 2/5', 'PRESS 3/5', 'PRESS 4/5', 'PRESS 5/5']

    product_processes.append((pid, processes))

# 各製品の各工程に対してspmデータを生成
for product_id, process_names in product_processes:
    for process_name in process_names:
        # 各工程に1〜3個の機械を割り当て
        num_machines = random.randint(1, 3)

        # ランダムに機械を選択（重複なし）
        selected_machines = random.sample(press_machines, min(num_machines, len(press_machines)))

        for machine_no in selected_machines:
            # cycle_timeは50〜500秒の範囲でランダム生成
            cycle_time = round(random.uniform(50.0, 500.0), 2)

            values.append(f"({product_id}, '{process_name}', '{machine_no}', {cycle_time}, 'admin')")

# SQL文を組み立て
if values:
    sql_lines.append(",\n".join(values) + ";")
else:
    sql_lines.append("-- No data to insert")

# ファイルに書き込み
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print()
print("=" * 60)
print("✓ SPMデータを生成しました（正しい版）")
print("=" * 60)
print(f"  ファイル: {output_file}")
print(f"  総レコード数: {len(values)}件")
print(f"  対象製品数: {len(product_processes)}製品")
print(f"  使用機械数: {len(press_machines)}台")
print()
print("=" * 60)
print("実行手順:")
print("=" * 60)
print()
print("1. テーブル構造を変更:")
print("   Get-Content database\\alter_spm_table.sql | docker exec -i factory-db mysql -uroot -ppassword123 factory_db")
print()
print("2. SPMデータを挿入:")
print("   Get-Content database\\insert_spm_correct.sql | docker exec -i factory-db mysql -uroot -ppassword123 factory_db")
print()
print("3. 確認:")
print("   docker exec factory-db mysql -uapp_user -papp_password factory_db -e \"SELECT * FROM spm LIMIT 10;\"")
print()
