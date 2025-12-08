#!/usr/bin/env python3
"""
production_scheduleテーブルを作成するスクリプト
バックエンドディレクトリで実行: python3 create_production_schedule_table.py
"""
import sys
import os

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.database import engine
    from app.models.production_schedule import ProductionSchedule
    from sqlalchemy import inspect

    print("production_scheduleテーブルを作成しています...")

    # テーブルが既に存在するか確認
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if 'production_schedule' in existing_tables:
        print("✓ production_scheduleテーブルは既に存在します")

        # カラム情報を表示
        columns = inspector.get_columns('production_schedule')
        print(f"\nカラム数: {len(columns)}")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        # テーブルを作成
        ProductionSchedule.__table__.create(engine, checkfirst=True)

        # 作成されたか確認
        inspector = inspect(engine)
        if 'production_schedule' in inspector.get_table_names():
            print("✓ production_scheduleテーブルを作成しました")

            # カラム情報を表示
            columns = inspector.get_columns('production_schedule')
            print(f"\nカラム数: {len(columns)}")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ テーブルの作成に失敗しました")
            sys.exit(1)

    print("\n完了しました")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
