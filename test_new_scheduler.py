"""
新しいスケジューリング方式とデータ取得ロジックの検証スクリプト
"""
import sys
import io
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker

# UTF-8で出力するように設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.config import settings
from app.models.production_schedule import ProductionSchedule
from app.models.po import PO
from app.models.product import Product
from app.models.customer import Customer
from app.models.process import Process
from app.models.factory import MachineList
from app.services.production_scheduler import ProductionScheduler

db_url = settings.DATABASE_URL.replace('@db', '@localhost')
print(f"Connecting to database: {db_url}")

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_new_scheduling():
    """新しいスケジューリング方式とデータ取得のテスト"""
    db = SessionLocal()
    
    try:
        # 1. スケジューリング実行
        print("=" * 80)
        print("1. スケジューリング実行")
        print("=" * 80)
        
        scheduler = ProductionScheduler(db, working_hours=8)
        result = scheduler.generate_schedule_by_deadline()
        
        press_schedules = result['constrained_schedules']
        print(f"スケジュール生成完了: {len(press_schedules)} 件のプレス工程")
        
        # コミット（データ取得テストのため）
        db.commit()
        
        # 2. データ取得ロジック（API相当）の検証
        print("\n" + "=" * 80)
        print("2. データ取得ロジック（get_press_weekly_schedule_from_plan）の検証")
        print("=" * 80)
        
        # 日付範囲設定
        earliest_schedule = db.query(func.min(ProductionSchedule.planned_start_datetime)).scalar()
        if earliest_schedule:
            today = earliest_schedule.date()
        else:
            today = datetime.now().date()
            
        print(f"開始日: {today}")
        end_date = today + timedelta(days=7)
        
        # プレス機取得
        press_machines = db.query(MachineList).filter(
            MachineList.machine_type == 'PRESS'
        ).order_by(MachineList.machine_no).all()
        print(f"プレス機: {len(press_machines)} 台")
        
        # スケジュール取得
        schedules_query = db.query(ProductionSchedule)\
            .join(Process, ProductionSchedule.process_id == Process.process_id)\
            .filter(
                and_(
                    ProductionSchedule.machine_list_id.isnot(None),
                    ProductionSchedule.planned_start_datetime >= today,
                    ProductionSchedule.planned_start_datetime < end_date
                )
            )\
            .order_by(ProductionSchedule.planned_start_datetime.asc())\
            .all()
            
        print(f"期間内のプレススケジュール: {len(schedules_query)} 件")
        
        # グループ化ロジックの検証
        schedule_dict = {}
        for machine in press_machines:
            schedule_dict[machine.machine_no] = 0
            
        processed_count = 0
        error_count = 0
        
        production_deadline_cache = {}
        
        for schedule in schedules_query:
            try:
                # 機械チェック
                machine = db.query(MachineList).filter(
                    MachineList.machine_list_id == schedule.machine_list_id
                ).first()
                if not machine:
                    print(f"Warning: Machine not found for schedule {schedule.schedule_id}")
                    continue
                    
                # データ整合性チェック
                po = db.query(PO).filter(PO.po_id == schedule.po_id).first()
                if not po:
                    print(f"Warning: PO not found for schedule {schedule.schedule_id}")
                    continue
                    
                product = db.query(Product).filter(Product.product_id == po.product_id).first()
                if not product:
                    print(f"Warning: Product not found for PO {po.po_id}")
                    continue
                    
                process = db.query(Process).filter(Process.process_id == schedule.process_id).first()
                if not process:
                    print(f"Warning: Process not found for schedule {schedule.schedule_id}")
                    continue
                
                # PO数量合計計算（ここが修正ポイント）
                po_total_data = scheduler.calculate_po_total_with_28days(product.product_id)
                total_po_quantity = po_total_data.get('po_total', 0)
                if total_po_quantity == 0:
                    total_po_quantity = po.po_quantity
                    
                # 締切日計算
                if po.po_id not in production_deadline_cache:
                    total_days = scheduler.calculate_total_processing_days(product, total_po_quantity)
                    production_deadline = scheduler.calculate_production_deadline(
                        po.delivery_date,
                        total_days
                    )
                    production_deadline_cache[po.po_id] = production_deadline
                
                schedule_dict[machine.machine_no] += 1
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing schedule {schedule.schedule_id}: {str(e)}")
                error_count += 1
                import traceback
                traceback.print_exc()
        
        print(f"\n処理完了: {processed_count} 件")
        print(f"エラー: {error_count} 件")
        print("\n機械別スケジュール数:")
        for machine_no, count in schedule_dict.items():
            print(f"  {machine_no}: {count} 件")
            
        if processed_count > 0:
            print("\n検証成功: データは正しく生成・取得されています。")
        else:
            print("\n検証失敗: データが生成または取得できていません。")
        
    except Exception as e:
        print(f"\n致命的なエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_new_scheduling()
