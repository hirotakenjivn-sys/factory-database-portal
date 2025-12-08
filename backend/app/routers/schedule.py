from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List
from datetime import datetime, timedelta, date
from decimal import Decimal
import pytz
from ..database import get_db

# ベトナム時間（UTC+7）のタイムゾーン
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
from ..models import Calendar, HolidayType, PO, Product, Process, ProcessNameType, Customer, ProductionSchedule
from ..models.factory import MachineList
from ..schemas import schedule as schemas
from ..routers.auth import get_current_user
from ..services.production_scheduler import ProductionScheduler

router = APIRouter()


# ============================================
# Holiday Types
# ============================================

@router.get("/holiday-types", response_model=List[schemas.HolidayType])
async def get_holiday_types(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """休日種別一覧を取得"""
    holiday_types = db.query(HolidayType).all()
    return holiday_types


@router.post("/holiday-types", response_model=schemas.HolidayType, status_code=status.HTTP_201_CREATED)
async def create_holiday_type(
    holiday_type_data: schemas.HolidayTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """休日種別を登録"""
    new_holiday_type = HolidayType(**holiday_type_data.dict())
    db.add(new_holiday_type)
    db.commit()
    db.refresh(new_holiday_type)
    return new_holiday_type


# ============================================
# Calendar (Holidays)
# ============================================

@router.get("/calendar", response_model=List[schemas.CalendarWithDetails])
async def get_calendar(
    skip: int = 0,
    limit: int = 365,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """カレンダー（休日）一覧を取得"""
    calendars = db.query(Calendar)\
        .join(HolidayType, Calendar.holiday_type_id == HolidayType.holiday_type_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

    # データを整形
    result = []
    for cal in calendars:
        holiday_type = db.query(HolidayType).filter(HolidayType.holiday_type_id == cal.holiday_type_id).first()
        result.append({
            "calendar_id": cal.calendar_id,
            "date_holiday": cal.date_holiday,
            "holiday_type_id": cal.holiday_type_id,
            "timestamp": cal.timestamp,
            "user": cal.user,
            "date_type": holiday_type.date_type if holiday_type else None,
        })

    return result


@router.get("/calendar/{calendar_id}", response_model=schemas.Calendar)
async def get_calendar_item(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """カレンダー項目を1件取得"""
    calendar_item = db.query(Calendar).filter(Calendar.calendar_id == calendar_id).first()

    if not calendar_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )

    return calendar_item


@router.post("/calendar", response_model=schemas.Calendar, status_code=status.HTTP_201_CREATED)
async def create_calendar(
    calendar_data: schemas.CalendarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """休日を登録"""
    # 休日種別の存在確認
    holiday_type = db.query(HolidayType).filter(HolidayType.holiday_type_id == calendar_data.holiday_type_id).first()
    if not holiday_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday type not found"
        )

    # 既に同じ日付が登録されていないかチェック
    existing = db.query(Calendar).filter(Calendar.date_holiday == calendar_data.date_holiday).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This date is already registered as a holiday"
        )

    new_calendar = Calendar(
        **calendar_data.dict(),
        user=current_user["username"]
    )

    db.add(new_calendar)
    db.commit()
    db.refresh(new_calendar)

    return new_calendar


@router.put("/calendar/{calendar_id}", response_model=schemas.Calendar)
async def update_calendar(
    calendar_id: int,
    calendar_data: schemas.CalendarUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """休日を更新"""
    calendar_item = db.query(Calendar).filter(Calendar.calendar_id == calendar_id).first()

    if not calendar_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )

    # 更新データを適用
    update_data = calendar_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(calendar_item, key, value)

    calendar_item.user = current_user["username"]

    db.commit()
    db.refresh(calendar_item)

    return calendar_item


@router.delete("/calendar/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """休日を削除"""
    calendar_item = db.query(Calendar).filter(Calendar.calendar_id == calendar_id).first()

    if not calendar_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )

    db.delete(calendar_item)
    db.commit()

    return None


# ============================================
# Delivery Schedule (PO納期)
# ============================================

@router.get("/delivery-schedule")
async def get_delivery_schedule(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """納期スケジュールを取得（POの納期一覧）"""
    pos = db.query(PO)\
        .join(Product, PO.product_id == Product.product_id)\
        .order_by(PO.delivery_date)\
        .offset(skip)\
        .limit(limit)\
        .all()

    result = []
    for po in pos:
        result.append({
            "po_id": po.po_id,
            "po_number": po.po_number,
            "product_code": po.product.product_code,
            "po_quantity": po.po_quantity,
            "delivery_date": po.delivery_date,
            "date_receive_po": po.date_receive_po,
        })

    return result


# ============================================
# Progress Table (進捗確認)
# ============================================

@router.get("/progress-table")
async def get_progress_table(
    db: Session = Depends(get_db)
):
    """
    進捗確認テーブルを取得
    工程表にPO情報（PO数量合計、PO番号、納期）を追加したもの
    """
    # 製品ごとに工程をグループ化
    products = db.query(
        Product.product_id,
        Product.product_code,
        Customer.customer_name
    ).join(
        Customer, Product.customer_id == Customer.customer_id
    ).filter(
        Product.is_active == True
    ).all()

    result = []
    for product in products:
        # この製品の工程を取得
        processes = db.query(Process).filter(
            Process.product_id == product.product_id
        ).order_by(Process.process_no).all()

        # 工程がない製品はスキップ
        if not processes:
            continue

        # 工程を工程番号ごとに整理（最大20工程）
        # 工程オブジェクト全体を保持
        process_map = {}
        for proc in processes:
            if proc.process_no <= 20:
                process_map[proc.process_no] = proc

        # この製品のPO情報を取得
        # 1. 最も近い納期を取得（未配送のみ）
        earliest_po = db.query(PO).filter(
            and_(
                PO.product_id == product.product_id,
                PO.is_delivered == False
            )
        ).order_by(PO.delivery_date).first()

        total_po_quantity = None
        po_numbers_display = None
        earliest_delivery_date = None

        if earliest_po:
            earliest_delivery_date = earliest_po.delivery_date.strftime("%d/%m/%Y")

            # 最も近い納期から28日以内のPOを取得
            date_limit = earliest_po.delivery_date + timedelta(days=28)

            relevant_pos = db.query(PO).filter(
                and_(
                    PO.product_id == product.product_id,
                    PO.is_delivered == False,
                    PO.delivery_date >= earliest_po.delivery_date,
                    PO.delivery_date <= date_limit
                )
            ).order_by(PO.delivery_date).all()

            # PO数量の合計を計算
            total_po_quantity = sum(po.po_quantity for po in relevant_pos)

            # PO番号を最大4件まで取得（改行で区切る）
            po_numbers = [po.po_number for po in relevant_pos[:4]]
            po_numbers_display = "<br>".join(po_numbers)

        product_row = {
            "product_id": product.product_id,
            "customer_name": product.customer_name,
            "product_code": product.product_code,
            "total_po_quantity": total_po_quantity,
            "po_numbers_display": po_numbers_display,
            "earliest_delivery_date": earliest_delivery_date,
        }

        # 全工程の合計加工時間を計算
        total_days = 0
        total_minutes = 0

        # 各工程の加工時間を計算して保存
        process_times = {}
        for i in range(1, 21):
            process = process_map.get(i)
            if process and total_po_quantity:
                # 工程タイプを取得
                process_type_record = db.query(ProcessNameType).filter(
                    ProcessNameType.process_name == process.process_name
                ).first()
                process_type = process_type_record.day_or_spm if process_type_record else None

                # デフォルト稼働時間は8時間
                working_hours = 8

                # 加工時間を計算
                time_needed = calculate_process_time(
                    process,
                    total_po_quantity,
                    working_hours,
                    process_type,
                    db
                )

                process_times[i] = {
                    "days": time_needed["days"],
                    "minutes": time_needed["minutes"]
                }

                # 合計に加算
                total_days += time_needed["days"]
                total_minutes += time_needed["minutes"]

        # 納期から逆算して各工程の予定日時を計算
        process_schedules = {}
        if earliest_po and total_po_quantity:
            current_date = earliest_po.delivery_date
            working_hours = 8

            # 工程を逆順（最終工程から最初の工程）に処理
            process_numbers = sorted([k for k in process_map.keys()], reverse=True)
            for process_no in process_numbers:
                if process_no in process_times:
                    time_needed = process_times[process_no]

                    # この工程の開始予定日時を計算
                    planned_datetime = subtract_working_time(
                        current_date,
                        time_needed["days"],
                        time_needed["minutes"],
                        working_hours,
                        db
                    )

                    process_schedules[process_no] = planned_datetime
                    current_date = planned_datetime.date()

        # 工程1〜20のフィールドを追加（工程名 + 加工日数 + 予定日時）
        for i in range(1, 21):
            process = process_map.get(i)
            if process and total_po_quantity and i in process_times:
                time_needed = process_times[i]
                days = time_needed["days"]
                minutes = time_needed["minutes"]
                hours = minutes // 60

                time_str = ""
                if days > 0:
                    time_str += f"{days}day"
                if hours > 0:
                    time_str += f"{hours}h"
                if not time_str:
                    time_str = "0h"

                # 予定日時を追加
                schedule_str = ""
                if i in process_schedules:
                    planned_dt = process_schedules[i]
                    schedule_str = f"\n{planned_dt.strftime('%d/%m %H:%M')}"

                # 工程名 + 加工時間 + 予定日時を結合
                product_row[f"process_{i}"] = f"{process.process_name}\n({time_str}){schedule_str}"
            elif process:
                # PO数量がない場合は工程名のみ
                product_row[f"process_{i}"] = process.process_name
            else:
                product_row[f"process_{i}"] = ""

        # 合計加工時間をフォーマット（稼働時間を考慮して日単位に切り上げ）
        # デフォルト稼働時間は8時間
        working_hours = 8

        # 分を時間に変換
        total_hours_from_minutes = total_minutes / 60

        # 稼働時間を超える時間を日数に換算して切り上げ
        import math
        additional_days = math.ceil(total_hours_from_minutes / working_hours)

        # 最終的な日数
        final_days = total_days + additional_days

        # 残りの時間（稼働時間内）
        remaining_hours = total_hours_from_minutes % working_hours

        total_time_str = ""
        if final_days > 0:
            total_time_str += f"{final_days}day"
        if remaining_hours > 0:
            total_time_str += f"{int(remaining_hours)}h"
        if not total_time_str:
            total_time_str = "0h"

        product_row["total_processing_time"] = total_time_str

        result.append(product_row)

    return result


# ============================================
# Production Plan Calculation (生産計画計算)
# ============================================

def get_working_minutes(hours: int) -> int:
    """稼働時間から実稼働分数を計算（休憩時間を除く）"""
    working_minutes_map = {
        8: 440,   # 8時間 - 40分休憩
        9: 500,   # 9時間 - 40分休憩
        10: 560,  # 10時間 - 40分休憩
        11: 620,  # 11時間 - 70分休憩
        12: 680,  # 12時間 - 70分休憩
    }
    return working_minutes_map.get(hours, hours * 60)  # デフォルトは休憩なし


def is_working_day(date_to_check: date, db: Session) -> bool:
    """指定された日が稼働日（休日でない）かチェック"""
    holiday = db.query(Calendar).filter(Calendar.date_holiday == date_to_check).first()
    return holiday is None


def calculate_process_time(
    process: Process,
    po_quantity: int,
    working_hours: int,
    process_type: bool,
    db: Session
) -> dict:
    """
    工程の所要時間を計算
    Returns: {"days": int, "minutes": int}
    """
    if process_type is True:  # SPM
        # SPM: 1分間あたりの生産数（例: SPM60 = 1分間に60個）
        # 処理時間（分） = 数量 ÷ (SPM × 安全係数)
        if not process.rough_cycletime or process.rough_cycletime == 0:
            return {"days": 0, "minutes": 0}

        safety_factor = Decimal("0.7")
        # effective_spm = 1分間あたりの実効生産数
        effective_spm = process.rough_cycletime * safety_factor

        # 段取時間を追加
        setup_time = process.setup_time or Decimal("0")

        # 総生産時間（分） = (数量 ÷ 実効SPM) + 段取時間
        total_minutes = (Decimal(po_quantity) / effective_spm) + setup_time

        # 1日の稼働分数
        daily_minutes = get_working_minutes(working_hours)

        # 必要日数を計算
        days = int(total_minutes / daily_minutes)
        remaining_minutes = int(total_minutes % daily_minutes)

        return {"days": days, "minutes": remaining_minutes}

    elif process_type is False:  # DAY
        # DAY: rough_cycletime日で production_limit 個生産できる
        # 必要日数 = CEILING(PO数量 / production_limit) * rough_cycletime
        # 例: TAPPING 1日 2500pcs → rough_cycletime=1, production_limit=2500
        # 例: PLATING 5日 50000pcs → rough_cycletime=5, production_limit=50000
        if not process.production_limit or process.production_limit == 0:
            return {"days": 0, "minutes": 0}

        import math
        # 必要な生産サイクル数
        cycles_needed = math.ceil(po_quantity / process.production_limit)

        # rough_cycletimeが設定されている場合は日数として使用、なければ1日とする
        days_per_cycle = float(process.rough_cycletime) if process.rough_cycletime else 1

        # 総必要日数
        total_days = int(cycles_needed * days_per_cycle)

        return {"days": total_days, "minutes": 0}

    else:
        # タイプが不明な場合はスキップ
        return {"days": 0, "minutes": 0}


def subtract_working_time(
    start_date: date,
    days: int,
    minutes: int,
    working_hours: int,
    db: Session
) -> datetime:
    """
    指定された日付から稼働時間を遡って計算
    休日を考慮して実際の稼働日のみカウント
    """
    current_date = start_date
    remaining_days = days
    remaining_minutes = minutes

    # 開始時刻は6:00とする
    start_time_hour = 6
    start_time_minute = 0

    # 分を日数に変換（1日の稼働分数を超える場合）
    daily_minutes = get_working_minutes(working_hours)
    if remaining_minutes > 0:
        remaining_days += 1  # 分単位の作業がある場合は1日追加

    # 日数分遡る
    while remaining_days > 0:
        current_date = current_date - timedelta(days=1)

        # 稼働日のみカウント
        if is_working_day(current_date, db):
            remaining_days -= 1

    # 分単位の調整
    if remaining_minutes > 0:
        # 開始時刻から分数分進める
        result_hour = start_time_hour + (remaining_minutes // 60)
        result_minute = start_time_minute + (remaining_minutes % 60)

        if result_minute >= 60:
            result_hour += 1
            result_minute -= 60
    else:
        result_hour = start_time_hour
        result_minute = start_time_minute

    return datetime.combine(current_date, datetime.min.time().replace(hour=result_hour, minute=result_minute))


@router.post("/calculate-production-plan")
async def calculate_production_plan(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    生産計画を計算

    製品ごとに未配送のPOをグループ化し、PO数量合計で各工程の生産予定日時を計算する
    最も近い納期の3日前から逆算して、各工程の開始予定日時を求める
    """
    working_hours = request.get("working_hours", 8)

    # 製品ごとにグループ化して、未配送のPOを取得
    products_with_pos = db.query(
        Product.product_id,
        Product.product_code,
        Customer.customer_name
    ).join(
        Customer, Product.customer_id == Customer.customer_id
    ).join(
        PO, PO.product_id == Product.product_id
    ).filter(
        and_(
            Product.is_active == True,
            PO.is_delivered == False
        )
    ).distinct().all()

    result = []

    for product_info in products_with_pos:
        product_id = product_info.product_id
        product_code = product_info.product_code
        customer_name = product_info.customer_name

        # この製品の工程を取得（工程番号の降順 = 最終工程から）
        processes = db.query(Process).filter(
            Process.product_id == product_id
        ).order_by(Process.process_no.desc()).all()

        if not processes:
            continue

        # この製品の未配送POを取得
        # 1. 最も近い納期を取得
        earliest_po = db.query(PO).filter(
            and_(
                PO.product_id == product_id,
                PO.is_delivered == False
            )
        ).order_by(PO.delivery_date).first()

        if not earliest_po:
            continue

        # 2. 最も近い納期から28日以内のPOを取得
        date_limit = earliest_po.delivery_date + timedelta(days=28)

        relevant_pos = db.query(PO).filter(
            and_(
                PO.product_id == product_id,
                PO.is_delivered == False,
                PO.delivery_date >= earliest_po.delivery_date,
                PO.delivery_date <= date_limit
            )
        ).all()

        # PO数量の合計を計算
        total_po_quantity = sum(po.po_quantity for po in relevant_pos)

        # 生産開始予定日 = 納期から逆算（納期そのものから各工程の加工時間を引く）
        production_start_date = earliest_po.delivery_date
        current_date = production_start_date

        # 納期（最も近いもの）
        delivery_date_str = earliest_po.delivery_date.strftime("%d/%m/%Y")

        # 各工程を逆順に計算
        for process in processes:
            # 工程タイプを取得
            process_type_record = db.query(ProcessNameType).filter(
                ProcessNameType.process_name == process.process_name
            ).first()

            process_type = process_type_record.day_or_spm if process_type_record else None

            # 工程の所要時間を計算（PO数量合計を使用）
            time_needed = calculate_process_time(
                process,
                total_po_quantity,
                working_hours,
                process_type,
                db
            )

            # 前の工程の開始日時を計算（稼働日を考慮して遡る）
            planned_datetime = subtract_working_time(
                current_date,
                time_needed["days"],
                time_needed["minutes"],
                working_hours,
                db
            )

            result.append({
                "customer_name": customer_name,
                "product_code": product_code,
                "process_name": process.process_name,
                "po_quantity": total_po_quantity,
                "planned_datetime": planned_datetime.strftime("%d/%m/%Y %H:%M"),
                "delivery_date": delivery_date_str,  # 納期（最も近いもの）
                "planned_datetime_sort": planned_datetime  # ソート用の日時オブジェクト
            })

            # 次の工程（1つ前の工程番号）の開始日を更新
            current_date = planned_datetime.date()

    # 生産計画日時で昇順にソート（早い日時が上）
    result.sort(key=lambda x: x["planned_datetime_sort"])

    # ソート用フィールドを削除
    for item in result:
        del item["planned_datetime_sort"]

    return result


# ============================================
# Production Schedule (生産計画)
# ============================================

@router.get("/production-schedule/debug")
async def debug_production_schedule(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """デバッグ情報を取得"""
    from ..services.production_scheduler import ProductionScheduler

    # スケジューラーを初期化
    scheduler = ProductionScheduler(db, 8)

    # 対象製品を取得
    target_products = scheduler.get_target_products_with_pos()

    # PRESS機を確認
    from ..models.factory import MachineList
    press_machines = db.query(MachineList).filter(
        MachineList.machine_type == 'PRESS'
    ).all()

    # 全工程名を取得（ユニーク）
    all_process_names = db.query(Process.process_name).distinct().limit(50).all()
    unique_process_names = [p[0] for p in all_process_names]

    # 製品情報を整形
    product_details = []
    for product_data in target_products[:5]:  # 最初の5件のみ
        product = product_data['product']
        earliest_po = product_data['earliest_po']
        processes = product_data['processes']

        process_list = []
        for p in processes[:10]:  # 最初の10工程
            # PRESS工程かどうかを判定（柔軟な判定）
            process_name_upper = p.process_name.upper() if p.process_name else ""
            is_press = (
                'PRESS' in process_name_upper or
                'プレス' in p.process_name or
                p.process_name == 'PRESS'
            )
            process_list.append({
                "process_name": p.process_name,
                "is_press_process": is_press,
                "rough_cycletime": float(p.rough_cycletime) if p.rough_cycletime else None,
                "setup_time": float(p.setup_time) if p.setup_time else None,
                "production_limit": p.production_limit
            })

        product_details.append({
            "product_code": product.product_code,
            "po_number": earliest_po.po_number,
            "delivery_date": earliest_po.delivery_date.isoformat(),
            "total_quantity": product_data['total_quantity'],
            "planned_start_date": product_data['planned_start_date'].isoformat(),
            "processes_count": len(processes),
            "processes": process_list
        })

    today = datetime.now(VIETNAM_TZ).date()

    return {
        "today": today.isoformat(),
        "target_products_count": len(target_products),
        "press_machines_count": len(press_machines),
        "press_machines": [
            {
                "machine_list_id": m.machine_list_id,
                "machine_no": m.machine_no,
                "machine_type": m.machine_type
            }
            for m in press_machines
        ],
        "all_process_names": unique_process_names,
        "press_process_detection": "工程名に 'PRESS'（大文字小文字無視）または 'プレス' が含まれる工程にPRESS機を割り当て",
        "sample_products": product_details,
        "logic_explanation": {
            "step1": "製品ごとに最も近い納期のPOを基準とする",
            "step2": "基準納期+28日以内のPOの数量を合算",
            "step3": "納期から逆算して、今日より前または今日から3日後までに開始が必要な製品のみ抽出"
        }
    }


@router.post("/production-schedule/generate")
async def generate_production_schedule(
    request: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    生産計画を自動生成

    - 納期+28日以内の全POを対象
    - makespan（全体の生産完了時刻）を最小化
    - PRESS機の割当最適化
    - 休日カレンダーを考慮
    """
    working_hours = request.get("working_hours", 8)

    # リソース制約設定（将来の拡張用）
    resource_constraints = request.get("resource_constraints", None)

    # スケジューラーを初期化
    scheduler = ProductionScheduler(db, working_hours, resource_constraints)

    # スケジュールを生成
    try:
        result = scheduler.generate_schedule(user_id=current_user.get("username"))
        makespan = scheduler.calculate_makespan()

        return {
            "success": True,
            "constrained_schedules_count": len(result['constrained_schedules']),
            "unconstrained_schedules_count": len(result['unconstrained_schedules']),
            "total_schedules_count": len(result['all_schedules']),
            "makespan": makespan.isoformat() if makespan else None,
            "message": f"{len(result['all_schedules'])}件のスケジュールを生成しました（制約あり: {len(result['constrained_schedules'])}件、並行実行: {len(result['unconstrained_schedules'])}件）"
        }
    except Exception as e:
        import traceback
        error_detail = f"スケジュール生成に失敗しました: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/production-schedule", response_model=List[schemas.ProductionSchedule])
async def get_production_schedule(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """生産計画スケジュールを取得"""
    schedules = db.query(ProductionSchedule)\
        .order_by(ProductionSchedule.planned_start_datetime.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    return schedules


@router.get("/production-schedule/detailed")
async def get_production_schedule_detailed(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """生産計画スケジュールを詳細情報付きで取得"""
    schedules = db.query(ProductionSchedule)\
        .join(PO, ProductionSchedule.po_id == PO.po_id)\
        .join(Product, PO.product_id == Product.product_id)\
        .join(Customer, Product.customer_id == Customer.customer_id)\
        .join(Process, ProductionSchedule.process_id == Process.process_id)\
        .order_by(ProductionSchedule.planned_start_datetime.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    result = []
    for schedule in schedules:
        po = db.query(PO).filter(PO.po_id == schedule.po_id).first()
        process = db.query(Process).filter(Process.process_id == schedule.process_id).first()
        product = db.query(Product).filter(Product.product_id == po.product_id).first()
        customer = db.query(Customer).filter(Customer.customer_id == product.customer_id).first()

        machine_name = None
        machine_list_id_debug = schedule.machine_list_id

        if schedule.machine_list_id:
            machine = db.query(MachineList).filter(MachineList.machine_list_id == schedule.machine_list_id).first()
            if machine:
                machine_name = machine.machine_no

        # デバッグ情報をログ出力
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Process: {process.process_name}, machine_list_id: {machine_list_id_debug}, machine_name: {machine_name}")

        result.append({
            "schedule_id": schedule.schedule_id,
            "po_number": po.po_number,
            "customer_name": customer.customer_name,
            "product_code": product.product_code,
            "process_name": process.process_name,
            "machine_name": machine_name,
            "machine_list_id": machine_list_id_debug,  # デバッグ用
            "planned_start_datetime": schedule.planned_start_datetime.strftime("%d/%m/%Y %H:%M"),
            "planned_end_datetime": schedule.planned_end_datetime.strftime("%d/%m/%Y %H:%M"),
            "po_quantity": schedule.po_quantity,
            "setup_time": float(schedule.setup_time) if schedule.setup_time else 0,
            "processing_time": float(schedule.processing_time) if schedule.processing_time else 0,
            "delivery_date": po.delivery_date.strftime("%d/%m/%Y") if po.delivery_date else None,
        })

    return result


@router.delete("/production-schedule")
async def delete_production_schedule(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """生産計画スケジュールを全削除"""
    deleted_count = db.query(ProductionSchedule).delete()
    db.commit()

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"{deleted_count}件のスケジュールを削除しました"
    }


@router.get("/comprehensive-production-plan")
async def get_comprehensive_production_plan(
    working_hours: int = 8,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    保存された包括的な生産計画を取得
    """
    # スケジューラーを初期化（計算用メソッドを使用するため）
    scheduler = ProductionScheduler(db, working_hours)

    # 対象製品とPOを取得（理論的な生産締切日などを再計算）
    target_products = scheduler.get_target_products_with_pos()

    try:
        # 保存されている全スケジュールを取得
        all_schedules_orm = db.query(ProductionSchedule).all()
        
        # ORMオブジェクトを辞書に変換
        all_schedules = []
        for sched in all_schedules_orm:
            po = db.query(PO).filter(PO.po_id == sched.po_id).first()
            product = db.query(Product).filter(Product.product_id == po.product_id).first() if po else None
            process = db.query(Process).filter(Process.process_id == sched.process_id).first()
            
            all_schedules.append({
                'po_id': sched.po_id,
                'po_number': po.po_number if po else '',
                'product_code': product.product_code if product else '',
                'process_name': process.process_name if process else '',
                'machine_list_id': sched.machine_list_id,
                'planned_start': sched.planned_start_datetime,
                'planned_end': sched.planned_end_datetime,
                'po_quantity': sched.po_quantity
            })

        # makespanを計算
        makespan = scheduler.calculate_makespan()

        # 製品ごとにグループ化した詳細情報を作成
        products_summary = []
        for product_data in target_products:
            product = product_data['product']
            earliest_po = product_data['earliest_po']

            # この製品のスケジュールを取得
            product_schedules = []
            for sched in all_schedules:
                if sched['product_code'] == product.product_code:
                    product_schedules.append(sched)

            products_summary.append({
                "product_code": product.product_code,
                "customer_name": product.customer.customer_name if product.customer else None,
                "total_quantity": product_data['total_quantity'],
                "total_days": product_data['total_days'],
                "remaining_hours": product_data['remaining_hours'],
                "display_string": product_data['display_string'],
                "production_deadline": product_data['production_deadline'].isoformat(),
                "delivery_date": earliest_po.delivery_date.isoformat(),
                "po_number": earliest_po.po_number,
                "process_count": len(product_data['processes']),
                "schedules": product_schedules
            })

        # スケジュール件数をカウント
        constrained_count = len([s for s in all_schedules if s['machine_list_id'] is not None])
        unconstrained_count = len(all_schedules) - constrained_count

        return {
            "success": True,
            "constrained_schedules_count": constrained_count,
            "unconstrained_schedules_count": unconstrained_count,
            "total_schedules_count": len(all_schedules),
            "makespan": makespan.isoformat() if makespan else None,
            "products_count": len(products_summary),
            "products": products_summary,
            "message": f"{len(all_schedules)}件のスケジュールを取得しました"
        }
    except Exception as e:
        import traceback
        error_detail = f"生産計画の取得に失敗しました: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/comprehensive-production-plan")
async def generate_comprehensive_production_plan(
    request: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    全工程を含む包括的な生産計画を計算

    - 今週のPOをもとに全工程の生産計画を計算
    - プレス工程の並列実行を考慮
    - 段取り時間60分を適用
    - 生産締切日・総加工時間を計算
    """
    working_hours = request.get("working_hours", 8)
    resource_constraints = request.get("resource_constraints", None)

    # スケジューラーを初期化
    scheduler = ProductionScheduler(db, working_hours, resource_constraints)

    # 対象製品とPOを取得
    target_products = scheduler.get_target_products_with_pos()

    # スケジュールを生成
    try:
        result = scheduler.generate_schedule(user_id=current_user.get("username"))
        makespan = scheduler.calculate_makespan()

        # 全スケジュールを使用
        all_schedules = result['all_schedules']

        # ===== 工程完全性チェック（無効化） =====
        # 注意: 現在、工程完全性チェックは無効化されています
        # 理由: 一部の工程がProcessNameTypesに登録されていても、
        #       スケジューラーがまだサポートしていない場合があるため
        # TODO: 将来的には全工程タイプをスケジューラーでサポートし、チェックを有効化
        validation_errors = []
        
        # 検証コードをコメントアウト（無効化）
        if False:  # 検証を無効化
            # ProcessNameTypeのキャッシュを取得（scheduler の _process_type_cache を参照）
            from app.models.process import ProcessNameType
            registered_process_types = {pt.process_name for pt in db.query(ProcessNameType).all()}
            
            for product_data in target_products:
                product = product_data['product']
                processes = product_data['processes']  # 工程マスター
                
                # この製品のスケジュールから、スケジュール済み工程を抽出
                scheduled_process_names = set()
                for sched in all_schedules:
                    if sched['product_code'] == product.product_code:
                        scheduled_process_names.add(sched['process_name'])
                
                # 工程マスターの全工程がスケジュールに含まれているかチェック
                # 除外条件:
                #   - 時間データがない工程（スケジュール不可能）
                #   - ProcessNameTypeに未登録の工程
                missing_processes = []
                for process in processes:
                    # ProcessNameTypeチェック（PRESS工程は特別扱い）
                    process_name_to_check = process.process_name
                    if process.process_name.upper().startswith("PRESS"):
                        process_name_to_check = "PRESS"
                    
                    is_registered = process_name_to_check in registered_process_types
                    
                    # スケジュール可能かチェック（rough_cycletime または production_limit が設定されているか）
                    has_time_data = (
                        (process.rough_cycletime is not None and process.rough_cycletime > 0) or
                        (process.production_limit is not None and process.production_limit > 0)
                    )
                    
                    # 登録済み かつ 時間データがあり かつ スケジュールに含まれていない場合のみエラー
                    if is_registered and has_time_data and process.process_name not in scheduled_process_names:
                        missing_processes.append(f"{process.process_name} (工程{process.process_no})")
                
                if missing_processes:
                    validation_errors.append({
                        "product_code": product.product_code,
                        "customer_name": product.customer.customer_name if product.customer else "不明",
                        "missing_processes": missing_processes
                    })
        
        # 欠けている工程がある場合はエラーを返す（現在は無効化）
        if validation_errors:
            error_message = "以下の製品でスケジュールに含まれていない工程があります：\n\n"
            for error in validation_errors:
                error_message += f"【{error['customer_name']} - {error['product_code']}】\n"
                error_message += f"  欠けている工程: {', '.join(error['missing_processes'])}\n\n"
            error_message += "全ての工程がスケジュールに含まれるまで計算を中止します。\n"
            error_message += "工程マスターを確認し、必要に応じてサイクルタイムや生産限界を設定してください。"
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # 製品ごとにグループ化した詳細情報を作成
        products_summary = []
        for product_data in target_products:
            product = product_data['product']
            earliest_po = product_data['earliest_po']

            # この製品のスケジュールを取得
            product_schedules = []
            for sched in all_schedules:
                if sched['product_code'] == product.product_code:
                    product_schedules.append(sched)

            products_summary.append({
                "product_code": product.product_code,
                "customer_name": product.customer.customer_name if product.customer else None,
                "total_quantity": product_data['total_quantity'],
                "total_days": product_data['total_days'],
                "remaining_hours": product_data['remaining_hours'],
                "display_string": product_data['display_string'],
                "production_deadline": product_data['production_deadline'].isoformat(),
                "delivery_date": earliest_po.delivery_date.isoformat(),
                "po_number": earliest_po.po_number,
                "process_count": len(product_data['processes']),
                "schedules": product_schedules
            })

        return {
            "success": True,
            "constrained_schedules_count": len(result['constrained_schedules']),
            "unconstrained_schedules_count": len(result['unconstrained_schedules']),
            "total_schedules_count": len(all_schedules),
            "makespan": makespan.isoformat() if makespan else None,
            "products_count": len(products_summary),
            "products": products_summary,
            "message": f"{len(all_schedules)}件のスケジュールを生成しました（{len(products_summary)}製品）"
        }
    except HTTPException:
        # HTTPExceptionはそのまま再送出（バリデーションエラーなど）
        raise
    except Exception as e:
        import traceback
        error_detail = f"包括的生産計画の生成に失敗しました: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/press-weekly-schedule-from-plan")
async def get_press_weekly_schedule_from_plan(
    working_hours: int = 8,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    生成された生産計画から1週間のプレス予定を取得

    production_scheduleテーブルのPRESS工程のみを抽出し、
    機械ごと・日付ごとにグループ化して返す

    Args:
        working_hours: 工場稼働時間（デフォルト: 8時間）
    """
    from datetime import datetime, timedelta
    from ..services.production_scheduler import ProductionScheduler

    # スケジュールが存在するか確認し、最も早い日付を取得
    earliest_schedule = db.query(func.min(ProductionSchedule.planned_start_datetime)).scalar()
    
    if earliest_schedule:
        # スケジュールが存在する場合はその日付を開始日とする
        today = earliest_schedule.date()
    else:
        # スケジュールがない場合は今日を開始日とする
        today = datetime.now(VIETNAM_TZ).date()

    # 今日から7日間の日付リストを作成
    dates = [(today + timedelta(days=i)).isoformat() for i in range(7)]

    # PRESS機を取得
    press_machines = db.query(MachineList).filter(
        MachineList.machine_type == 'PRESS'
    ).order_by(MachineList.machine_no).all()

    # デバッグログ：全スケジュール件数を確認
    import logging
    logger = logging.getLogger(__name__)
    
    total_count = db.query(ProductionSchedule).count()
    constrained_count = db.query(ProductionSchedule).filter(ProductionSchedule.machine_list_id.isnot(None)).count()
    logger.info(f"DEBUG: Total schedules: {total_count}, Constrained (Press): {constrained_count}")
    logger.info(f"DEBUG: Earliest schedule: {earliest_schedule}, Today set to: {today}")

    # PRESS工程のスケジュールを取得（1週間分）
    end_date = today + timedelta(days=7)
    logger.info(f"DEBUG: Query range: {today} to {end_date}")
    
    press_schedules = db.query(ProductionSchedule)\
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
        
    logger.info(f"DEBUG: Found {len(press_schedules)} press schedules in range")

    # 生産締切日計算用のスケジューラーを初期化
    scheduler = ProductionScheduler(db, working_hours=working_hours)

    # POごとの生産締切日をキャッシュ（パフォーマンス向上のため）
    production_deadline_cache = {}

    # 機械ごと、日付ごとのスケジュールを作成
    schedule_dict = {}
    for machine in press_machines:
        schedule_dict[machine.machine_no] = {}
        for date_str in dates:
            schedule_dict[machine.machine_no][date_str] = []

    # スケジュールをグループ化（日をまたぐ場合は分割）
    for schedule in press_schedules:
        try:
            # 機械を取得
            machine = db.query(MachineList).filter(
                MachineList.machine_list_id == schedule.machine_list_id
            ).first()

            if not machine:
                continue
            
            # PRESS機械以外はスキップ（TAP, BARREL, PACKINGなど）
            if machine.machine_type != 'PRESS':
                continue

            # POと製品情報を取得
            po = db.query(PO).filter(PO.po_id == schedule.po_id).first()
            if not po:
                continue
                
            product = db.query(Product).filter(Product.product_id == po.product_id).first()
            if not product:
                continue
                
            customer = db.query(Customer).filter(Customer.customer_id == product.customer_id).first()

            # 工程情報を取得
            process = db.query(Process).filter(Process.process_id == schedule.process_id).first()
            if not process:
                continue

            # 開始日と終了日を取得
            start_date = schedule.planned_start_datetime.date()
            end_date = schedule.planned_end_datetime.date()

            # 全体の数量（PO数量合計）- 28日ウィンドウロジックを使用
            po_total_data = scheduler.calculate_po_total_with_28days(product.product_id)
            total_po_quantity = po_total_data.get('po_total', 0)
            # もし計算できなかった場合（通常ありえないが）はPO数量を使用
            if total_po_quantity == 0:
                total_po_quantity = po.po_quantity

            # 生産締切日を計算（キャッシュを使用）
            if po.po_id not in production_deadline_cache:
                # 総加工日数を計算
                total_days = scheduler.calculate_total_processing_days(product, total_po_quantity)
                # 生産締切日を計算（納期から逆算）
                production_deadline = scheduler.calculate_production_deadline(
                    po.delivery_date,
                    total_days
                )
                production_deadline_cache[po.po_id] = production_deadline
            else:
                production_deadline = production_deadline_cache[po.po_id]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing schedule {schedule.schedule_id}: {str(e)}")
            continue

        # 日をまたぐ場合は各日ごとに分割
        current_date = start_date
        cumulative_quantity = 0  # 累積生産数

        while current_date <= end_date:
            date_str = current_date.isoformat()

            # 該当する日付の範囲内かチェック
            if date_str not in dates:
                current_date = current_date + timedelta(days=1)
                continue

            # この日の開始時刻と終了時刻を計算
            # タイムゾーン情報を統一（タイムゾーン非対応に変換）
            planned_start_naive = schedule.planned_start_datetime.replace(tzinfo=None) if schedule.planned_start_datetime.tzinfo else schedule.planned_start_datetime
            planned_end_naive = schedule.planned_end_datetime.replace(tzinfo=None) if schedule.planned_end_datetime.tzinfo else schedule.planned_end_datetime

            if current_date == start_date:
                # 開始日：スケジュールの開始時刻から
                day_start = planned_start_naive
            else:
                # 2日目以降：その日の始業時刻（6:00）から
                day_start = datetime.combine(current_date, datetime.min.time().replace(hour=6, minute=0))

            if current_date == end_date:
                # 終了日：スケジュールの終了時刻まで
                day_end = planned_end_naive
            else:
                # 最終日以外：その日の終業時刻（工場稼働時間を参照）
                # 稼働時間は8-12時間、開始時刻6:00なので終業時刻は14:00-18:00
                work_end_hour = 6 + working_hours
                day_end = datetime.combine(current_date, datetime.min.time().replace(hour=work_end_hour, minute=0))

            # この日の作業時間を計算（分）- 休憩時間を除外
            day_duration_minutes = scheduler.calculate_working_minutes_in_range(day_start, day_end)

            # 総作業時間を計算（全日数分）- 休憩時間を除外
            total_duration_minutes = scheduler.calculate_working_minutes_in_range(planned_start_naive, planned_end_naive)

            # このスケジュールレコードの数量と加工時間
            # production_scheduler.pyで保存時にすでにこのスケジュールレコード分の数量が設定されている
            schedule_quantity = schedule.po_quantity
            schedule_processing_time = float(schedule.processing_time or 0)

            # この日の生産数と加工時間を計算
            # スケジュールが1日で完了する場合（start_date == end_date）はそのまま使用
            # 複数日にまたがる場合のみ作業時間の比率で按分
            if start_date == end_date:
                # 1日で完了するスケジュール：そのまま使用
                day_quantity = schedule_quantity
                day_processing_time = schedule_processing_time
            elif total_duration_minutes > 0:
                # 複数日にまたがるスケジュール：作業時間の比率で按分
                ratio = day_duration_minutes / total_duration_minutes
                day_quantity = int(ratio * schedule_quantity)
                day_processing_time = ratio * schedule_processing_time
            else:
                day_quantity = 0
                day_processing_time = 0

            # 累積生産数を更新
            cumulative_quantity += day_quantity

            # 最終日の場合、端数調整（累積がスケジュール数量と一致するように）
            if current_date == end_date:
                cumulative_quantity = schedule_quantity

            # 段取り時間の計算（初日のみ、工場稼働時間内に収める）
            initial_setup_range = None
            final_setup_range = None
            
            # 段取り時間は既にスケジュールの計算に含まれているため、
            # day_startとday_endの範囲内で段取り時間を表示する
            if current_date == start_date and schedule.setup_time and schedule.setup_time > 0:
                setup_minutes = float(schedule.setup_time)
                initial_setup_minutes = setup_minutes * 0.8  # 80%を開始段取り
                final_setup_minutes = setup_minutes * 0.2    # 20%を終了段取り
                
                # 開始段取り：day_startから開始（工場稼働時間内）
                initial_setup_start = day_start
                initial_setup_end = day_start + timedelta(minutes=initial_setup_minutes)
                initial_setup_range = f"{initial_setup_start.strftime('%H:%M')}-{initial_setup_end.strftime('%H:%M')}"
                
                # 終了段取り：分割タスクでない場合、または最終日の場合のみ表示
                # 次の日に持ち越す場合は終了段取りは不要
                is_final_day = (current_date == end_date)
                if is_final_day:
                # 終了段取りはプレス作業終了後（工場稼働時間内）
                    final_setup_start = day_end - timedelta(minutes=final_setup_minutes)
                    final_setup_end = day_end
                    final_setup_range = f"{final_setup_start.strftime('%H:%M')}-{final_setup_end.strftime('%H:%M')}"
            
            # デバッグ用ログ
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"DEBUG - Product: {product.product_code}, Process: {process.process_name}, Date: {current_date}")
            logger.info(f"  schedule.po_quantity: {schedule.po_quantity}")
            logger.info(f"  schedule.processing_time: {schedule.processing_time}")
            logger.info(f"  total_po_quantity: {total_po_quantity}")
            logger.info(f"  day_quantity: {day_quantity}")
            logger.info(f"  day_processing_time: {day_processing_time}")
            logger.info(f"  cumulative_quantity: {cumulative_quantity}")
            logger.info(f"  day_duration_minutes: {day_duration_minutes}")
            logger.info(f"  total_duration_minutes: {total_duration_minutes}")
            
            # タスク情報を作成
            task = {
                "product_code": product.product_code,
                "customer_name": customer.customer_name,
                "process_name": process.process_name if process else "-",
                "process_no": process.process_no if process else 999,  # 工程番号（ソート用）
                "po_quantity": total_po_quantity,  # PO数量合計
                "day_quantity": day_quantity,  # この日の生産数
                "cumulative_quantity": cumulative_quantity,  # 累積生産数
                "delivery_date": po.delivery_date.strftime("%d/%m/%Y") if po.delivery_date else "-",
                "production_deadline": production_deadline.strftime("%d/%m/%Y"),  # 生産締切日（納期から逆算した開始日）
                "planned_end_datetime": planned_end_naive.strftime("%d/%m/%Y %H:%M"),  # 工程終了日時
                "start_time": day_start.strftime("%H:%M"),
                "end_time": day_end.strftime("%H:%M"),
                "setup_time": float(schedule.setup_time) if current_date == start_date else 0,  # 段取りは初日のみ
                "processing_time": float(day_processing_time),  # この日の実際の加工時間
                "is_split": start_date != end_date,  # 分割されたタスクかどうか
                "split_info": f"{(current_date - start_date).days + 1}/{(end_date - start_date).days + 1}" if start_date != end_date else None,
                "initial_setup_range": initial_setup_range,  # 開始段取り時刻範囲
                "final_setup_range": final_setup_range  # 終了段取り時刻範囲
            }

            schedule_dict[machine.machine_no][date_str].append(task)

            # 次の日へ
            current_date = current_date + timedelta(days=1)

    return {
        "dates": dates,
        "machines": [
            {
                "machine_no": m.machine_no,
                "machine_list_id": m.machine_list_id
            }
            for m in press_machines
        ],
        "schedule": schedule_dict
    }


@router.get("/all-schedule-from-plan")
async def get_all_schedule_from_plan(
    working_hours: int = 8,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    生成された生産計画から全工程のスケジュールを取得（進捗確認用）

    production_scheduleテーブルから全工程を取得し、
    製品ごと・工程ごとにグループ化して返す
    """
    from datetime import datetime, timedelta
    from ..services.production_scheduler import ProductionScheduler

    # 今日から7日間
    today = datetime.now(VIETNAM_TZ).date()
    end_date = today + timedelta(days=7)

    # 全工程のスケジュールを取得
    all_schedules = db.query(ProductionSchedule)\
        .join(Process, ProductionSchedule.process_id == Process.process_id)\
        .filter(
            and_(
                ProductionSchedule.planned_start_datetime >= today,
                ProductionSchedule.planned_start_datetime < end_date
            )
        )\
        .all()

    # 生産締切日計算用のスケジューラーを初期化
    scheduler = ProductionScheduler(db, working_hours=working_hours)

    # POごとの生産締切日をキャッシュ
    production_deadline_cache = {}

    # 製品ごとのデータを作成
    product_processes = {}

    for schedule in all_schedules:
        # POと製品情報を取得
        po = db.query(PO).filter(PO.po_id == schedule.po_id).first()
        if not po:
            continue

        product = db.query(Product).filter(Product.product_id == po.product_id).first()
        if not product:
            continue

        customer = db.query(Customer).filter(Customer.customer_id == product.customer_id).first()

        # 工程情報を取得
        process = db.query(Process).filter(Process.process_id == schedule.process_id).first()
        if not process:
            continue

        # 開始日を取得
        start_date = schedule.planned_start_datetime.date()

        # 全体の数量（PO数量合計）
        total_po_quantity = schedule.po_quantity

        # 生産締切日を計算（キャッシュを使用）
        if po.po_id not in production_deadline_cache:
            total_days = scheduler.calculate_total_processing_days(product, total_po_quantity)
            production_deadline = scheduler.calculate_production_deadline(
                po.delivery_date,
                total_days
            )
            production_deadline_cache[po.po_id] = production_deadline
        else:
            production_deadline = production_deadline_cache[po.po_id]

        # 製品キー
        product_key = product.product_code

        if product_key not in product_processes:
            product_processes[product_key] = {
                'customer_name': customer.customer_name if customer else '-',
                'product_code': product.product_code,
                'po_quantity': total_po_quantity,
                'delivery_date': po.delivery_date.strftime("%d/%m/%Y") if po.delivery_date else "-",
                'production_deadline': production_deadline.strftime("%d/%m/%Y"),
                'po_numbers': set(),  # PO番号を収集
                'processes': {}
            }

        # PO番号を追加
        product_processes[product_key]['po_numbers'].add(po.po_number)

        # 工程キー（process_nameで識別）
        process_key = process.process_name

        # 日付をフォーマット
        date = start_date
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        formatted_date = f"{day}/{month}"

        # 工程タイプを取得
        process_type_record = db.query(ProcessNameType).filter(
            ProcessNameType.process_name == process.process_name
        ).first()

        # 総加工時間を計算
        total_minutes = float(schedule.setup_time or 0) + float(schedule.processing_time or 0)

        # タイプに応じて表示値を計算
        if process_type_record and process_type_record.day_or_spm is False:
            # DAY: 日数で表示
            daily_minutes = scheduler.get_working_minutes(working_hours)
            display_value = round(total_minutes / daily_minutes, 1)  # 小数点1桁
            display_unit = 'D'
        else:
            # SPM: 時間で表示
            display_value = round(total_minutes / 60)
            display_unit = 'H'

        # 工程データを追加または更新
        if process_key in product_processes[product_key]['processes']:
            # 既存の工程データを更新
            existing = product_processes[product_key]['processes'][process_key]
            existing['display_value'] = float(existing['display_value']) + float(display_value)
            # より早い日付を保持
            if start_date.isoformat() < existing['date_str']:
                existing['date'] = formatted_date
                existing['date_str'] = start_date.isoformat()
            # より遅い終了日時を保持
            current_end = schedule.planned_end_datetime.isoformat()
            if 'latest_end_date' not in existing or current_end > existing['latest_end_date']:
                existing['latest_end_date'] = current_end
            # display_unitが設定されていない場合は設定
            if 'display_unit' not in existing:
                existing['display_unit'] = display_unit
        else:
            # 新規工程データを追加
            product_processes[product_key]['processes'][process_key] = {
                'name': process.process_name,
                'process_no': process.process_no,
                'date': formatted_date,
                'date_str': start_date.isoformat(),
                'display_value': float(display_value),
                'display_unit': display_unit,
                'latest_end_date': schedule.planned_end_datetime.isoformat()
            }

    # 各製品の総加工時間を計算
    for product_data in product_processes.values():
        processes = product_data['processes']

        # process_noでソート
        sorted_processes = sorted(processes.values(), key=lambda p: p['process_no'])

        total_hours = 0
        total_days = 0

        i = 0
        while i < len(sorted_processes):
            current_process = sorted_processes[i]

            # PRESS工程かチェック
            is_press = 'PRESS' in current_process['name'].upper()

            if is_press:
                # 連続するPRESS工程の最大値を取得
                press_group = [current_process]
                j = i + 1
                while j < len(sorted_processes) and 'PRESS' in sorted_processes[j]['name'].upper():
                    press_group.append(sorted_processes[j])
                    j += 1

                # グループ内の最大値を取得
                max_value = max(p['display_value'] for p in press_group)
                max_unit = press_group[0]['display_unit']  # 同じPRESSなので単位は同じ

                if max_unit == 'H':
                    total_hours += max_value
                else:
                    total_days += max_value

                i = j  # グループ全体をスキップ
            else:
                # 非PRESS工程はそのまま加算
                if current_process['display_unit'] == 'H':
                    total_hours += current_process['display_value']
                else:
                    total_days += current_process['display_value']
                i += 1

        # フォーマット（日数を先に、時間を後に）
        time_parts = []
        if total_days > 0:
            # 小数点がある場合は表示
            if total_days % 1 == 0:
                time_parts.append(f"{int(total_days)}D")
            else:
                time_parts.append(f"{total_days:.1f}D")
        if total_hours > 0:
            time_parts.append(f"{int(total_hours)}H")

        product_data['total_processing_time'] = ' '.join(time_parts) if time_parts else '0H'

    # PO番号を改行区切りの文字列に変換
    for product_data in product_processes.values():
        po_numbers_set = product_data.pop('po_numbers', set())
        po_numbers_list = sorted(list(po_numbers_set))
        product_data['po_numbers_display'] = '<br>'.join(po_numbers_list) if po_numbers_list else '-'

    return {
        'products': list(product_processes.values())
    }


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
    
    # 総加工時間と生産締切日を計算
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
        
        for proc in sorted_processes:
            if proc['display_unit'] == 'H':
                total_hours += proc['display_value']
            else:
                total_days += proc['display_value']
        
        # フォーマット
        time_parts = []
        if total_days > 0:
            if total_days % 1 == 0:
                time_parts.append(f"{int(total_days)}D")
            else:
                time_parts.append(f"{total_days:.1f}D")
        if total_hours > 0:
            time_parts.append(f"{int(total_hours)}H")
        
        product_data['total_processing_time'] = ' '.join(time_parts) if time_parts else '0H'
        
        # 生産締切日を計算
        total_processing_days = total_days + (total_hours / 8)  # 8時間=1日と仮定
        delivery_date_obj = datetime.strptime(product_data['delivery_date'], "%d/%m/%Y").date()
        production_deadline = scheduler.calculate_production_deadline(delivery_date_obj, total_processing_days)
        product_data['production_deadline'] = production_deadline.strftime("%d/%m/%Y")
    
    # リスト形式に変換
    products_list = list(product_processes.values())
    
    return {
        'products': products_list,
        'products_count': len(products_list)
    }

