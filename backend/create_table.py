#!/usr/bin/env python3
"""
production_scheduleテーブルを作成するスクリプト
バックエンドコンテナ内で実行してください
"""
import sys
import os

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
from app.models.production_schedule import ProductionSchedule

def create_production_schedule_table():
    """production_scheduleテーブルを作成"""
    try:
        print("production_scheduleテーブルを作成中...")

        # テーブルを作成
        ProductionSchedule.__table__.create(engine, checkfirst=True)

        print("✓ production_scheduleテーブルを作成しました")

        # テーブルが存在するか確認
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if 'production_schedule' in inspector.get_table_names():
            print("✓ テーブルの存在を確認しました")

            # カラム情報を表示
            columns = inspector.get_columns('production_schedule')
            print(f"\nカラム数: {len(columns)}")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ テーブルが見つかりません")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_production_schedule_table()
