#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Machine Listのみを生成するスクリプト
新スキーマ: machine_type_id (外部キー)
"""

import sys
import io

# UTF-8エンコーディングを設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_machine_list(count=20):
    """機械リストデータ生成（新スキーマ対応）"""
    machines = []
    for i in range(count):
        factory_id = (i % 2) + 1  # 2工場を想定
        machine_no = f"M-{i+1:04d}"
        machines.append(f"""INSERT INTO `machine_list` (`factory_id`, `machine_no`, `machine_type_id`, `user`)
SELECT {factory_id}, '{machine_no}', machine_type_id, 'admin' FROM machine_types WHERE machine_type_name = 'PRESS';""")
    return machines

def write_sql_file():
    """SQLファイルを生成（Machine Listのみ）"""
    output_file = 'machine_list_only.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("""-- Machine List Only
-- Factory Database Portal
-- 新スキーマ: machine_type_id (外部キー)

SET NAMES utf8mb4;

-- ================================================
-- Machine List (機械リスト) - 20 records
-- ================================================
""")
        machines = generate_machine_list(20)
        f.write('\n'.join(machines) + '\n')
    
    print(f"✅ 完了！{output_file}ファイルが生成されました。")

if __name__ == '__main__':
    print("Machine Listデータを生成中...")
    write_sql_file()
