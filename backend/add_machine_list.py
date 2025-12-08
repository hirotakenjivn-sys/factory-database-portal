#!/usr/bin/env python3
"""
機械リストマスタにサンプルデータを追加するスクリプト
プレス機のサンプルデータを登録
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.factory import MachineList
from datetime import datetime

# データベース接続設定（Docker内からの接続）
DATABASE_URL = "mysql+pymysql://app_user:app_password@db:3306/factory_db"

def add_machine_list_data():
    """機械リストマスタにサンプルデータを追加"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 既存データを確認
        existing_count = db.query(MachineList).count()
        print(f"既存の機械リストデータ件数: {existing_count}")
        
        # サンプルデータ（プレス機）
        # MachineListモデル: machine_list_id, factory_id, machine_no, machine_type, timestamp, user
        machines = [
            {
                "factory_id": 1,  # デフォルトの工場ID
                "machine_no": "プレス機1号",
                "machine_type": "PRESS",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "プレス機2号",
                "machine_type": "PRESS",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "プレス機3号",
                "machine_type": "PRESS",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "プレス機4号",
                "machine_type": "PRESS",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "プレス機5号",
                "machine_type": "PRESS",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "TAP1号機",
                "machine_type": "TAP",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "TAP2号機",
                "machine_type": "TAP",
                "user": "admin",
                "timestamp": datetime.now()
            },
            {
                "factory_id": 1,
                "machine_no": "BARREL1号機",
                "machine_type": "BARREL",
                "user": "admin",
                "timestamp": datetime.now()
            },
        ]
        
        # データを追加
        added_count = 0
        for machine_data in machines:
            # 同じ名前の機械が既に存在するかチェック
            existing = db.query(MachineList).filter(
                MachineList.machine_no == machine_data["machine_no"]
            ).first()
            
            if existing:
                print(f"スキップ: {machine_data['machine_no']} (既に存在)")
                continue
            
            machine = MachineList(**machine_data)
            db.add(machine)
            added_count += 1
            print(f"追加: {machine_data['machine_no']} ({machine_data['machine_type']})")
        
        db.commit()
        print(f"\n{added_count}件の機械リストデータを追加しました")
        
        # 追加後の件数を表示
        total_count = db.query(MachineList).count()
        print(f"現在の機械リストデータ件数: {total_count}")
        
        # 登録されたデータを表示
        print("\n登録されている機械リスト:")
        all_machines = db.query(MachineList).all()
        for m in all_machines:
            print(f"  - ID:{m.machine_list_id} {m.machine_no} ({m.machine_type})")
        
    except Exception as e:
        db.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("機械リストマスタにサンプルデータを追加します...")
    add_machine_list_data()
    print("完了しました！")
