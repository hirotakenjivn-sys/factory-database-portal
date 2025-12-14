#!/usr/bin/env python3
"""
iot_button_eventsテーブルを作成するスクリプト
バックエンドコンテナ内で実行してください
"""
import sys
import os

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
from app.models.iot_button_event import IotButtonEvent

def create_iot_table():
    """iot_button_eventsテーブルを作成"""
    try:
        print("iot_button_eventsテーブルを作成中...")

        # テーブルを作成
        IotButtonEvent.__table__.create(engine, checkfirst=True)

        print("✓ iot_button_eventsテーブルを作成しました")

        # テーブルが存在するか確認
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if 'iot_button_events' in inspector.get_table_names():
            print("✓ テーブルの存在を確認しました")

            # カラム情報を表示
            columns = inspector.get_columns('iot_button_events')
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
    create_iot_table()
