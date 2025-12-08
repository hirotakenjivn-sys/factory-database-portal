#!/usr/bin/env python3
import pymysql

# データベース接続
conn = pymysql.connect(
    host='localhost',
    user='app_user',
    password='app_password',
    database='factory_db',
    port=3306
)

try:
    with conn.cursor() as cursor:
        # 機械リストの総数を確認
        cursor.execute("SELECT COUNT(*) as total FROM machine_list")
        total = cursor.fetchone()[0]
        print(f"=== 機械リスト総数: {total}機 ===\n")

        # factory別、machine_type別の集計
        cursor.execute("""
            SELECT
                f.factory_name,
                ml.machine_type,
                COUNT(*) as count
            FROM machine_list ml
            LEFT JOIN factories f ON ml.factory_id = f.factory_id
            GROUP BY f.factory_name, ml.machine_type
            ORDER BY f.factory_name, ml.machine_type
        """)

        print("=== 工場・機械種別 集計 ===")
        for row in cursor.fetchall():
            factory_name, machine_type, count = row
            print(f"{factory_name:20s} {machine_type if machine_type else 'NULL':10s} {count:3d}機")

        print("\n=== 全機械リスト ===")
        cursor.execute("""
            SELECT
                ml.machine_list_id,
                f.factory_name,
                ml.machine_no,
                ml.machine_type
            FROM machine_list ml
            LEFT JOIN factories f ON ml.factory_id = f.factory_id
            ORDER BY ml.factory_id, ml.machine_type, ml.machine_no
        """)

        print(f"{'ID':5s} {'工場':20s} {'機械番号':15s} {'種別':10s}")
        print("-" * 55)
        for row in cursor.fetchall():
            machine_id, factory_name, machine_no, machine_type = row
            print(f"{machine_id:<5d} {factory_name:20s} {machine_no:15s} {machine_type if machine_type else 'NULL':10s}")

finally:
    conn.close()
