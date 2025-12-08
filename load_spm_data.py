#!/usr/bin/env python3
"""
SPMサンプルデータをデータベースに読み込むスクリプト
"""
import pymysql
import os
from pathlib import Path

# データベース接続情報
DB_CONFIG = {
    'host': 'localhost',
    'user': 'app_user',
    'password': 'app_password',
    'database': 'factory_db',
    'charset': 'utf8mb4'
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
        connection = pymysql.connect(**DB_CONFIG)
        print("✓ データベースに接続しました")

        with connection.cursor() as cursor:
            # コメント行を除外してSQL文を分割
            statements = []
            current_statement = []

            for line in sql_content.split('\n'):
                line = line.strip()
                # コメント行をスキップ
                if line.startswith('--') or not line:
                    continue

                current_statement.append(line)

                # セミコロンで終わる行は文の終わり
                if line.endswith(';'):
                    statements.append(' '.join(current_statement))
                    current_statement = []

            # 各SQL文を実行
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
                    if 'DELETE' in statement.upper():
                        print(f"✓ 既存データを削除しました: {cursor.rowcount}件")
                    elif 'INSERT' in statement.upper():
                        print(f"✓ データを挿入しました: {cursor.rowcount}件")

            connection.commit()
            print("✓ トランザクションをコミットしました")

        connection.close()
        print("✓ データベース接続を閉じました")
        return True

    except pymysql.Error as e:
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
