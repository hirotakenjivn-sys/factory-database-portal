"""
新しいエンドポイント: /schedule/unconstrained-schedule

プレス機の制約を考慮せず、すべての工程を現在時刻から順次実行するスケジュールを計算
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from ..database import get_db
from ..models.po import PO
from ..models.product import Product
from ..models.customer import Customer
from ..models.process import Process, ProcessNameType
from ..auth import get_current_user
from ..config import VIETNAM_TZ

@router.get("/unconstrained-schedule")
async def get_unconstrained_schedule(
    working_hours: int = 8,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    プレス機制約なしのスケジュール計算
    
    すべての工程を現在時刻から順次実行し、機械の空き状況を考慮しない理論的なスケジュールを返す
    """
    from ..services.production_scheduler import ProductionScheduler
    
    # スケジューラー初期化
    scheduler = ProductionScheduler(db, working_hours=working_hours)
   
    # 今週のPOを取得（生産対象）
    today = datetime.now(VIETNAM_TZ).date()
    end_of_week = today + timedelta(days=7)
    
    target_pos = db.query(PO).filter(
        and_(
            PO.delivery_date >= today,
            PO.delivery_date <= end_of_week
        )
    ).all()
    
    # 製品ごとのデータを作成
    product_processes = {}
    current_time = scheduler.get_vietnam_now()
    
    for po in target_pos:
        product = db.query(Product).filter(Product.product_id == po.product_id).first()
        if not product:
            continue
            
        customer = db.query(Customer).filter(Customer.customer_id == product.customer_id).first()
        
        # 製品の全工程を取得
        processes = db.query(Process).filter(
            Process.product_id == product.product_id
        ).order_by(Process.process_no).all()
        
        product_key = product.product_code
        
        if product_key not in product_processes:
            product_processes[product_key] = {
                'customer_name': customer.customer_name if customer else '-',
                'product_code': product.product_code,
                'po_quantity': po.po_quantity,
                'delivery_date': po.delivery_date.strftime("%d/%m/%Y") if po.delivery_date else "-",
                'po_numbers': {po.po_number},
                'processes': {},
                'production_deadline': ''
            }
        else:
            product_processes[product_key]['po_numbers'].add(po.po_number)
        
        # 各工程を順次計算（現在時刻から）
        work_start = current_time
        
        for process in processes:
            # 工程時間を計算
            setup_time, processing_time = scheduler.calculate_process_time(process, po.po_quantity)
            total_minutes = setup_time + processing_time
            
            if total_minutes == 0:
                continue
            
            # 終了時刻を計算（稼働時間を考慮）
            work_end = scheduler.add_working_time(work_start, total_minutes)
            
            # 開始日をフォーマット
            start_date = work_start.date()
            day = str(start_date.day).zfill(2)
            month = str(start_date.month).zfill(2)
            formatted_date = f"{day}/{month}"
            
            # 工程タイプを取得
            process_type_record = db.query(ProcessNameType).filter(
                ProcessNameType.process_name == process.process_name
            ).first()
            
            # タイプに応じて表示値を計算
            if process_type_record and process_type_record.day_or_spm is False:
                # DAY: 日数で表示
                daily_minutes = scheduler.get_working_minutes(working_hours)
                display_value = round(total_minutes / daily_minutes, 1)
                display_unit = 'D'
            else:
                # SPM: 時間で表示
                display_value = round(total_minutes / 60)
                display_unit = 'H'
            
            # 工程データを追加
            process_key = process.process_name
            if process_key in product_processes[product_key]['processes']:
                existing = product_processes[product_key]['processes'][process_key]
                existing['display_value'] = float(existing['display_value']) + float(display_value)
            else:
                product_processes[product_key]['processes'][process_key] = {
                    'name': process.process_name,
                    'process_no': process.process_no,
                    'date': formatted_date,
                    'date_str': start_date.isoformat(),
                    'display_value': float(display_value),
                    'display_unit': display_unit,
                    'latest_end_date': work_end.isoformat()
                }
            
            # 次の工程の開始時刻を更新
            work_start = work_end
    
    # 総加工時間と生産締切日を計算（元のエンドポイントと同じロジック）
    for product_data in product_processes.values():
        # POリストを文字列に変換
        po_list = sorted(list(product_data['po_numbers']))
        if len(po_list) > 1:
            product_data['po_numbers_display'] = '<br>'.join(po_list)
        else:
            product_data['po_numbers_display'] = po_list[0] if po_list else '-'
        
        # 総加工時間を計算
        processes = product_data['processes']
        sorted_processes = sorted(processes.values(), key=lambda p: p['process_no'])
        
        total_hours = 0
        total_days = 0
        
        for process in sorted_processes:
            if process['display_unit'] == 'H':
                total_hours += process['display_value']
            else:
                total_days += process['display_value']
        
        # フォーマット
        formatted_time = []
        if total_days > 0:
            formatted_time.append(f"{int(total_days)}day")
        if total_hours > 0:
            formatted_time.append(f"{int(total_hours)}hour")
        
        product_data['total_processing_time'] = ' '.join(formatted_time) if formatted_time else '0hour'
        
        # 生産締切日を計算
        total_processing_days = total_days + (total_hours / 8)  # 8時間=1日と仮定
        from datetime import datetime
        delivery_date = datetime.strptime(product_data['delivery_date'], "%d/%m/%Y").date()
        production_deadline = scheduler.calculate_production_deadline(delivery_date, total_processing_days)
        product_data['production_deadline'] = production_deadline.strftime("%d/%m/%Y")
    
    # リスト形式に変換
    products_list = list(product_processes.values())
    
    return {
        'products': products_list,
        'products_count': len(products_list)
    }
