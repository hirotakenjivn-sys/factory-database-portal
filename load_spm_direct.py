#!/usr/bin/env python3
"""
SPMサンプルデータを直接データベースに読み込むスクリプト
"""
import mysql.connector
from pathlib import Path

# データベース接続情報
DB_CONFIG = {
    'host': 'localhost',
    'user': 'app_user',
    'password': 'app_password',
    'database': 'factory_db'
}

def load_spm_data():
    """SPMサンプルデータを読み込む"""
    sql_file = Path(__file__).parent / 'database' / 'insert_spm_correct.sql'

    if not sql_file.exists():
        print(f"エラー: {sql_file} が見つかりません")
        return False

    # SQLファイルを読み込む
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 接続
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✓ データベースに接続しました")

        cursor = connection.cursor()

        # SQL文を実行
        # まず既存データを削除
        cursor.execute("DELETE FROM spm;")
        deleted_count = cursor.rowcount
        print(f"✓ 既存データを削除しました: {deleted_count}件")

        # INSERT文を抽出
        lines = sql_content.split('\n')
        insert_sql = []
        in_insert = False

        for line in lines:
            line = line.strip()
            if line.startswith('INSERT INTO'):
                in_insert = True
                insert_sql.append(line)
            elif in_insert:
                insert_sql.append(line)
                if line.endswith(';'):
                    # INSERT文を実行
                    full_sql = ' '.join(insert_sql)
                    cursor.execute(full_sql)
                    print(f"✓ データを挿入しました: {cursor.rowcount}件")
                    insert_sql = []
                    in_insert = False

        connection.commit()
        print("✓ トランザクションをコミットしました")

        # 確認
        cursor.execute("SELECT COUNT(*) FROM spm;")
        count = cursor.fetchone()[0]
        print(f"✓ SPMテーブルのレコード数: {count}件")

        cursor.close()
        connection.close()
        print("✓ データベース接続を閉じました")
        return True

    except mysql.connector.Error as e:
        print(f"エラー: {e}")
        return False
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("SPMサンプルデータ読み込みスクリプト")
    print("=" * 60)
    print()

    success = load_spm_data()

    print()
    print("=" * 60)
    if success:
        print("✓ SPMサンプルデータの読み込みが完了しました")
    else:
        print("✗ SPMサンプルデータの読み込みに失敗しました")
    print("=" * 60)
