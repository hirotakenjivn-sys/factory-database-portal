"""
納期計算ユーティリティ

DAY工程とSPM工程を考慮した納期計算ロジックを提供します。
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict
from decimal import Decimal
import math

from ..models.process import Process, ProcessNameType
from ..models.calendar import Calendar
from ..models.factory import Factory, WorkingHours


def get_holidays(db: Session, start_date: date, end_date: date) -> List[date]:
    """
    指定期間内の休日一覧を取得
    """
    holidays = db.query(Calendar.date_holiday).filter(
        Calendar.date_holiday >= start_date,
        Calendar.date_holiday <= end_date
    ).all()
    return [h[0] for h in holidays]


def is_business_day(target_date: date, holidays: List[date]) -> bool:
    """
    営業日かどうかを判定（土日と休日を除外）
    """
    # 土曜=5, 日曜=6
    if target_date.weekday() >= 5:
        return False
    if target_date in holidays:
        return False
    return True


def add_business_days(start_date: date, days: int, holidays: List[date]) -> date:
    """
    指定日から営業日ベースで日数を加算

    Args:
        start_date: 開始日
        days: 追加する営業日数
        holidays: 休日リスト

    Returns:
        date: 計算後の日付
    """
    current_date = start_date
    business_days_added = 0

    while business_days_added < days:
        current_date += timedelta(days=1)
        if is_business_day(current_date, holidays):
            business_days_added += 1

    return current_date


def calculate_day_process_duration(
    po_quantity: int,
    rough_cycletime: Decimal,
    production_limit: int
) -> int:
    """
    DAY工程の所要日数を計算

    Args:
        po_quantity: PO数量
        rough_cycletime: 1サイクルの日数
        production_limit: 1サイクルで生産できる数量

    Returns:
        int: 必要な営業日数

    計算式:
        必要サイクル数 = CEILING(PO数量 / 生産限界)
        必要日数 = 必要サイクル数 × rough_cycletime

    例:
        PO数量=5,000個、rough_cycletime=1日、production_limit=2,500個
        → 必要サイクル数 = CEILING(5000/2500) = 2
        → 必要日数 = 2 * 1 = 2日
    """
    if production_limit <= 0:
        raise ValueError("production_limit must be greater than 0")

    # 必要サイクル数を計算（切り上げ）
    required_cycles = math.ceil(po_quantity / production_limit)

    # 必要日数を計算
    required_days = required_cycles * float(rough_cycletime)

    return int(math.ceil(required_days))


def calculate_spm_process_duration(
    po_quantity: int,
    rough_cycletime: Decimal,
    working_hours_per_day: Decimal
) -> int:
    """
    SPM工程の所要日数を計算

    Args:
        po_quantity: PO数量
        rough_cycletime: 1分間に生産できる個数（個/分）
        working_hours_per_day: 1日あたりの稼働時間（時間）

    Returns:
        int: 必要な営業日数（切り上げ）

    計算式:
        総生産時間（分） = PO数量 / rough_cycletime
        1日あたりの稼働分数 = working_hours_per_day × 60
        必要日数 = CEILING(総生産時間（分） / 稼働分数)

    例:
        PO数量=5,000個、rough_cycletime=60個/分、稼働時間=8時間/日
        → 総生産時間 = 5000 / 60 = 83.33分
        → 稼働分数 = 8 × 60 = 480分/日
        → 必要日数 = CEILING(83.33 / 480) = 1日
    """
    if working_hours_per_day <= 0:
        raise ValueError("working_hours_per_day must be greater than 0")

    if rough_cycletime <= 0:
        raise ValueError("rough_cycletime must be greater than 0")

    # 総生産時間（分）
    total_minutes = po_quantity / float(rough_cycletime)

    # 1日あたりの稼働分数
    daily_minutes = float(working_hours_per_day) * 60

    # 必要日数（切り上げ）
    required_days = total_minutes / daily_minutes

    return int(math.ceil(required_days))


def calculate_delivery_date(
    db: Session,
    product_id: int,
    po_quantity: int,
    start_date: date
) -> Dict:
    """
    製品のPO数量と開始日から納期を計算

    Args:
        db: データベースセッション
        product_id: 製品ID
        po_quantity: PO数量
        start_date: 開始日（通常はPO受領日）

    Returns:
        Dict: {
            "delivery_date": date,  # 計算された納期
            "total_days": int,      # 総所要日数（営業日ベース）
            "processes": [          # 各工程の詳細
                {
                    "process_no": int,
                    "process_name": str,
                    "days": int,
                    "start_date": date,
                    "end_date": date
                },
                ...
            ]
        }
    """
    # 製品の全工程を取得（工程番号順）
    processes = db.query(Process).filter(
        Process.product_id == product_id
    ).order_by(Process.process_no).all()

    if not processes:
        raise ValueError(f"No processes found for product_id={product_id}")

    # デフォルトの稼働時間を取得（最初の工場のもの）
    working_hours_record = db.query(WorkingHours).first()
    working_hours_per_day = Decimal(8.0) if not working_hours_record else working_hours_record.hours

    # 休日リストを取得（開始日から最大1年後まで）
    end_date_estimate = start_date + timedelta(days=365)
    holidays = get_holidays(db, start_date, end_date_estimate)

    # 各工程の計算結果
    process_details = []
    current_date = start_date
    total_days = 0

    for process in processes:
        # 工程名マスタから工程タイプを取得
        process_name_type = db.query(ProcessNameType).filter(
            ProcessNameType.process_name == process.process_name
        ).first()

        # day_or_spmがNoneの場合は、production_limitの有無で判断
        if process_name_type:
            is_spm = process_name_type.day_or_spm
        else:
            # production_limitがあればDAY工程、なければSPM工程とみなす
            is_spm = process.production_limit is None

        # 工程の所要日数を計算
        if is_spm:
            # SPM工程
            if process.rough_cycletime is None or process.rough_cycletime <= 0:
                # サイクルタイムが設定されていない場合は0日とする
                days_required = 0
            else:
                days_required = calculate_spm_process_duration(
                    po_quantity,
                    process.rough_cycletime,
                    working_hours_per_day
                )
        else:
            # DAY工程
            if process.production_limit is None or process.production_limit <= 0:
                raise ValueError(
                    f"Process {process.process_name} (No.{process.process_no}) is DAY type but production_limit is not set"
                )
            if process.rough_cycletime is None or process.rough_cycletime <= 0:
                raise ValueError(
                    f"Process {process.process_name} (No.{process.process_no}) is DAY type but rough_cycletime is not set"
                )

            days_required = calculate_day_process_duration(
                po_quantity,
                process.rough_cycletime,
                process.production_limit
            )

        # 営業日ベースで日数を加算
        process_start_date = current_date
        process_end_date = add_business_days(current_date, days_required, holidays)

        process_details.append({
            "process_id": process.process_id,
            "process_no": process.process_no,
            "process_name": process.process_name,
            "process_type": "SPM" if is_spm else "DAY",
            "days": days_required,
            "start_date": process_start_date,
            "end_date": process_end_date,
            "rough_cycletime": float(process.rough_cycletime) if process.rough_cycletime else None,
            "production_limit": process.production_limit,
        })

        current_date = process_end_date
        total_days += days_required

    return {
        "delivery_date": current_date,
        "total_days": total_days,
        "processes": process_details,
        "start_date": start_date,
        "po_quantity": po_quantity,
        "product_id": product_id,
    }
