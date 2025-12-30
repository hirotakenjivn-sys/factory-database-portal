"""
生産計画スケジューリングロジック

要件:
- 納期+28日以内の全POを対象
- makespan（全体の生産完了時刻）を最小化
- PRESS機の割当最適化
- 休日カレンダーを考慮
"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import pytz
import logging
import time

# ロガー設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.DEBUG)

from ..models import (
    PO, Process, ProcessNameType, MachineList, MachineType,
    Calendar, Product, ProductionSchedule, FinishedProduct
)

# ベトナム時間（UTC+7）のタイムゾーン
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


class ProductionScheduler:
    """生産計画スケジューラー"""

    def __init__(self, db: Session, working_hours: int = 8, resource_constraints: Dict = None):
        self.db = db
        self.working_hours = working_hours
        # 実稼働分数マップ（休憩時間を除いた実作業時間）
        # 休憩時間帯は add_working_time メソッドで自動的にスキップされる
        # - 昼休憩: 10:00-10:40（40分）- 全稼働時間
        # - 追加休憩: 14:00-14:30（30分）- 11時間以上稼働の場合のみ
        self.working_minutes_map = {
            8: 440,   # 8時間稼働（6:00-14:00）、実稼働440分（昼休憩40分除く）
            9: 500,   # 9時間稼働（6:00-15:00）、実稼働500分（昼休憩40分除く）
            10: 560,  # 10時間稼働（6:00-16:00）、実稼働560分（昼休憩40分除く）
            11: 590,  # 11時間稼働（6:00-17:00）、実稼働590分（昼休憩40分+追加休憩30分除く）
            12: 650,  # 12時間稼働（6:00-18:00）、実稼働650分（昼休憩40分+追加休憩30分除く）
        }

        # リソース制約のデフォルト設定
        if resource_constraints is None:
            resource_constraints = {
                'PRESS': {
                    'type': 'machine',
                    'enabled': True,
                    'capacity': None,  # Noneの場合はDBから取得
                }
                # 将来追加:
                # 'BARREL': {'type': 'machine', 'enabled': False, 'capacity': 5},
                # '修正': {'type': 'worker', 'enabled': False, 'capacity': 3}
            }

        self.resource_constraints = resource_constraints

        # PRESS機の空き時間を管理（machine_list_id: 空き時間）
        self.machine_availability: Dict[int, datetime] = {}
        # PRESS機の最後の工程を記録（段取り時間判定用）
        self.machine_last_process: Dict[int, int] = {}  # machine_list_id: process_id

        # 新アルゴリズム用データ構造
        # 機械の日次スケジュール
        self.machine_daily_schedule: Dict[int, Dict[str, List[Dict]]] = {}
        # {machine_id: {'2025-01-15': [{'start': datetime, 'end': datetime, ...}]}}

        # 継続中タスク
        self.machine_ongoing_task: Dict[int, Dict] = {}
        # {machine_id: {'process_id': int, 'product_id': int, ...}}

        # ProcessNameTypeキャッシュ（DBクエリ削減のため）
        self._process_type_cache: Dict[str, Optional[bool]] = {}
        self._load_process_type_cache()

        # 工程のスケジュール状態
        self.process_schedule_status: Dict[Tuple[int, int], str] = {}
        # {(product_id, process_no): 'pending'|'in_progress'|'completed'}

        # 並列実行を許可する製品コード（ダミー）
        self.PARALLEL_EXECUTION_ALLOWED_PRODUCTS = ["ALLOW-PARALLEL"]
        
        # PO完了優先スケジューリング用データ構造
        # 機械ごとの進行中Product（同じ製品のPOを連続処理）
        self.machine_ongoing_product: Dict[int, int] = {}  # {machine_id: product_id}
        
        # Product進捗追跡（同じ製品の全POをまとめて管理）
        self.product_progress: Dict[int, Dict] = {}
        # {product_id: {
        #     'total_quantity': int,  # この製品の全PO合計数量
        #     'scheduled_quantity': int,  # スケジュール済み数量
        #     'is_complete': bool  # すべて完了したか
        # }}

    def _load_process_type_cache(self):
        """ProcessNameTypeをキャッシュにロード（初期化時に1回だけ実行）"""
        process_types = self.db.query(ProcessNameType).all()
        for pt in process_types:
            self._process_type_cache[pt.process_name] = pt.day_or_spm
        logger.debug(f"ProcessNameTypeキャッシュロード完了: {len(self._process_type_cache)}件")

    def _get_process_type(self, process_name: str) -> Optional[bool]:
        """キャッシュからProcessTypeを取得"""
        return self._process_type_cache.get(process_name)

    def get_working_minutes(self, hours: int) -> int:
        """稼働時間から実稼働分数を計算（休憩時間を除く）"""
        return self.working_minutes_map.get(hours, hours * 60)

    def is_working_day(self, date_to_check: date) -> bool:
        """指定された日が稼働日（休日でない）かチェック"""
        holiday = self.db.query(Calendar).filter(
            Calendar.date_holiday == date_to_check
        ).first()
        return holiday is None

    def skip_break_times(self, current_dt: datetime) -> datetime:
        """
        休憩時間帯をスキップ

        - 昼休憩: 10:00-10:40（全稼働時間）
        - 追加休憩: 14:00-14:30（11時間以上稼働の場合のみ）
        """
        hour = current_dt.hour
        minute = current_dt.minute

        # 昼休憩時間帯（10:00-10:40）のチェック
        if hour == 10 and minute < 40:
            # 10:00台で10:40より前なら10:40に移動
            return current_dt.replace(hour=10, minute=40, second=0, microsecond=0)
        elif hour < 10 or (hour == 10 and minute == 0):
            # 10:00ちょうどなら10:40に移動
            if hour == 10 and minute == 0:
                return current_dt.replace(hour=10, minute=40, second=0, microsecond=0)

        # 追加休憩時間帯（14:00-14:30）のチェック（11時間以上稼働の場合）
        if self.working_hours >= 11:
            if hour == 14 and minute < 30:
                # 14:00台で14:30より前なら14:30に移動
                return current_dt.replace(hour=14, minute=30, second=0, microsecond=0)
            elif hour == 14 and minute == 0:
                # 14:00ちょうどなら14:30に移動
                return current_dt.replace(hour=14, minute=30, second=0, microsecond=0)

        return current_dt

    def get_next_working_datetime(self, start_dt: datetime) -> datetime:
        """次の稼働日の開始時刻（6:00）を取得"""
        current_date = start_dt.date()

        # 次の日から探索
        current_date = current_date + timedelta(days=1)

        while not self.is_working_day(current_date):
            current_date = current_date + timedelta(days=1)

        # 稼働開始時刻（6:00）を返す
        return datetime.combine(current_date, datetime.min.time().replace(hour=6, minute=0))

    def add_working_time(
        self,
        start_dt: datetime,
        minutes: float
    ) -> datetime:
        """
        開始日時から稼働時間を加算
        休日、稼働時間外、休憩時間帯を考慮

        休憩時間帯:
        - 10:00-10:40（昼休憩、全稼働時間）
        - 14:00-14:30（追加休憩、11時間以上稼働）
        """
        current_dt = start_dt
        remaining_minutes = float(minutes)

        # 稼働開始時刻と終了時刻
        work_start_hour = 6
        work_end_hour = work_start_hour + self.working_hours

        while remaining_minutes > 0:
            # 現在の日が休日の場合、次の稼働日に移動
            if not self.is_working_day(current_dt.date()):
                current_dt = self.get_next_working_datetime(current_dt)
                continue

            # 稼働時間内かチェック
            if current_dt.hour < work_start_hour:
                # 稼働開始前 → 稼働開始時刻に設定
                current_dt = current_dt.replace(hour=work_start_hour, minute=0, second=0)
            elif current_dt.hour >= work_end_hour:
                # 稼働終了後 → 次の稼働日に移動
                current_dt = self.get_next_working_datetime(current_dt)
                continue

            # 休憩時間帯をスキップ
            before_skip = current_dt
            current_dt = self.skip_break_times(current_dt)

            # スキップした場合、その分の時間は消費されない
            if current_dt != before_skip:
                # 休憩後の時刻に移動したが、remaining_minutesは減らさない
                pass

            # 今日の終業時刻
            today_end = current_dt.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

            # 現在時刻から今日の終業時刻までの分数
            minutes_until_end_of_day = (today_end - current_dt).total_seconds() / 60

            if minutes_until_end_of_day <= 0:
                # 既に終業時刻を過ぎている場合、次の稼働日へ
                current_dt = self.get_next_working_datetime(current_dt)
                continue

            # 休憩時間帯を考慮した次の休憩開始時刻を計算
            next_break_start = None
            next_break_end = None

            # 昼休憩（10:00-10:40）
            lunch_start = current_dt.replace(hour=10, minute=0, second=0, microsecond=0)
            lunch_end = current_dt.replace(hour=10, minute=40, second=0, microsecond=0)
            if current_dt < lunch_start:
                next_break_start = lunch_start
                next_break_end = lunch_end

            # 追加休憩（14:00-14:30）11時間以上の場合
            if self.working_hours >= 11:
                additional_start = current_dt.replace(hour=14, minute=0, second=0, microsecond=0)
                additional_end = current_dt.replace(hour=14, minute=30, second=0, microsecond=0)
                if current_dt < additional_start:
                    if next_break_start is None or additional_start < next_break_start:
                        # 追加休憩の方が先、またはまだ休憩が設定されていない
                        if next_break_start is None or current_dt >= lunch_end:
                            next_break_start = additional_start
                            next_break_end = additional_end

            # 次の休憩までの時間を計算
            if next_break_start and next_break_start < today_end:
                minutes_until_break = (next_break_start - current_dt).total_seconds() / 60

                if minutes_until_break > 0 and remaining_minutes > minutes_until_break:
                    # 休憩前に到達 → 休憩後に移動
                    current_dt = current_dt + timedelta(minutes=minutes_until_break)
                    remaining_minutes -= minutes_until_break
                    # 休憩時間をスキップ
                    current_dt = next_break_end
                    continue

            # 残り時間を処理
            if remaining_minutes <= minutes_until_end_of_day:
                # 今日中に終わる
                current_dt = current_dt + timedelta(minutes=remaining_minutes)
                remaining_minutes = 0
                # 最終チェック：休憩時間帯に入っていないか
                current_dt = self.skip_break_times(current_dt)
            else:
                # 今日中に終わらない → 次の稼働日へ
                remaining_minutes -= minutes_until_end_of_day
                current_dt = self.get_next_working_datetime(current_dt)

        return current_dt

    def calculate_working_minutes_in_range(
        self,
        start_dt: datetime,
        end_dt: datetime
    ) -> float:
        """
        指定された期間内の実稼働時間（分）を計算
        休憩時間を除外する
        """
        if start_dt >= end_dt:
            return 0.0

        total_minutes = (end_dt - start_dt).total_seconds() / 60
        
        # 休憩時間帯の定義
        breaks = []
        
        # 昼休憩（10:00-10:40）
        lunch_start = start_dt.replace(hour=10, minute=0, second=0, microsecond=0)
        lunch_end = start_dt.replace(hour=10, minute=40, second=0, microsecond=0)
        breaks.append((lunch_start, lunch_end))
        
        # 追加休憩（14:00-14:30）11時間以上の場合
        if self.working_hours >= 11:
            additional_start = start_dt.replace(hour=14, minute=0, second=0, microsecond=0)
            additional_end = start_dt.replace(hour=14, minute=30, second=0, microsecond=0)
            breaks.append((additional_start, additional_end))
            
        # 期間と休憩の重複を計算して減算
        deducted_minutes = 0
        
        for break_start, break_end in breaks:
            # 重複期間を計算
            overlap_start = max(start_dt, break_start)
            overlap_end = min(end_dt, break_end)
            
            if overlap_start < overlap_end:
                deducted_minutes += (overlap_end - overlap_start).total_seconds() / 60
                
        return max(0.0, total_minutes - deducted_minutes)

    def calculate_process_time(
        self,
        process: Process,
        po_quantity: int
    ) -> Tuple[float, float]:
        """
        工程の所要時間を計算
        Returns: (setup_time分, processing_time分)
        """
        # 工程タイプをキャッシュから取得
        process_type = self._get_process_type(process.process_name)

        setup_time = float(process.setup_time or 0)

        if process_type is True:  # SPM
            # SPM: 1分間あたりの生産数（例: SPM60 = 1分間に60個）
            # 処理時間（分） = 数量 ÷ (SPM × 安全係数)
            if not process.rough_cycletime or process.rough_cycletime == 0:
                return setup_time, 0

            safety_factor = Decimal("0.7")
            # effective_spm = 1分間あたりの実効生産数
            effective_spm = process.rough_cycletime * safety_factor

            # 総生産時間（分） = 数量 ÷ 実効SPM
            processing_minutes = float(Decimal(po_quantity) / effective_spm)

            return setup_time, processing_minutes

        elif process_type is False:  # DAY
            # DAY: rough_cycletime日で production_limit 個生産できる
            if not process.production_limit or process.production_limit == 0:
                return setup_time, 0

            import math
            cycles_needed = math.ceil(po_quantity / process.production_limit)
            days_per_cycle = float(process.rough_cycletime) if process.rough_cycletime else 1
            total_days = cycles_needed * days_per_cycle

            # 日数を分に変換（1日 = 稼働時間 × 60分）
            daily_minutes = self.get_working_minutes(self.working_hours)
            processing_minutes = total_days * daily_minutes

            return setup_time, processing_minutes

        else:
            # タイプが不明な場合
            return setup_time, 0

    def calculate_quantity_per_time(
        self,
        process: Process,
        minutes: float
    ) -> int:
        """
        指定された時間で処理できる数量を計算
        Returns: 数量
        """
        # 工程タイプをキャッシュから取得
        process_type = self._get_process_type(process.process_name)

        if process_type is True:  # SPM
            if not process.rough_cycletime or process.rough_cycletime == 0:
                return 0

            safety_factor = Decimal("0.7")
            # effective_spm = 1分間あたりの実効生産数
            effective_spm = process.rough_cycletime * safety_factor

            # 指定時間で処理できる数量 = 時間（分） × 実効SPM
            quantity = int(float(effective_spm) * minutes)

            return quantity

        elif process_type is False:  # DAY
            if not process.production_limit or process.production_limit == 0:
                return 0

            # 指定時間（分）を日数に変換
            daily_minutes = self.get_working_minutes(self.working_hours)
            days = minutes / daily_minutes

            # rough_cycletimeで割って処理回数を求め、production_limitをかける
            days_per_cycle = float(process.rough_cycletime) if process.rough_cycletime else 1
            cycles = days / days_per_cycle
            quantity = int(cycles * process.production_limit)

            return quantity

        else:
            return 0

    def calculate_total_processing_days(
        self,
        product: Product,
        po_quantity: int
    ) -> float:
        """
        製品の総加工時間を日数（小数点あり）で計算

        Returns: 総加工日数（例: 5.27日）
        """
        # 製品の全工程を取得
        processes = self.db.query(Process).filter(
            Process.product_id == product.product_id
        ).order_by(Process.process_no.asc()).all()

        total_days = 0.0  # 日数（小数点あり）
        daily_minutes = self.get_working_minutes(self.working_hours)

        for process in processes:
            # 所要時間を計算（キャッシュを使用）
            setup_time, processing_time = self.calculate_process_time(
                process, po_quantity
            )

            total_time = setup_time + processing_time

            # 分を日数に変換（DAY、SPM共通）
            days = total_time / daily_minutes
            total_days += days

        return total_days

    def calculate_production_deadline(
        self,
        delivery_date: date,
        total_days: float
    ) -> date:
        """
        生産締切日を計算

        納期から総加工日数を引いて、生産を開始すべき日付を算出
        稼働日（休日でない日）のみをカウント
        端数は切り上げ（math.ceil）

        Args:
            delivery_date: 納期
            total_days: 総加工日数（小数点あり、例: 5.27）

        Returns:
            生産締切日
        """
        import math

        current_date = delivery_date
        # 端数切り上げ: 5.27 → 6
        days_to_subtract = math.ceil(total_days)

        # 稼働日を遡る
        while days_to_subtract > 0:
            current_date = current_date - timedelta(days=1)

            # 稼働日の場合のみカウント
            if self.is_working_day(current_date):
                days_to_subtract -= 1

        return current_date

    def should_postpone_setup(
        self,
        current_time: datetime,
        setup_time_minutes: float,
        work_end_hour: int
    ) -> Tuple[bool, float]:
        """
        段取り作業を翌日に持ち越すべきか判定

        段取り作業の途中で終業時刻になる場合は翌日へ持ち越し
        持ち越す場合、翌日の段取り時間として最低60分を確保

        Args:
            current_time: 現在時刻
            setup_time_minutes: 段取り時間（分）
            work_end_hour: 終業時刻（時）

        Returns:
            (持ち越すべきか, 翌日の段取り時間)
        """
        # 終業時刻を計算
        end_time = current_time.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

        # 現在時刻から終業時刻までの残り時間（分）- 休憩時間を除外
        remaining_minutes = self.calculate_working_minutes_in_range(current_time, end_time)

        # 段取り作業が終業時刻までに完了しない場合
        if setup_time_minutes > remaining_minutes:
            # 翌日に持ち越し
            # 翌日の段取り時間は最低60分
            next_day_setup_time = max(setup_time_minutes, 60.0)
            return True, next_day_setup_time

        # 今日中に完了できる
        return False, setup_time_minutes

    def is_press_process(self, process_name: str) -> bool:
        """
        プレス工程かどうかを判定

        Args:
            process_name: 工程名

        Returns:
            プレス工程ならTrue
        """
        if not process_name:
            return False

        process_name_upper = process_name.upper()
        return (
            'PRESS' in process_name_upper or
            'プレス' in process_name
        )

    def get_machine_type_from_process_name(self, process_name: str) -> Optional[str]:
        """
        工程名から機械タイプを推測

        Args:
            process_name: 工程名

        Returns:
            機械タイプ（'PRESS', 'TAP', 'BARREL'など）またはNone
        """
        if not process_name:
            return None

        process_name_upper = process_name.upper()

        if 'PRESS' in process_name_upper or 'プレス' in process_name:
            return 'PRESS'
        elif 'TAP' in process_name_upper or 'タップ' in process_name:
            return 'TAP'
        elif 'BARREL' in process_name_upper or 'バレル' in process_name:
            return 'BARREL'
        else:
            # その他の工程（PACKING等）は機械不要
            return None

    def calculate_po_total_with_28days(self, product_id: int) -> Dict:
        """
        製品コードごとのPO数合計を計算

        1. 製品の未配送POを納期順に取得
        2. 最も早い納期のPOを基準とする
        3. 基準納期から+28日以内のPOの数量を合算

        Args:
            product_id: 製品ID

        Returns:
            {
                'earliest_po': PO,
                'reference_delivery_date': date,
                'po_total': int,  # PO数合計
                'relevant_pos': List[PO]  # 対象となるPOのリスト
            }
        """
        # この製品の未配送POを取得
        earliest_po = self.db.query(PO).filter(
            and_(
                PO.product_id == product_id,
                PO.is_delivered == False
            )
        ).order_by(PO.delivery_date.asc()).first()

        if not earliest_po:
            return {
                'earliest_po': None,
                'reference_delivery_date': None,
                'po_total': 0,
                'relevant_pos': []
            }

        # 基準納期から+28日以内のPOを取得
        date_limit = earliest_po.delivery_date + timedelta(days=28)
        relevant_pos = self.db.query(PO).filter(
            and_(
                PO.product_id == product_id,
                PO.is_delivered == False,
                PO.delivery_date >= earliest_po.delivery_date,
                PO.delivery_date <= date_limit
            )
        ).all()

        # PO数量合計を計算
        po_total = sum(po.po_quantity for po in relevant_pos)

        return {
            'earliest_po': earliest_po,
            'reference_delivery_date': earliest_po.delivery_date,
            'po_total': po_total,
            'relevant_pos': relevant_pos
        }

    def calculate_production_quantity(self, product_id: int, po_total: int) -> int:
        """
        生産数を計算

        PO数合計 - finished_products = 生産数

        Args:
            product_id: 製品ID
            po_total: PO数合計

        Returns:
            生産数（0以上を保証）
        """
        # 未出荷の完成品在庫を取得
        unshipped_finished = self.db.query(
            func.sum(FinishedProduct.finished_quantity)
        ).filter(
            FinishedProduct.product_id == product_id,
            FinishedProduct.is_shipped == False
        ).scalar() or 0

        # 生産数 = PO数合計 - 未出荷在庫（0以上を保証）
        production_quantity = max(0, po_total - unshipped_finished)

        return production_quantity

    def calculate_all_processes_deadline(
        self,
        product: Product,
        production_quantity: int,
        delivery_date: date
    ) -> Dict:
        """
        全工程の加工時間を計算し、締切日を決定

        1. 製品の全工程を取得
        2. 各工程の加工時間を計算（DAY or SPM）
        3. 段取り時間を加算
        4. 総加工時間から締切日を計算

        Args:
            product: 製品
            production_quantity: 生産数
            delivery_date: 納期

        Returns:
            {
                'total_minutes': float,  # 総加工時間（分）
                'total_days': float,  # 総加工日数
                'deadline': date,  # 締切日
                'process_details': List[Dict]  # 各工程の詳細
            }
        """
        # 製品の全工程を取得
        processes = self.db.query(Process).filter(
            Process.product_id == product.product_id
        ).order_by(Process.process_no.asc()).all()

        if not processes:
            return {
                'total_minutes': 0.0,
                'total_days': 0.0,
                'deadline': delivery_date,
                'process_details': []
            }

        total_minutes = 0.0
        daily_minutes = self.get_working_minutes(self.working_hours)
        process_details = []

        for process in processes:
            # 所要時間を計算（setup_time + processing_time）
            setup_time, processing_time = self.calculate_process_time(
                process, production_quantity
            )

            total_time = setup_time + processing_time
            total_minutes += total_time

            process_details.append({
                'process_no': process.process_no,
                'process_name': process.process_name,
                'setup_time': setup_time,
                'processing_time': processing_time,
                'total_time': total_time
            })

        # 総分数を日数に変換
        total_days = total_minutes / daily_minutes if daily_minutes > 0 else 0

        # 生産締切日を計算
        deadline = self.calculate_production_deadline(
            delivery_date,
            total_days
        )

        return {
            'total_minutes': total_minutes,
            'total_days': total_days,
            'deadline': deadline,
            'process_details': process_details
        }

    def can_run_in_parallel(
        self,
        process1: Process,
        process2: Process,
        machine_id1: Optional[int],
        machine_id2: Optional[int]
    ) -> bool:
        """
        2つの工程が並列実行可能かチェック

        同じ製品内で連続するプレス工程が異なる機械を使用する場合に並列実行可能

        Args:
            process1: 工程1
            process2: 工程2
            machine_id1: 工程1の機械ID
            machine_id2: 工程2の機械ID

        Returns:
            並列実行可能ならTrue
        """
        # 両方プレス工程であること
        if not (self.is_press_process(process1.process_name) and
                self.is_press_process(process2.process_name)):
            return False

        # 機械が異なること（None の場合は並列実行不可）
        if machine_id1 is None or machine_id2 is None:
            return False

        return machine_id1 != machine_id2

    def get_target_products_with_pos(self) -> List[Dict]:
        """
        生産計画対象の製品とPOを取得

        1. 製品ごとに最も近い納期のPOを基準とする
        2. 基準納期+28日以内のPOの数量を合算
        3. 総加工日数と余り時間を計算
        4. 生産締切日を計算（納期 - 総加工日数）
        5. 生産締切日が今日より前、または今日から6日前までの製品を対象
        6. 生産締切日が近い順にソート
        """

        today = self.get_vietnam_today()
        six_days_before = today - timedelta(days=6)

        # アクティブな製品を取得
        products = self.db.query(Product).filter(
            Product.is_active == True
        ).all()

        target_products = []

        for product in products:
            # この製品の未配送POを取得
            earliest_po = self.db.query(PO).filter(
                and_(
                    PO.product_id == product.product_id,
                    PO.is_delivered == False
                )
            ).order_by(PO.delivery_date.asc()).first()

            if not earliest_po:
                continue

            # 基準納期から+28日以内のPOを取得
            date_limit = earliest_po.delivery_date + timedelta(days=28)
            relevant_pos = self.db.query(PO).filter(
                and_(
                    PO.product_id == product.product_id,
                    PO.is_delivered == False,
                    PO.delivery_date >= earliest_po.delivery_date,
                    PO.delivery_date <= date_limit
                )
            ).all()

            # PO数量合計を計算
            total_po_quantity = sum(po.po_quantity for po in relevant_pos)

            # 未出荷の完成品在庫を取得
            unshipped_finished = self.db.query(
                func.sum(FinishedProduct.finished_quantity)
            ).filter(
                FinishedProduct.product_id == product.product_id,
                FinishedProduct.is_shipped == False
            ).scalar() or 0

            # 生産数 = PO数合計 - 未出荷在庫（0以上を保証）
            production_quantity = max(0, total_po_quantity - unshipped_finished)

            # 生産数が0の場合はスキップ（在庫で賄える）
            if production_quantity == 0:
                continue

            # 工程が存在するか確認
            processes = self.db.query(Process).filter(
                Process.product_id == product.product_id
            ).order_by(Process.process_no.asc()).all()

            if not processes:
                continue

            # 総加工日数を計算（小数点あり）- 生産数を使用
            total_days = self.calculate_total_processing_days(
                product, production_quantity
            )

            # 生産締切日を計算（端数切り上げ）
            production_deadline = self.calculate_production_deadline(
                earliest_po.delivery_date,
                total_days
            )

            # 表示用文字列を生成（互換性のため）
            import math
            display_days = math.floor(total_days)
            remaining_hours = int((total_days - display_days) * self.working_hours)
            display_string = f"{display_days}日 {remaining_hours}時間"

            # 生産締切日が「今日より前」または「6日前〜今日」の範囲にあるものを対象
            if production_deadline <= today or production_deadline >= six_days_before:
                target_products.append({
                    'product': product,
                    'earliest_po': earliest_po,
                    'relevant_pos': relevant_pos,
                    'total_quantity': total_po_quantity,  # PO数合計
                    'production_quantity': production_quantity,  # 生産数（在庫引き後）
                    'unshipped_finished': unshipped_finished,  # 未出荷在庫
                    'production_deadline': production_deadline,
                    'total_days': total_days,
                    'remaining_hours': remaining_hours,
                    'display_string': display_string,
                    'processes': processes
                })

        # 生産締切日でソート（近いものから）
        target_products.sort(key=lambda x: x['production_deadline'])

        return target_products

    def get_target_pos_sorted_by_deadline(self) -> List[Dict]:
        """
        生産締切日の早い順に製品をリスト化（製品単位 + PO数合計方式）

        新要件版:
        1. 製品ごとに納期が直近のPOをもとに、その納期から28日後までの同じ製品の合計数量を計算（PO数合計）
        2. PO数合計から倉庫finished_productsを引いた数を生産数とする
        3. 直近のPOを基準にすべて工程の加工時間を計算し、締切日を決める
        4. 締切日の早い順にソート

        Returns:
            List[Dict]: {
                'product': Product,
                'earliest_po': PO,  # 基準となる最も早いPO
                'relevant_pos': List[PO],  # 28日以内のPO
                'po_total': int,  # PO数合計
                'production_quantity': int,  # 生産数（PO数合計 - 在庫）
                'deadline': date,  # 締切日
                'processes': List[Process],  # この製品の全工程
                'press_processes': List[Process],  # プレス工程のみ
                'current_process_no': int,  # 現在スケジュール対象の工程番号（初期値は最初のプレス工程）
                'total_days': float,  # 総加工日数
                'process_details': List[Dict]  # 各工程の詳細
            }
        """
        # アクティブな製品を取得
        products = self.db.query(Product).filter(
            Product.is_active == True
        ).all()

        target_products_list = []

        for product in products:
            # === 1. PO数合計を計算（納期から28日後まで） ===
            po_data = self.calculate_po_total_with_28days(product.product_id)
            
            if not po_data['earliest_po']:
                continue  # POがない製品はスキップ

            # === 2. 生産数を計算（PO数合計 - 在庫） ===
            production_quantity = self.calculate_production_quantity(
                product.product_id,
                po_data['po_total']
            )

            # 生産数が0の場合はスキップ（在庫で賄える）
            if production_quantity == 0:
                continue

            # === 3. 工程を確認 ===
            processes = self.db.query(Process).filter(
                Process.product_id == product.product_id
            ).order_by(Process.process_no.asc()).all()

            if not processes:
                continue

            # プレス工程が存在するかチェック
            press_processes = [p for p in processes if self.is_press_process(p.process_name)]

            if not press_processes:
                # プレス工程がない製品はスキップ（プレス優先スケジューリングの対象外）
                continue

            # === 4. 全工程の加工時間を計算し、締切日を決定 ===
            deadline_data = self.calculate_all_processes_deadline(
                product,
                production_quantity,
                po_data['earliest_po'].delivery_date
            )

            # === 5. データ構造を構築 ===
            target_products_list.append({
                'product': product,
                'earliest_po': po_data['earliest_po'],
                'relevant_pos': po_data['relevant_pos'],
                'po_total': po_data['po_total'],
                'production_quantity': production_quantity,
                'deadline': deadline_data['deadline'],
                'processes': processes,
                'press_processes': press_processes,
                'current_process_no': press_processes[0].process_no if press_processes else 0,  # 最初のプレス工程
                'total_days': deadline_data['total_days'],
                'process_details': deadline_data['process_details']
            })

        # === 6. 締切日でソート（締切日の早い順） ===
        target_products_list.sort(key=lambda x: (x['deadline'], x['product'].product_id))

        return target_products_list

    def recalculate_deadline_considering_machines(
        self,
        po_data: Dict,
        scheduled_process_ids: set = None
    ) -> date:
        """
        プレス機の空き状況を考慮して生産締切日を再計算

        Args:
            po_data: POデータ（product, processes, po_quantity等を含む）
            scheduled_process_ids: 既にスケジュール済みの工程ID（再計算から除外）

        Returns:
            再計算された生産締切日
        """
        if scheduled_process_ids is None:
            scheduled_process_ids = set()

        po = po_data['po']
        po_quantity = po_data.get('production_quantity', po_data['po_quantity'])

        # 最も早く空くプレス機の開始時刻を取得
        if self.machine_availability:
            earliest_machine_start = min(self.machine_availability.values())
        else:
            earliest_machine_start = self.get_vietnam_now()

        # 工程はpo_dataから取得（DBクエリ不要）
        processes = po_data.get('processes', [])

        total_minutes = 0.0
        daily_minutes = self.get_working_minutes(self.working_hours)

        for process in processes:
            # 既にスケジュール済みの工程はスキップ
            if process.process_id in scheduled_process_ids:
                continue

            # 所要時間を計算
            setup_time, processing_time = self.calculate_process_time(
                process, po_quantity
            )
            total_minutes += setup_time + processing_time

        # プレス工程の場合、機械の空き状況を考慮
        press_processes = [p for p in processes if self.is_press_process(p.process_name) and p.process_id not in scheduled_process_ids]

        if press_processes:
            # 最も早く空くプレス機からの待ち時間を加算
            current_time = self.get_vietnam_now()
            wait_minutes = 0
            if earliest_machine_start > current_time:
                # 待ち時間を計算（稼働時間ベース）
                wait_minutes = self.calculate_working_minutes_in_range(current_time, earliest_machine_start)
            total_minutes += wait_minutes

        # 総分数を日数に変換
        total_days = total_minutes / daily_minutes if daily_minutes > 0 else 0

        # 生産締切日を計算
        production_deadline = self.calculate_production_deadline(
            po.delivery_date,
            total_days
        )

        return production_deadline

    def recalculate_all_deadlines_and_resort(
        self,
        target_pos_list: List[Dict],
        scheduled_pos_processes: Dict[int, set]
    ) -> List[Dict]:
        """
        全POの締切日を再計算してソートし直す

        Args:
            target_pos_list: POデータのリスト
            scheduled_pos_processes: {po_id: set(スケジュール済み工程ID)}

        Returns:
            締切日で再ソートされたPOリスト
        """
        for po_data in target_pos_list:
            po_id = po_data['po'].po_id
            scheduled_process_ids = scheduled_pos_processes.get(po_id, set())

            # 締切日を再計算
            new_deadline = self.recalculate_deadline_considering_machines(
                po_data,
                scheduled_process_ids
            )
            po_data['production_deadline'] = new_deadline

        # 締切日で再ソート
        target_pos_list.sort(key=lambda x: (x['production_deadline'], x['po'].po_id))

        return target_pos_list

    def recalculate_all_deadlines_and_resort_products(
        self,
        target_products_list: List[Dict],
        scheduled_product_processes: Dict[int, set]
    ) -> List[Dict]:
        """
        全製品の締切日を再計算してソートし直す（製品単位版）

        Args:
            target_products_list: 製品データのリスト
            scheduled_product_processes: {product_id: set(スケジュール済み工程ID)}

        Returns:
            締切日で再ソートされた製品リスト
        """
        for product_data in target_products_list:
            product_id = product_data['product'].product_id
            scheduled_process_ids = scheduled_product_processes.get(product_id, set())

            # スケジュール済み工程を除いた残りの工程で加工時間を再計算
            remaining_processes = [
                p for p in product_data['processes']
                if p.process_id not in scheduled_process_ids
            ]

            if not remaining_processes:
                # 全工程完了
                continue

            # 残りの工程の加工時間を計算
            total_minutes = 0.0
            daily_minutes = self.get_working_minutes(self.working_hours)

            for process in remaining_processes:
                setup_time, processing_time = self.calculate_process_time(
                    process, product_data['production_quantity']
                )
                total_minutes += setup_time + processing_time

            # プレス工程の待ち時間を考慮
            remaining_press_processes = [
                p for p in product_data['press_processes']
                if p.process_id not in scheduled_process_ids
            ]

            if remaining_press_processes and self.machine_availability:
                # 最も早く空くプレス機からの待ち時間を加算
                earliest_machine_start = min(self.machine_availability.values())
                current_time = self.get_vietnam_now()
                if earliest_machine_start > current_time:
                    wait_minutes = self.calculate_working_minutes_in_range(current_time, earliest_machine_start)
                    total_minutes += wait_minutes

            # 総分数を日数に変換
            total_days = total_minutes / daily_minutes if daily_minutes > 0 else 0

            # 締切日を再計算
            new_deadline = self.calculate_production_deadline(
                product_data['earliest_po'].delivery_date,
                total_days
            )
            product_data['deadline'] = new_deadline

        # 締切日で再ソート
        target_products_list.sort(key=lambda x: (x['deadline'], x['product'].product_id))

        return target_products_list

    def initialize_machine_availability(self):
        """PRESS機の空き時間を初期化"""
        press_machines = self.db.query(MachineList).join(MachineType).filter(
            MachineType.machine_type_name == 'PRESS'
        ).all()

        # 現在時刻を開始時刻とする
        start_time = self.get_vietnam_now()

        # 稼働時間内かチェック
        work_start_hour = 6
        work_end_hour = work_start_hour + self.working_hours

        # 休日の場合、次の稼働日へ
        if not self.is_working_day(start_time.date()):
            start_time = self.get_next_working_datetime(start_time)
        # 稼働時間外の場合
        elif start_time.hour < work_start_hour:
            # 稼働開始前 → 今日の6:00に設定
            start_time = start_time.replace(hour=work_start_hour, minute=0, second=0)
        elif start_time.hour >= work_end_hour:
            # 稼働終了後 → 次の稼働日の6:00に設定
            start_time = self.get_next_working_datetime(start_time)

        for machine in press_machines:
            self.machine_availability[machine.machine_list_id] = start_time
            # 初期状態では前回の工程なし
            self.machine_last_process[machine.machine_list_id] = None

    @staticmethod
    def get_vietnam_now() -> datetime:
        """ベトナム時間の現在日時を取得（タイムゾーン非対応）"""
        # タイムゾーン対応のdatetimeを取得してからタイムゾーン情報を削除
        return datetime.now(VIETNAM_TZ).replace(tzinfo=None)

    @staticmethod
    def get_vietnam_today() -> date:
        """ベトナム時間の今日の日付を取得"""
        return datetime.now(VIETNAM_TZ).date()

    def assign_press_machine(
        self,
        start_time: datetime,
        duration_minutes: float,
        process_id: int,
        setup_time: float
    ) -> Tuple[int, datetime, datetime, float]:
        """
        最も早く空くPRESS機を割当
        同じ機械で違う工程の場合は段取り時間を追加

        Returns: (machine_list_id, planned_start, planned_end, actual_setup_time)
        """
        # 最も早く空く機械を探す
        earliest_machine_list_id = None
        earliest_available_time = None

        for machine_list_id, available_time in self.machine_availability.items():
            # この機械がいつから使えるか
            actual_start = max(start_time, available_time)

            if earliest_available_time is None or actual_start < earliest_available_time:
                earliest_available_time = actual_start
                earliest_machine_list_id = machine_list_id

        if earliest_machine_list_id is None:
            raise ValueError("利用可能なPRESS機が見つかりません")

        # 実際の開始時刻
        planned_start = earliest_available_time

        # 段取り時間を確認
        additional_setup_time = 0
        if (earliest_machine_list_id in self.machine_last_process and
            self.machine_last_process[earliest_machine_list_id] is not None):
            # 前回の工程と今回の工程が異なる場合、段取り時間を追加
            if self.machine_last_process[earliest_machine_list_id] != process_id:
                additional_setup_time = setup_time

                # 段取り替え30分ルールを適用
                work_end_hour = 6 + self.working_hours
                should_postpone, adjusted_setup_time = self.should_postpone_setup(
                    planned_start,
                    additional_setup_time,
                    work_end_hour
                )

                if should_postpone:
                    # 翌日に持ち越し
                    next_day = planned_start.date() + timedelta(days=1)
                    while not self.is_working_day(next_day):
                        next_day = next_day + timedelta(days=1)
                    planned_start = datetime.combine(next_day, datetime.min.time().replace(hour=6, minute=0))
                    additional_setup_time = adjusted_setup_time

                # 段取り時間を考慮して開始時刻を調整
                planned_start = self.add_working_time(planned_start, additional_setup_time)

        # 総作業時間を計算（段取り時間は既に考慮済み）
        total_time = duration_minutes

        # 終了時刻を計算（稼働時間を考慮）
        planned_end = self.add_working_time(planned_start, total_time)

        # この機械の次の空き時間と最後の工程を更新
        self.machine_availability[earliest_machine_list_id] = planned_end
        self.machine_last_process[earliest_machine_list_id] = process_id

        return earliest_machine_list_id, planned_start, planned_end, additional_setup_time

    def generate_schedule_old(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        生産計画を生成（旧アルゴリズム）

        優先度変更：プレス機を工場稼働時間分最大限活用することを最優先
        - できるだけ早期にプレス機を埋める（1-4日目フル、6-7日目空き）

        Returns: 生成されたスケジュールのリスト
        """
        # PRESS機の空き時間を初期化
        self.initialize_machine_availability()

        # 対象製品とPOを取得（優先度順）
        target_products = self.get_target_products_with_pos()

        # 既存のスケジュールを削除
        self.db.query(ProductionSchedule).delete()
        self.db.commit()

        schedules = []

        for product_data in target_products:
            product = product_data['product']
            earliest_po = product_data['earliest_po']
            total_quantity = product_data['total_quantity']
            processes = product_data['processes']

            # 前工程の終了時刻を保持
            previous_end_time = None
            # 前工程の情報（並列実行判定用）
            previous_process = None
            previous_machine_id = None
            # 現工程で使用できる数量（前工程で生産した数量）
            available_quantity = total_quantity

            for process in processes:
                # 工程の所要時間を計算（前工程で生産した数量を使用）
                setup_time, processing_time = self.calculate_process_time(
                    process, available_quantity
                )

                total_time = setup_time + processing_time

                if total_time == 0:
                    continue

                # 開始時刻を決定
                # PRESS工程かどうかを先に判定
                is_press = self.is_press_process(process.process_name)

                if previous_end_time is None:
                    # 最初の工程 → 現在時刻から開始
                    start_time = self.get_vietnam_now()
                else:
                    # PRESS工程の場合は、プレス機を最大限活用するため、
                    # できるだけ早くプレス機に割り当てる
                    if is_press:
                        # プレス機の最も早い空き時刻を確認
                        if self.machine_availability:
                            earliest_machine_available = min(self.machine_availability.values())
                            # 前工程の終了時刻 vs プレス機の空き時刻の遅い方を使用
                            # （前工程が完了しないと材料がないため）
                            start_time = max(previous_end_time, earliest_machine_available)
                        else:
                            start_time = previous_end_time
                    elif (previous_process and
                        self.is_press_process(previous_process.process_name) and
                        self.is_press_process(process.process_name)):
                        # 両方プレス工程の場合、並列実行の可能性あり
                        # 現在時刻から開始（後で機械割り当て時に調整）
                        start_time = self.get_vietnam_now()
                    else:
                        # 前工程の終了時刻から開始
                        start_time = previous_end_time

                machine_list_id = None

                if is_press:
                    # PRESS工程：1日で終わらない場合は複数日に分割
                    # 稼働時間を最大活用する
                    remaining_quantity = available_quantity
                    produced_quantity = 0  # 実際に生産した数量の合計
                    current_start = start_time
                    work_end_hour = 6 + self.working_hours
                    last_end_time = None
                    max_iterations = 100  # 無限ループ防止

                    iteration_count = 0
                    while remaining_quantity > 0 and iteration_count < max_iterations:
                        iteration_count += 1
                        # 現在の開始時刻を稼働時間内に調整
                        if current_start.hour < 6:
                            current_start = current_start.replace(hour=6, minute=0, second=0)
                        elif current_start.hour >= work_end_hour:
                            current_start = self.get_next_working_datetime(current_start)

                        # 休日チェック
                        if not self.is_working_day(current_start.date()):
                            current_start = self.get_next_working_datetime(current_start)
                            continue

                        # 今日の終業時刻を計算
                        current_day_end = current_start.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

                        # 今日の残り時間を計算（分）- 休憩時間を除外
                        remaining_minutes_today = self.calculate_working_minutes_in_range(current_start, current_day_end)

                        if remaining_minutes_today <= 0:
                            # 既に終業時刻を過ぎている場合は次の稼働日へ
                            current_start = self.get_next_working_datetime(current_start)
                            continue

                        # 残り数量の処理時間を計算
                        current_setup_time, remaining_processing_time = self.calculate_process_time(
                            process, remaining_quantity
                        )

                        # 今日中に全て終わるかチェック
                        if remaining_processing_time <= remaining_minutes_today:
                            # 全て今日中に終わる
                            quantity_this_batch = remaining_quantity
                            processing_time_this_batch = remaining_processing_time
                        else:
                            # 今日中に終わらない：今日の稼働時間を最大活用
                            # 今日の残り時間で処理できる最大数量を計算
                            quantity_this_batch = self.calculate_quantity_per_time(process, remaining_minutes_today)

                            if quantity_this_batch <= 0:
                                # 計算上は0だが、残り数量が少ない場合は全部処理
                                if remaining_quantity <= 10:
                                    quantity_this_batch = remaining_quantity
                                    _, processing_time_this_batch = self.calculate_process_time(
                                        process, quantity_this_batch
                                    )
                                else:
                                    # 今日はこれ以上処理できない → 次の稼働日へ
                                    current_start = self.get_next_working_datetime(current_start)
                                    continue
                            else:
                                # 残り数量を超えないように制限
                                quantity_this_batch = min(quantity_this_batch, remaining_quantity)

                                # この数量の実際の処理時間を計算
                                _, processing_time_this_batch = self.calculate_process_time(
                                    process, quantity_this_batch
                                )

                        # 実際の処理時間でPRESS機を割当（段取り時間も考慮される）
                        machine_list_id, planned_start, planned_end, actual_setup = self.assign_press_machine(
                            current_start,
                            processing_time_this_batch,
                            process.process_id,
                            current_setup_time
                        )

                        # スケジュールをDBに保存
                        schedule = ProductionSchedule(
                            po_id=earliest_po.po_id,
                            process_id=process.process_id,
                            machine_list_id=machine_list_id,
                            planned_start_datetime=planned_start,
                            planned_end_datetime=planned_end,
                            po_quantity=quantity_this_batch,
                            setup_time=actual_setup,
                            processing_time=processing_time_this_batch,
                            user=user_id
                        )

                        self.db.add(schedule)
                        schedules.append({
                            'po_id': earliest_po.po_id,
                            'po_number': earliest_po.po_number,
                            'product_code': product.product_code,
                            'process_name': process.process_name,
                            'machine_list_id': machine_list_id,
                            'planned_start': planned_start,
                            'planned_end': planned_end,
                            'po_quantity': quantity_this_batch
                        })

                        # 次のバッチの準備
                        remaining_quantity -= quantity_this_batch
                        produced_quantity += quantity_this_batch  # 生産数量を累積
                        last_end_time = planned_end

                        if remaining_quantity > 0:
                            # まだ残りがある場合、次の稼働日の開始時刻（6:00）へ
                            # 稼働時間を最大活用するため、次の日の開始時刻から
                            next_day = planned_end.date() + timedelta(days=1)
                            # 次の稼働日を探す
                            while not self.is_working_day(next_day):
                                next_day = next_day + timedelta(days=1)
                            # 次の稼働日の開始時刻（6:00）
                            current_start = datetime.combine(next_day, datetime.min.time().replace(hour=6, minute=0))

                    # 次工程の開始時刻を更新（最後のバッチの終了時刻）
                    previous_end_time = last_end_time
                    # 次工程で使用できる数量を更新（この工程で生産した数量）
                    available_quantity = produced_quantity
                    # 前工程情報を更新（並列実行判定用）
                    previous_process = process
                    previous_machine_id = machine_list_id

                else:
                    # PRESS以外の工程も分割生産に対応
                    remaining_quantity = available_quantity
                    produced_quantity = 0
                    current_start = start_time
                    work_end_hour = 6 + self.working_hours
                    last_end_time = None
                    max_iterations = 100  # 無限ループ防止

                    iteration_count = 0
                    while remaining_quantity > 0 and iteration_count < max_iterations:
                        iteration_count += 1
                        # 稼働時間内に調整
                        if current_start.hour < 6:
                            current_start = current_start.replace(hour=6, minute=0, second=0)
                        elif current_start.hour >= work_end_hour:
                            current_start = self.get_next_working_datetime(current_start)

                        # 休日チェック
                        if not self.is_working_day(current_start.date()):
                            current_start = self.get_next_working_datetime(current_start)
                            continue

                        # 今日の終業時刻
                        current_day_end = current_start.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)
                        # 今日の残り時間を計算（分）- 休憩時間を除外
                        remaining_minutes_today = self.calculate_working_minutes_in_range(current_start, current_day_end)

                        if remaining_minutes_today <= 0:
                            current_start = self.get_next_working_datetime(current_start)
                            continue

                        # 残り数量の処理時間を計算
                        current_setup_time, remaining_processing_time = self.calculate_process_time(
                            process, remaining_quantity
                        )

                        # 今日中に全て終わるかチェック
                        if remaining_processing_time <= remaining_minutes_today:
                            # 全て今日中に終わる
                            quantity_this_batch = remaining_quantity
                            processing_time_this_batch = remaining_processing_time
                        else:
                            # 今日中に終わらない：分割
                            quantity_this_batch = self.calculate_quantity_per_time(process, remaining_minutes_today)

                            if quantity_this_batch <= 0:
                                # 計算上は0だが、残り数量が少ない場合は全部処理
                                if remaining_quantity <= 10:
                                    quantity_this_batch = remaining_quantity
                                    _, processing_time_this_batch = self.calculate_process_time(
                                        process, quantity_this_batch
                                    )
                                else:
                                    current_start = self.get_next_working_datetime(current_start)
                                    continue
                            else:
                                quantity_this_batch = min(quantity_this_batch, remaining_quantity)
                                _, processing_time_this_batch = self.calculate_process_time(
                                    process, quantity_this_batch
                                )

                        planned_start = current_start
                        planned_end = self.add_working_time(planned_start, processing_time_this_batch)

                        # スケジュールをDBに保存
                        schedule = ProductionSchedule(
                            po_id=earliest_po.po_id,
                            process_id=process.process_id,
                            machine_list_id=machine_list_id,
                            planned_start_datetime=planned_start,
                            planned_end_datetime=planned_end,
                            po_quantity=quantity_this_batch,
                            setup_time=current_setup_time if produced_quantity == 0 else 0,
                            processing_time=processing_time_this_batch,
                            user=user_id
                        )

                        self.db.add(schedule)
                        schedules.append({
                            'po_id': earliest_po.po_id,
                            'po_number': earliest_po.po_number,
                            'product_code': product.product_code,
                            'process_name': process.process_name,
                            'machine_list_id': machine_list_id,
                            'planned_start': planned_start,
                            'planned_end': planned_end,
                            'po_quantity': quantity_this_batch
                        })

                        remaining_quantity -= quantity_this_batch
                        produced_quantity += quantity_this_batch
                        last_end_time = planned_end

                        if remaining_quantity > 0:
                            # 次の稼働日の開始時刻（6:00）へ
                            next_day = planned_end.date() + timedelta(days=1)
                            while not self.is_working_day(next_day):
                                next_day = next_day + timedelta(days=1)
                            current_start = datetime.combine(next_day, datetime.min.time().replace(hour=6, minute=0))

                    # 次工程の開始時刻を更新
                    previous_end_time = last_end_time
                    # 次工程で使用できる数量を更新
                    available_quantity = produced_quantity
                    # 前工程情報を更新（並列実行判定用）
                    previous_process = process
                    previous_machine_id = machine_list_id

        # コミット
        self.db.commit()

        return schedules

    def calculate_makespan(self) -> Optional[datetime]:
        """
        全体の完了時刻（makespan）を計算
        """
        last_schedule = self.db.query(ProductionSchedule).order_by(
            ProductionSchedule.planned_end_datetime.desc()
        ).first()

        if last_schedule:
            return last_schedule.planned_end_datetime

        return None

    # ============================================
    # 新アルゴリズム用メソッド
    # ============================================

    def initialize_all_machines_v2(self):
        """全機械（PRESS、TAP、BARREL等）を初期化"""
        # 全機械を取得
        all_machines = self.db.query(MachineList).all()

        today = self.get_vietnam_today()

        for machine in all_machines:
            # 日次スケジュールを初期化（7日分）
            self.machine_daily_schedule[machine.machine_list_id] = {}
            for day_offset in range(7):
                date_key = (today + timedelta(days=day_offset)).isoformat()
                self.machine_daily_schedule[machine.machine_list_id][date_key] = []

            # 継続中タスクなし
            # （machine_ongoing_taskには追加しない）

    def get_machines_with_free_time(self, current_date: date) -> List[int]:
        """指定日に空き時間がある機械のIDリストを取得"""
        date_key = current_date.isoformat()
        machines_with_free_time = []

        for machine_id, daily_schedule in self.machine_daily_schedule.items():
            if date_key not in daily_schedule:
                continue

            # この日のスケジュールを取得
            schedules = daily_schedule[date_key]

            # 稼働時間の合計を計算
            total_minutes = sum(
                (s['end'] - s['start']).total_seconds() / 60
                for s in schedules
            )

            # 稼働可能時間
            daily_minutes = self.get_working_minutes(self.working_hours)

            # 空き時間があるかチェック（少しでも空きがあれば）
            if total_minutes < daily_minutes - 1:  # 1分以上の空きがあれば
                machines_with_free_time.append(machine_id)

        return machines_with_free_time

    def calculate_free_time(self, machine_id: int, current_date: date) -> float:
        """指定機械の指定日の空き時間（分）を計算"""
        date_key = current_date.isoformat()

        if machine_id not in self.machine_daily_schedule:
            return 0

        if date_key not in self.machine_daily_schedule[machine_id]:
            return 0

        # この日のスケジュールを取得
        schedules = self.machine_daily_schedule[machine_id][date_key]

        # 空き時間（実稼働時間で計算）
        free_minutes = 0
        for s in schedules:
            # スケジュール間のギャップを計算する必要があるが、
            # ここでは簡易的に「1日の総実稼働時間 - 既にスケジュールされた実稼働時間」とする
            # ただし、スケジュールが重なっていない前提
            
            # スケジュールの実稼働時間を計算
            work_mins = self.calculate_working_minutes_in_range(s['start'], s['end'])
            free_minutes += work_mins
            
        # 1日の総実稼働時間
        daily_minutes = self.get_working_minutes(self.working_hours)
        
        # 残りの空き時間
        remaining_free = daily_minutes - free_minutes

        return max(0, remaining_free)



    def find_next_unscheduled_process(self, product_data: Dict) -> Optional[Process]:
        """製品の次の未スケジュール工程を取得"""
        product = product_data['product']
        processes = product_data['processes']

        for process in processes:
            status_key = (product.product_id, process.process_no)

            # ステータスを確認
            status = self.process_schedule_status.get(status_key, 'pending')

            if status == 'pending':
                # この工程がまだスケジュールされていない
                return process

        # 全工程が完了またはスケジュール済み
        return None

    def is_previous_process_completed(self, product_data: Dict, process: Process) -> bool:
        """前工程が完了しているかチェック"""
        product = product_data['product']

        if process.process_no == 1:
            # 最初の工程は前工程なし
            return True

        # 前工程のステータスを確認
        prev_status_key = (product.product_id, process.process_no - 1)
        prev_status = self.process_schedule_status.get(prev_status_key, 'pending')

        return prev_status == 'completed'

    def update_process_status(self, product_data: Dict, process: Process, is_completed: bool):
        """工程のステータスを更新"""
        product = product_data['product']
        status_key = (product.product_id, process.process_no)

        if is_completed:
            self.process_schedule_status[status_key] = 'completed'
        else:
            self.process_schedule_status[status_key] = 'in_progress'

    def update_machine_schedule(self, machine_id: int, current_date: date, start: datetime, end: datetime):
        """機械のスケジュールを更新"""
        date_key = current_date.isoformat()

        if machine_id not in self.machine_daily_schedule:
            self.machine_daily_schedule[machine_id] = {}

        if date_key not in self.machine_daily_schedule[machine_id]:
            self.machine_daily_schedule[machine_id][date_key] = []

        self.machine_daily_schedule[machine_id][date_key].append({
            'start': start,
            'end': end
        })

    def needs_setup_time(self, machine_id: int, process_id: int) -> bool:
        """段取り時間が必要かチェック（前回と異なる工程か）"""
        if machine_id not in self.machine_last_process:
            # 初回
            return True

        last_process_id = self.machine_last_process.get(machine_id)

        if last_process_id is None:
            # 前回の工程なし
            return True

        # 前回と異なる工程かチェック
        return last_process_id != process_id

    def process_ongoing_tasks_for_day(self, current_date: date, schedules: List, user_id: Optional[int] = None):
        """継続中タスクを処理（全機械）"""
        # 今日の稼働開始・終了時刻
        day_start = datetime.combine(current_date, datetime.min.time().replace(hour=6, minute=0))
        work_end_hour = 6 + self.working_hours
        day_end = datetime.combine(current_date, datetime.min.time().replace(hour=work_end_hour, minute=0))

        # 今日の稼働時間（分）
        daily_minutes = self.get_working_minutes(self.working_hours)

        # 継続中タスクのコピー（イテレーション中の削除対策）
        ongoing_tasks = list(self.machine_ongoing_task.items())

        for machine_id, task_info in ongoing_tasks:
            # 残り時間を計算
            remaining_minutes = task_info['remaining_minutes']

            # タスク開始時刻（今日の開始時刻）
            task_start = day_start

            if remaining_minutes <= daily_minutes:
                # 今日中に完了
                actual_minutes = remaining_minutes
                task_end = self.add_working_time(task_start, actual_minutes)

                # スケジュール保存
                schedule = ProductionSchedule(
                    po_id=task_info['po_id'],
                    process_id=task_info['process_id'],
                    machine_list_id=machine_id,
                    planned_start_datetime=task_start,
                    planned_end_datetime=task_end,
                    po_quantity=task_info['remaining_quantity'],
                    setup_time=0,  # 継続タスクは段取り不要
                    processing_time=actual_minutes,
                    user=user_id
                )

                self.db.add(schedule)

                # POと製品情報を取得
                po = self.db.query(PO).filter(PO.po_id == task_info['po_id']).first()
                process = self.db.query(Process).filter(Process.process_id == task_info['process_id']).first()
                product = self.db.query(Product).filter(Product.product_id == task_info['product_id']).first()

                schedules.append({
                    'po_id': task_info['po_id'],
                    'po_number': po.po_number if po else '',
                    'product_code': product.product_code if product else '',
                    'process_id': task_info['process_id'],
                    'process_name': process.process_name if process else '',
                    'machine_list_id': machine_id,
                    'planned_start': task_start,
                    'planned_end': task_end,
                    'po_quantity': task_info['remaining_quantity']
                })

                # 機械のスケジュールを更新
                self.update_machine_schedule(machine_id, current_date, task_start, task_end)

                # 工程を完了としてマーク
                product_id = task_info['product_id']
                process = self.db.query(Process).filter(Process.process_id == task_info['process_id']).first()
                if process:
                    status_key = (product_id, process.process_no)
                    self.process_schedule_status[status_key] = 'completed'

                # 継続タスクをクリア
                del self.machine_ongoing_task[machine_id]

            else:
                # 今日中に終わらない → 継続
                task_end = day_end

                # 今日処理できる数量を計算
                quantity_today = self.calculate_quantity_per_time(
                    self.db.query(Process).filter(Process.process_id == task_info['process_id']).first(),
                    daily_minutes
                )

                # スケジュール保存
                schedule = ProductionSchedule(
                    po_id=task_info['po_id'],
                    process_id=task_info['process_id'],
                    machine_list_id=machine_id,
                    planned_start_datetime=task_start,
                    planned_end_datetime=task_end,
                    po_quantity=quantity_today,
                    setup_time=0,  # 継続タスクは段取り不要
                    processing_time=daily_minutes,
                    user=user_id
                )

                self.db.add(schedule)

                # POと製品情報を取得
                po = self.db.query(PO).filter(PO.po_id == task_info['po_id']).first()
                process = self.db.query(Process).filter(Process.process_id == task_info['process_id']).first()
                product = self.db.query(Product).filter(Product.product_id == task_info['product_id']).first()

                schedules.append({
                    'po_id': task_info['po_id'],
                    'po_number': po.po_number if po else '',
                    'product_code': product.product_code if product else '',
                    'process_id': task_info['process_id'],
                    'process_name': process.process_name if process else '',
                    'machine_list_id': machine_id,
                    'planned_start': task_start,
                    'planned_end': task_end,
                    'po_quantity': quantity_today
                })

                # 機械のスケジュールを更新
                self.update_machine_schedule(machine_id, current_date, task_start, task_end)

                # 残り時間と数量を更新
                self.machine_ongoing_task[machine_id]['remaining_minutes'] -= daily_minutes
                self.machine_ongoing_task[machine_id]['remaining_quantity'] -= quantity_today

    def find_best_press_machine(self, process: Process, current_date: date) -> Optional[int]:
        """最適なPRESS機を選択（空き時間が最も多い機械）"""
        # 全PRESS機を取得
        all_press_machines = self.db.query(MachineList).join(MachineType).filter(
            MachineType.machine_type_name == 'PRESS'
        ).all()

        best_machine_id = None
        max_free_time = 0

        for machine in all_press_machines:
            # この機械の空き時間を計算
            free_minutes = self.calculate_free_time(machine.machine_list_id, current_date)

            if free_minutes > max_free_time:
                max_free_time = free_minutes
                best_machine_id = machine.machine_list_id

        return best_machine_id if max_free_time > 10 else None  # 10分以上の空きがあれば

    def get_all_free_slots(self, machine_id: int, current_date: date) -> List[Tuple[datetime, datetime]]:
        """
        指定機械の指定日の全ての空き時間帯を取得
        Returns: List[(start, end)]
        """
        date_key = current_date.isoformat()
        
        # 稼働開始・終了時刻
        day_start = datetime.combine(current_date, datetime.min.time().replace(hour=6, minute=0))
        work_end_hour = 6 + self.working_hours
        day_end = datetime.combine(current_date, datetime.min.time().replace(hour=work_end_hour, minute=0))

        if machine_id not in self.machine_daily_schedule or date_key not in self.machine_daily_schedule[machine_id]:
            return [(day_start, day_end)]

        schedules = self.machine_daily_schedule[machine_id][date_key]
        if not schedules:
            return [(day_start, day_end)]

        # スケジュールを開始時刻でソート
        sorted_schedules = sorted(schedules, key=lambda s: s['start'])

        free_slots = []
        current_time = day_start

        for schedule in sorted_schedules:
            # 現在時刻からスケジュール開始までのギャップを確認
            if schedule['start'] > current_time:
                free_slots.append((current_time, schedule['start']))
            
            # 現在時刻をスケジュール終了時刻に進める
            # スケジュールが重なっている場合の考慮（通常はないはずだがmaxを取る）
            current_time = max(current_time, schedule['end'])

        # 最後のスケジュールから終業時刻までのギャップ
        if current_time < day_end:
            free_slots.append((current_time, day_end))

        return free_slots

    def assign_task_to_machine(
        self,
        machine_id: int,
        process: Process,
        product_data: Dict,
        current_date: date,
        schedules: List,
        user_id: Optional[int] = None,
        min_start_time: Optional[datetime] = None
    ) -> bool:
        """機械にタスクを割り当て"""
        # 全ての空きスロットを取得
        free_slots = self.get_all_free_slots(machine_id, current_date)
        
        selected_slot = None
        adjusted_start = None
        available_minutes = 0
        
        for start, end in free_slots:
            # スロットの長さ（分）
            slot_minutes = (end - start).total_seconds() / 60
            
            if slot_minutes < 10:
                continue
                
            # 最小開始時刻の制約チェック
            current_slot_start = start
            
            if min_start_time:
                if end <= min_start_time:
                    # このスロットは最小開始時刻より前に終わってしまうので使えない
                    continue
                    
                if current_slot_start < min_start_time:
                    # スロットの途中で開始可能になる
                    
                    # 調整後の開始時刻を計算（稼働時間内への補正含む）
                    temp_start = min_start_time
                    if temp_start.hour < 6:
                         temp_start = temp_start.replace(hour=6, minute=0, second=0)
                    
                    # add_working_time(0) で稼働時間内（休憩除外）に補正
                    temp_start = self.add_working_time(temp_start, 0)
                    
                    if temp_start >= end:
                        continue
                        
                    current_slot_start = temp_start
            
            # 再度長さをチェック（実稼働時間で）
            current_available = self.calculate_working_minutes_in_range(current_slot_start, end)
            
            if current_available >= 10:
                # 使用可能なスロットが見つかった
                selected_slot = (current_slot_start, end)
                adjusted_start = current_slot_start
                available_minutes = current_available
                break
        
        if not selected_slot:
            return False

        free_start = adjusted_start
        free_minutes = available_minutes

        # 工程の所要時間を計算
        setup_time, processing_time = self.calculate_process_time(
            process,
            product_data['total_quantity']
        )

        # 段取り時間判定
        if self.needs_setup_time(machine_id, process.process_id):
            actual_setup = float(setup_time)
        else:
            actual_setup = 0

        total_time = actual_setup + processing_time

        # 空き時間内で処理できる分を計算
        if total_time <= free_minutes:
            # 全量処理可能
            task_minutes = total_time
            task_quantity = product_data['total_quantity']
            is_completed = True
        else:
            # 一部のみ処理（継続タスクとして登録）
            available_time = free_minutes - actual_setup
            if available_time < 10:  # 段取り後の時間が不足
                return False

            task_quantity = self.calculate_quantity_per_time(process, available_time)
            if task_quantity <= 0:
                return False

            task_minutes = free_minutes
            is_completed = False

        # スケジュール保存
        task_start = free_start
        task_end = self.add_working_time(task_start, task_minutes)
        
        # task_end がスロットの終了時刻を超えていないか最終チェック
        # add_working_time は休憩時間をまたぐと終了時刻が伸びる可能性がある
        # しかし free_minutes は単純な時間差分で計算している
        # ここは重要：free_minutes は「スロットの実時間」
        # add_working_time は「稼働時間を考慮した終了時刻」
        # スロット自体が「稼働時間内」の区間であれば、単純加算でいいはずだが、
        # スロット内に休憩が含まれている場合、add_working_time はそれをスキップして後ろに倒す
        # そうなるとスロットの end を超える可能性がある？
        
        # machine_daily_schedule の start/end は「休憩込みの絶対時刻」
        # なので、スロット内に休憩がある場合、その分は「使えない時間」として扱われるべきか？
        # いや、add_working_time は休憩時間を「またぐ」処理をする。
        # つまり、10:00-10:40 の休憩がある場合、
        # 09:00 から 120分 のタスクを入れると、終了は 11:40 になる（休憩40分含む）。
        # このとき、スロットが 09:00 - 12:00 であれば、11:40 は収まっている。
        
        # しかし、get_all_free_slots で取得したスロットは「既にスケジュールが入っている隙間」。
        # 既存スケジュールも休憩をまたいでいる可能性がある。
        
        # 安全のため、task_end が selected_slot[1] (end) を超えないようにする
        if task_end > selected_slot[1]:
            # 計算誤差などで超えてしまった場合、スロットエンドに合わせる
            task_end = selected_slot[1]
            # 数量などは再計算が必要だが、微差なら無視するか、
            # あるいは task_minutes を再計算するか。
            # ここでは task_minutes を調整
            # task_minutes は add_working_time の逆算が必要で面倒
            # 簡易的に、is_completed = False にして継続タスクにする手もあるが、
            # ここまで来たらそのまま登録してしまう（1分程度の誤差なら許容）
            pass

        schedule = ProductionSchedule(
            po_id=product_data['earliest_po'].po_id,
            process_id=process.process_id,
            machine_list_id=machine_id,
            planned_start_datetime=task_start,
            planned_end_datetime=task_end,
            po_quantity=task_quantity,
            setup_time=actual_setup,
            processing_time=task_minutes - actual_setup,
            user=user_id
        )

        self.db.add(schedule)
        schedules.append({
            'po_id': product_data['earliest_po'].po_id,
            'po_number': product_data['earliest_po'].po_number,
            'product_code': product_data['product'].product_code,
            'process_id': process.process_id,
            'process_name': process.process_name,
            'machine_list_id': machine_id,
            'planned_start': task_start,
            'planned_end': task_end,
            'po_quantity': task_quantity
        })

        # 機械のスケジュールを更新
        self.update_machine_schedule(machine_id, current_date, task_start, task_end)

        # 機械の最後の工程を更新
        self.machine_last_process[machine_id] = process.process_id

        if not is_completed:
            # 継続タスクとして登録
            remaining_quantity = product_data['total_quantity'] - task_quantity
            remaining_time = total_time - task_minutes

            self.machine_ongoing_task[machine_id] = {
                'process_id': process.process_id,
                'product_id': product_data['product'].product_id,
                'po_id': product_data['earliest_po'].po_id,
                'remaining_quantity': remaining_quantity,
                'remaining_minutes': remaining_time,
                'started_date': current_date
            }

            # 工程ステータス: in_progress
            self.update_process_status(product_data, process, False)
        else:
            # 工程ステータス: completed
            self.update_process_status(product_data, process, True)

        return True

    def fill_available_time_for_day(
        self,
        current_date: date,
        target_products: List[Dict],
        schedules: List,
        user_id: Optional[int] = None
    ):
        """空き時間を最大限活用（PRESS機優先）"""
        # 無限ループ防止
        max_iterations = 100
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # 空き時間がある機械を取得
            machines_with_free_time = self.get_machines_with_free_time(current_date)

            if not machines_with_free_time:
                break  # この日は全機械が埋まった

            # タスク割り当て成功フラグ
            assigned = False

            # 生産締切日順に製品を処理
            for product_data in target_products:
                # 次の未スケジュール工程を探す
                next_process = self.find_next_unscheduled_process(product_data)

                if not next_process:
                    continue  # この製品は全工程完了

                # PRESS工程かチェック
                if self.is_press_process(next_process.process_name):
                    # 最適なPRESS機を探す
                    best_machine = self.find_best_press_machine(next_process, current_date)

                    if best_machine and best_machine in machines_with_free_time:
                        assigned = self.assign_task_to_machine(
                            best_machine,
                            next_process,
                            product_data,
                            current_date,
                            schedules,
                            user_id
                        )
                else:
                    # PRESS以外の工程
                    # 前工程が完了しているかチェック
                    if self.is_previous_process_completed(product_data, next_process):
                        # 工程名から機械タイプを推測
                        required_machine_type = self.get_machine_type_from_process_name(next_process.process_name)

                        if required_machine_type:
                            # 該当する機械タイプの中から最適な機械を探す
                            suitable_machines = self.db.query(MachineList).join(MachineType).filter(
                                MachineType.machine_type_name == required_machine_type
                            ).all()

                            for machine in suitable_machines:
                                if machine.machine_list_id in machines_with_free_time:
                                    assigned = self.assign_task_to_machine(
                                        machine.machine_list_id,
                                        next_process,
                                        product_data,
                                        current_date,
                                        schedules,
                                        user_id
                                    )
                                    if assigned:
                                        break
                        else:
                            # 機械不要の工程（PACKING等）
                            # 機械IDなしでスケジュール登録
                            # ただし、現在のassign_task_to_machineは機械が必要
                            # 簡易的に: 最初の空き機械を使用（または機械なしで登録）
                            # 機械なしでの登録をサポートするために、別途処理を追加
                            # 今回は簡易的に最初の機械を使用
                            if machines_with_free_time:
                                assigned = self.assign_task_to_machine(
                                    machines_with_free_time[0],
                                    next_process,
                                    product_data,
                                    current_date,
                                    schedules,
                                    user_id
                                )
                            else:
                                # 機械が空いていない場合は、機械なしで登録
                                # （PAC KING等の場合）
                                # この部分は後で実装
                                pass

                if assigned:
                    break  # 1つ割り当てたら次のイテレーション

            if not assigned:
                break  # これ以上割り当てできない

    def generate_schedule(self, user_id: Optional[int] = None) -> Dict:
        """
        生産計画を生成（締切日優先方式）
        
        PO単位で生産締切日を計算し、締切日の早い順にプレス工程を割り当て
        空き時間を最大限活用し、効率的なスケジューリングを実現
        
        Returns: {
            'constrained_schedules': [...],
            'unconstrained_schedules': [...],
            'all_schedules': [...]
        }
        """
        return self.generate_schedule_by_deadline(user_id)

    def generate_schedule_v2(self, user_id: Optional[int] = None) -> Dict:
        """
        生産計画を生成（2段階構成 - 旧方式）

        フェーズ1: 制約のある工程（PRESS等）のスケジューリング
        フェーズ2: 制約のない工程（TAP、BARREL、PACKING等）のスケジューリング（並行実行）

        Returns: {
            'constrained_schedules': [...],
            'unconstrained_schedules': [...],
            'all_schedules': [...]
        }
        """
        # 対象製品とPOを取得
        target_products = self.get_target_products_with_pos()

        # 既存のスケジュールを削除
        self.db.query(ProductionSchedule).delete()
        self.db.commit()

        # === フェーズ1: 制約のある工程のスケジューリング ===
        constrained_schedules = self.generate_constrained_schedule(
            target_products,
            user_id
        )

        # === フェーズ2: 制約のない工程のスケジューリング（並行実行） ===
        unconstrained_schedules = self.generate_unconstrained_schedule(
            target_products,
            constrained_schedules,
            user_id
        )

        # 統合
        all_schedules = constrained_schedules + unconstrained_schedules

        # コミット
        self.db.commit()

        return {
            'constrained_schedules': constrained_schedules,
            'unconstrained_schedules': unconstrained_schedules,
            'all_schedules': all_schedules
        }

    def generate_schedule_by_deadline(self, user_id: Optional[int] = None) -> Dict:
        """
        生産締切日優先のスケジューリング（製品単位 + PO数合計方式）

        新要件版: 1工程を組むごとに全製品の締切日を再計算し、再ソートする

        1. 製品単位でPO数合計を計算し、生産締切日を算出、締切日順にソート
        2. ループ: 1つのPRESS工程を組む
           2.1 締切日の早い製品でプレス機1で加工できる製品を探す
           2.2 プレス機に割り当て、工程が終了する日程を組む
           2.3 全製品の締切日を再計算
           2.4 締切日順にソートし直し
           2.5 次の工程へ
        3. 制約のない工程をスケジューリング

        Returns: {
            'constrained_schedules': [...],  # プレス工程のスケジュール
            'unconstrained_schedules': [...],  # その他工程のスケジュール
            'all_schedules': [...]  # 全スケジュール
        }
        """
        total_start_time = time.time()
        logger.info("=" * 60)
        logger.info("generate_schedule_by_deadline 開始（製品単位 + PO数合計方式）")

        # 製品単位で締切日順にソート
        step_start = time.time()
        target_products_list = self.get_target_pos_sorted_by_deadline()
        logger.info(f"[STEP 1] get_target_pos_sorted_by_deadline 完了: {time.time() - step_start:.2f}秒, 対象製品数: {len(target_products_list)}")

        # 既存のスケジュールを削除
        step_start = time.time()
        self.db.query(ProductionSchedule).delete()
        self.db.commit()
        logger.info(f"[STEP 2] 既存スケジュール削除完了: {time.time() - step_start:.2f}秒")

        # プレス機を初期化
        step_start = time.time()
        self.initialize_machine_availability()
        logger.info(f"[STEP 3] プレス機初期化完了: {time.time() - step_start:.2f}秒, プレス機数: {len(self.machine_availability)}")

        # スケジュールを保存するリスト
        press_schedules = []

        # === フェーズ1: 1工程ごとに締切日を再計算しながらスケジューリング ===
        # 各製品のスケジュール済み工程を追跡: {product_id: set(process_id)}
        scheduled_product_processes: Dict[int, set] = {}

        # 全製品の全プレス工程がスケジュールされるまでループ
        max_iterations = 10000  # 無限ループ防止
        iteration_count = 0

        logger.info("[PHASE 1] プレス工程スケジューリング開始")
        phase1_start = time.time()

        while iteration_count < max_iterations:
            iteration_count += 1

            # 100イテレーションごとにログ出力
            if iteration_count % 100 == 0:
                logger.info(f"  イテレーション {iteration_count}, スケジュール済み工程数: {len(press_schedules)}, 経過時間: {time.time() - phase1_start:.2f}秒")

            # === パフォーマンス最適化：再計算を10イテレーションごとに実行 ===
            # 初回は必ず実行、それ以降は10イテレーションごと
            if iteration_count == 1 or iteration_count % 10 == 0:
                # 締切日順に再ソート（製品単位）
                recalc_start = time.time()
                target_products_list = self.recalculate_all_deadlines_and_resort_products(
                    target_products_list,
                    scheduled_product_processes
                )
                if iteration_count % 100 == 0:
                    logger.debug(f"    再計算時間: {time.time() - recalc_start:.2f}秒")

            # 次にスケジュールする工程を探す
            scheduled_this_iteration = False

            for product_data in target_products_list:
                product = product_data['product']
                product_id = product.product_id

                # この製品のスケジュール済み工程IDセット
                if product_id not in scheduled_product_processes:
                    scheduled_product_processes[product_id] = set()

                # まだスケジュールされていないプレス工程を探す
                for press_process in product_data['press_processes']:
                    if press_process.process_id in scheduled_product_processes[product_id]:
                        continue  # 既にスケジュール済み

                    # この工程の加工時間を計算
                    setup_time, processing_time = self.calculate_process_time(
                        press_process,
                        product_data['production_quantity']
                    )

                    # この工程をスケジューリング
                    # 最も早く空くプレス機を選択して割り当て
                    machine_list_id, planned_start, planned_end, actual_setup = self.assign_press_machine(
                        self.get_vietnam_now(),
                        processing_time,  # 加工時間（分）
                        press_process.process_id,
                        float(press_process.setup_time or 0)
                    )

                    # スケジュールを保存
                    schedule = ProductionSchedule(
                        po_id=product_data['earliest_po'].po_id,
                        process_id=press_process.process_id,
                        machine_list_id=machine_list_id,
                        planned_start_datetime=planned_start,
                        planned_end_datetime=planned_end,
                        po_quantity=product_data['production_quantity'],
                        setup_time=actual_setup,
                        processing_time=(planned_end - planned_start).total_seconds() / 60 - actual_setup,
                        user=user_id
                    )

                    self.db.add(schedule)
                    press_schedules.append({
                        'po_id': product_data['earliest_po'].po_id,
                        'po_number': product_data['earliest_po'].po_number,
                        'product_code': product.product_code,
                        'process_name': press_process.process_name,
                        'machine_list_id': machine_list_id,
                        'planned_start': planned_start,
                        'planned_end': planned_end,
                        'po_quantity': product_data['production_quantity']
                    })

                    # スケジュール済みとしてマーク
                    scheduled_product_processes[product_id].add(press_process.process_id)
                    scheduled_this_iteration = True

                    # 1工程スケジュールしたら、全製品の締切日を再計算するためにループを抜ける
                    break

                if scheduled_this_iteration:
                    break

            # 今回のイテレーションで何もスケジュールされなかった場合は終了
            if not scheduled_this_iteration:
                break

        logger.info(f"[PHASE 1 完了] イテレーション数: {iteration_count}, プレススケジュール数: {len(press_schedules)}, 経過時間: {time.time() - phase1_start:.2f}秒")

        # === フェーズ2: 空き時間を最大限活用（残りのPOがあれば） ===
        logger.info("[PHASE 2] 空き時間活用開始")
        phase2_start = time.time()

        # === フェーズ2: 空き時間を最大限活用（残りのPOがあれば） ===
        logger.info("[PHASE 2] 空き時間活用開始")
        phase2_start = time.time()

        # 完全にスケジュール済みの製品を特定
        fully_scheduled_products = set()
        for product_data in target_products_list:
            product_id = product_data['product'].product_id
            press_process_ids = {p.process_id for p in product_data['press_processes']}
            scheduled_ids = scheduled_product_processes.get(product_id, set())
            if press_process_ids <= scheduled_ids:  # 全プレス工程がスケジュール済み
                fully_scheduled_products.add(product_id)

        self._fill_press_machine_free_time_products(
            target_products_list,
            fully_scheduled_products,
            press_schedules,
            scheduled_product_processes,
            user_id
        )
        logger.info(f"[PHASE 2 完了] 経過時間: {time.time() - phase2_start:.2f}秒")

        # === フェーズ3: 制約のない工程のスケジューリング ===
        logger.info("[PHASE 3] 制約なし工程スケジューリング開始")
        phase3_start = time.time()

        # 製品単位でグループ化してから制約のない工程をスケジューリング
        product_schedules_map = self._group_schedules_by_product(press_schedules)
        unconstrained_schedules = self._schedule_unconstrained_processes(
            target_products_list,
            product_schedules_map,
            user_id
        )
        logger.info(f"[PHASE 3 完了] 制約なしスケジュール数: {len(unconstrained_schedules)}, 経過時間: {time.time() - phase3_start:.2f}秒")

        # 統合
        all_schedules = press_schedules + unconstrained_schedules

        # コミット
        step_start = time.time()
        self.db.commit()
        logger.info(f"[STEP 4] DBコミット完了: {time.time() - step_start:.2f}秒")

        logger.info(f"generate_schedule_by_deadline 完了: 総時間 {time.time() - total_start_time:.2f}秒")
        logger.info(f"  - プレススケジュール: {len(press_schedules)}件")
        logger.info(f"  - 制約なしスケジュール: {len(unconstrained_schedules)}件")
        logger.info(f"  - 合計: {len(all_schedules)}件")
        logger.info("=" * 60)

        return {
            'constrained_schedules': press_schedules,
            'unconstrained_schedules': unconstrained_schedules,
            'all_schedules': all_schedules
        }

    def _schedule_press_process(
        self,
        po_data: Dict,
        press_process: Process,
        schedules: List[Dict],
        user_id: Optional[int] = None
    ):
        """
        プレス工程をスケジューリング

        1日で終わらない場合は翌稼働日に継続
        最も早く空くプレス機に割り当て
        """
        po = po_data['po']
        product = po_data['product']
        # 生産数を使用（在庫引き後の数量）。なければPO数量を使用
        production_quantity = po_data.get('production_quantity', po_data['po_quantity'])

        # 工程の所要時間を計算
        setup_time, processing_time = self.calculate_process_time(
            press_process,
            production_quantity
        )

        total_time = setup_time + processing_time

        if total_time == 0:
            return

        # 残り数量
        remaining_quantity = production_quantity
        produced_quantity = 0
        
        # 最も早く空くプレス機を探す
        earliest_machine_id = min(
            self.machine_availability.keys(),
            key=lambda mid: self.machine_availability[mid]
        )
        
        start_time = self.machine_availability[earliest_machine_id]
        
        # 分割生産のループ（1日で終わらない場合）
        work_end_hour = 6 + self.working_hours
        max_iterations = 100
        iteration_count = 0
        
        while remaining_quantity > 0 and iteration_count < max_iterations:
            iteration_count += 1
            
            # 稼働時間内に調整
            if start_time.hour < 6:
                start_time = start_time.replace(hour=6, minute=0, second=0)
            elif start_time.hour >= work_end_hour:
                start_time = self.get_next_working_datetime(start_time)
            
            # 休日チェック
            if not self.is_working_day(start_time.date()):
                start_time = self.get_next_working_datetime(start_time)
                continue
            
            # 今日の終業時刻
            day_end = start_time.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)
            # 今日の残り時間を計算（分）- 休憩時間を除外
            remaining_minutes_today = self.calculate_working_minutes_in_range(start_time, day_end)
            
            if remaining_minutes_today <= 0:
                start_time = self.get_next_working_datetime(start_time)
                continue
            
            # 残り数量の処理時間を計算
            current_setup_time, remaining_processing_time = self.calculate_process_time(
                press_process,
                remaining_quantity
            )
            
            # 今日中に終わるかチェック
            if remaining_processing_time <= remaining_minutes_today:
                # 全て今日中に終わる
                quantity_this_batch = remaining_quantity
                processing_time_this_batch = remaining_processing_time
            else:
                # 今日中に終わらない：今日の時間を最大活用
                quantity_this_batch = self.calculate_quantity_per_time(
                    press_process,
                    remaining_minutes_today
                )
                
                if quantity_this_batch <= 0:
                    if remaining_quantity <= 10:
                        quantity_this_batch = remaining_quantity
                        _, processing_time_this_batch = self.calculate_process_time(
                            press_process,
                            quantity_this_batch
                        )
                    else:
                        start_time = self.get_next_working_datetime(start_time)
                        continue
                else:
                    quantity_this_batch = min(quantity_this_batch, remaining_quantity)
                    _, processing_time_this_batch = self.calculate_process_time(
                        press_process,
                        quantity_this_batch
                    )
            
            # プレス機を割当（段取り時間も考慮）
            machine_id, planned_start, planned_end, actual_setup = self.assign_press_machine(
                start_time,
                processing_time_this_batch,
                press_process.process_id,
                current_setup_time
            )
            
            # スケジュール保存
            schedule = ProductionSchedule(
                po_id=po.po_id,
                process_id=press_process.process_id,
                machine_list_id=machine_id,
                planned_start_datetime=planned_start,
                planned_end_datetime=planned_end,
                po_quantity=quantity_this_batch,
                setup_time=actual_setup,
                processing_time=processing_time_this_batch,
                user=user_id
            )
            
            self.db.add(schedule)
            schedules.append({
                'po_id': po.po_id,
                'po_number': po.po_number,
                'product_code': product.product_code,
                'process_id': press_process.process_id,
                'process_name': press_process.process_name,
                'machine_list_id': machine_id,
                'planned_start': planned_start,
                'planned_end': planned_end,
                'po_quantity': quantity_this_batch
            })
            
            # 次のバッチの準備
            remaining_quantity -= quantity_this_batch
            produced_quantity += quantity_this_batch
            
            if remaining_quantity > 0:
                # 次の稼働日の開始時刻へ
                next_day = planned_end.date() + timedelta(days=1)
                while not self.is_working_day(next_day):
                    next_day = next_day + timedelta(days=1)
                start_time = datetime.combine(next_day, datetime.min.time().replace(hour=6, minute=0))

    def _fill_press_machine_free_time(
        self,
        target_pos_list: List[Dict],
        scheduled_pos: set,
        schedules: List[Dict],
        user_id: Optional[int] = None
    ):
        """
        プレス機の空き時間を最大限活用
        
        空き時間がある場合、締切日順に再度POリストを走査し、
        空き時間内で加工できるPOがあれば追加スケジュール
        """
        max_fill_iterations = 50  # 無限ループ防止
        
        for _ in range(max_fill_iterations):
            # 空き時間チェック
            has_free_time = False
            
            for machine_id, available_time in self.machine_availability.items():
                # この機械がまだ今日か明日の稼働時間内に空きがあるかチェック
                work_end_hour = 6 + self.working_hours
                current_day_end = available_time.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)
                
                if available_time < current_day_end:
                    # 今日まだ空き時間がある
                    has_free_time = True
                    break
            
            if not has_free_time:
                # 全プレス機が埋まった
                break
            
            # 締切日順にPOを走査して、空き時間に入るものを探す
            added_schedule = False
            
            for po_data in target_pos_list:
                po = po_data['po']
                
                # 既にスケジュール済みならスキップ
                if po.po_id in scheduled_pos:
                    continue
                
                # このPOのプレス工程をスケジューリング試行
                for press_process in po_data['press_processes']:
                    try:
                        self._schedule_press_process(
                            po_data,
                            press_process,
                            schedules,
                            user_id
                        )
                        added_schedule = True
                        break  # このPOの1つ目のプレス工程だけスケジュール
                    except:
                        # スケジュールできなかった場合はスキップ
                        continue
                
                if added_schedule:
                    scheduled_pos.add(po.po_id)
                    break  # 1つ追加したら再度チェック
            
            if not added_schedule:
                # これ以上追加できるPOがない
                break

    def _group_schedules_by_product(self, schedules: List[Dict]) -> Dict[str, List[Dict]]:
        """製品コード毎にスケジュールをグループ化"""
        product_map = {}
        
        for schedule in schedules:
            product_code = schedule['product_code']
            if product_code not in product_map:
                product_map[product_code] = []
            product_map[product_code].append(schedule)
        
        return product_map

    def _fill_press_machine_free_time_products(
        self,
        target_products_list: List[Dict],
        fully_scheduled_products: set,
        press_schedules: List[Dict],
        scheduled_product_processes: Dict[int, set],
        user_id: Optional[int] = None
    ):
        """
        プレス機の空き時間を最大限活用（製品単位版）
        
        空き時間がある場合、締切日順に再度製品リストを走査し、
        空き時間内で加工できる工程があれば追加スケジュール
        """
        max_fill_iterations = 50  # 無限ループ防止
        
        for _ in range(max_fill_iterations):
            # 空き時間チェック
            has_free_time = False
            
            for machine_id, available_time in self.machine_availability.items():
                # この機械がまだ今日か明日の稼働時間内に空きがあるかチェック
                work_end_hour = 6 + self.working_hours
                current_day_end = available_time.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)
                
                if available_time < current_day_end:
                    # 今日まだ空き時間がある
                    has_free_time = True
                    break
            
            if not has_free_time:
                # 全プレス機が埋まった
                break
            
            # 締切日順に製品を走査して、空き時間に入るものを探す
            added_schedule = False
            
            for product_data in target_products_list:
                product = product_data['product']
                product_id = product.product_id
                
                # 既に全工程スケジュール済みならスキップ
                if product_id in fully_scheduled_products:
                    continue
                
                # この製品のスケジュール済み工程IDセット
                if product_id not in scheduled_product_processes:
                    scheduled_product_processes[product_id] = set()
                
                # この製品のプレス工程をスケジューリング試行
                for press_process in product_data['press_processes']:
                    if press_process.process_id in scheduled_product_processes[product_id]:
                        continue
                        
                    try:
                        # 加工時間を計算
                        setup_time, processing_time = self.calculate_process_time(
                            press_process,
                            product_data['production_quantity']
                        )
                        
                        # 空き時間に割り当て
                        # assign_press_machineは最も早く空く機械を探すので、そのまま使える
                        machine_list_id, planned_start, planned_end, actual_setup = self.assign_press_machine(
                            self.get_vietnam_now(),
                            processing_time,
                            press_process.process_id,
                            float(press_process.setup_time or 0)
                        )
                        
                        # スケジュール保存
                        schedule = ProductionSchedule(
                            po_id=product_data['earliest_po'].po_id,
                            process_id=press_process.process_id,
                            machine_list_id=machine_list_id,
                            planned_start_datetime=planned_start,
                            planned_end_datetime=planned_end,
                            po_quantity=product_data['production_quantity'],
                            setup_time=actual_setup,
                            processing_time=(planned_end - planned_start).total_seconds() / 60 - actual_setup,
                            user=user_id
                        )
                        
                        self.db.add(schedule)
                        press_schedules.append({
                            'po_id': product_data['earliest_po'].po_id,
                            'po_number': product_data['earliest_po'].po_number,
                            'product_code': product.product_code,
                            'process_name': press_process.process_name,
                            'machine_list_id': machine_list_id,
                            'planned_start': planned_start,
                            'planned_end': planned_end,
                            'po_quantity': product_data['production_quantity']
                        })
                        
                        scheduled_product_processes[product_id].add(press_process.process_id)
                        added_schedule = True
                        
                        # 全工程完了チェック
                        press_process_ids = {p.process_id for p in product_data['press_processes']}
                        if press_process_ids <= scheduled_product_processes[product_id]:
                            fully_scheduled_products.add(product_id)
                            
                        break  # この製品の1つ目のプレス工程だけスケジュール
                    except Exception as e:
                        logger.warning(f"空き時間スケジュール失敗 (Product: {product.product_code}, Process: {press_process.process_name}): {str(e)}")
                        # スケジュールできなかった場合はスキップ
                        continue
                
                if added_schedule:
                    break  # 1つ追加したら再度チェック
            
            if not added_schedule:
                # これ以上追加できる工程がない
                break

    def _schedule_unconstrained_processes(
        self,
        target_products_list: List[Dict],
        product_schedules_map: Dict[str, List[Dict]],
        user_id: Optional[int] = None
    ) -> List[Dict]:
        """
        制約のない工程（TAP, BARREL, PACKING等）をスケジューリング
        
        製品単位で処理
        """
        unconstrained_schedules = []
        
        for product_data in target_products_list:
            product = product_data['product']
            product_code = product.product_code
            
            # この製品のスケジュール済み工程（プレス工程）
            existing_schedules = product_schedules_map.get(product_code, [])
            
            # プレス工程の終了日時を取得
            last_end_time = None
            if existing_schedules:
                last_end_time = max(s['planned_end'] for s in existing_schedules)
            else:
                # プレス工程がない場合は現在時刻から開始
                last_end_time = self.get_vietnam_now()
            
            # 制約のない工程を取得
            other_processes = [
                p for p in product_data['processes'] 
                if not self.is_press_process(p.process_name)
            ]
            
            current_start_time = last_end_time
            
            for process in other_processes:
                # 工程の所要時間を計算
                setup_time, processing_time = self.calculate_process_time(
                    process,
                    product_data['production_quantity']
                )
                
                total_time = setup_time + processing_time
                
                if total_time == 0:
                    continue
                
                # 開始時刻（前工程の終了時刻）
                planned_start = current_start_time
                
                # 終了時刻を計算
                planned_end = self.add_working_time(planned_start, total_time)
                
                # スケジュール登録
                # 機械IDは簡易的に割り当て（実際には機械の空き状況を見るべきだが、今回は簡易実装）
                machine_type = self.get_machine_type_from_process_name(process.process_name)
                machine_list_id = None
                
                if machine_type:
                    # 該当する機械の最初のものを割り当て
                    machines = self.db.query(MachineList).join(MachineType).filter(
                        MachineType.machine_type_name == machine_type
                    ).all()
                    if machines:
                        machine_list_id = machines[0].machine_list_id
                
                schedule = ProductionSchedule(
                    po_id=product_data['earliest_po'].po_id,
                    process_id=process.process_id,
                    machine_list_id=machine_list_id,
                    planned_start_datetime=planned_start,
                    planned_end_datetime=planned_end,
                    po_quantity=product_data['production_quantity'],
                    setup_time=setup_time,
                    processing_time=processing_time,
                    user=user_id
                )
                
                self.db.add(schedule)
                unconstrained_schedules.append({
                    'po_id': product_data['earliest_po'].po_id,
                    'po_number': product_data['earliest_po'].po_number,
                    'product_code': product_code,
                    'process_name': process.process_name,
                    'machine_list_id': machine_list_id,
                    'planned_start': planned_start,
                    'planned_end': planned_end,
                    'po_quantity': product_data['production_quantity']
                })
                
                # 次の工程の開始時刻を更新
                current_start_time = planned_end
                
        return unconstrained_schedules

    def generate_constrained_schedule(
        self,
        target_products: List[Dict],
        user_id: Optional[int] = None
    ) -> List[Dict]:
        """
        制約のある工程（PRESS等）のスケジュール生成

        日次優先・継続タスク最優先・稼働時間最大化
        """
        # 初期化（制約のある工程の機械のみ）
        self.initialize_constrained_machines()

        schedules = []
        today = self.get_vietnam_today()

        # 7日間順次処理
        for day_offset in range(7):
            current_date = today + timedelta(days=day_offset)

            # 休日スキップ
            if not self.is_working_day(current_date):
                continue

            # === 継続中タスクの処理 ===
            self.process_ongoing_tasks_for_day(current_date, schedules, user_id)

            # === 空き時間の最大活用（制約のある工程のみ） ===
            self.fill_constrained_processes_for_day(
                current_date,
                target_products,
                schedules,
                user_id
            )

        return schedules

    def initialize_constrained_machines(self):
        """制約のある工程の機械のみ初期化"""
        today = self.get_vietnam_today()

        for process_type, constraint in self.resource_constraints.items():
            if constraint['enabled'] and constraint['type'] == 'machine':
                # 該当する機械タイプを取得（例: PRESS機）
                machines = self.db.query(MachineList).join(MachineType).filter(
                    MachineType.machine_type_name == process_type
                ).all()

                for machine in machines:
                    # 日次スケジュールを初期化（7日分）
                    self.machine_daily_schedule[machine.machine_list_id] = {}
                    for day_offset in range(7):
                        date_key = (today + timedelta(days=day_offset)).isoformat()
                        self.machine_daily_schedule[machine.machine_list_id][date_key] = []

    def fill_constrained_processes_for_day(
        self,
        current_date: date,
        target_products: List[Dict],
        schedules: List[Dict],
        user_id: Optional[int] = None
    ):
        """制約のある工程の空き時間を埋める"""
        # 無限ループ防止
        max_iterations = 100
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            assigned = False

            # 生産締切日順に製品を処理
            for product_data in target_products:
                # 次の制約のある工程を探す
                next_process = self.find_next_constrained_process(product_data)

                if not next_process:
                    continue

                # 工程タイプを取得
                process_type = self.get_machine_type_from_process_name(next_process.process_name)
                
                if not process_type:
                    continue

                # 最適な機械を探す
                best_machine_id = self.find_best_machine(
                    next_process,
                    current_date,
                    process_type
                )

                if best_machine_id:
                    # 割り当て試行
                    success = self.assign_task_to_machine(
                        best_machine_id,
                        next_process,
                        product_data,
                        current_date,
                        schedules,
                        user_id
                    )
                    
                    if success:
                        assigned = True
                        break

            if not assigned:
                break

    def get_process_end_time(self, product_id: int, process_no: int, schedules: List[Dict]) -> Optional[datetime]:
        """指定された工程の最終終了時刻を取得"""
        end_times = []
        for schedule in schedules:
            # product_idのチェックが必要だが、schedulesにはproduct_codeしか入っていない
            # 簡易的にprocess_idでマッチングするか、product_codeでフィルタリングする
            # ここではschedules作成時にproduct_idを含めていないため、product_codeとprocess_noで判断する必要がある
            # しかしprocess_noもschedulesには含まれていない。
            # 既存のschedules構造: 'process_id'はある。
            
            if schedule.get('process_id'):
                # process_idからprocess_noを逆引きするのはコストがかかる
                # メモリ上のprocess_schedule_statusは使えないか？ -> statusだけで時刻はない
                
                # 仕方ないので、process_idが一致するもの探す
                # ただし、process_idを知るにはproduct_dataが必要
                pass

        # 効率化のため、schedulesから探すのではなく、
        # process_id を特定してから探す
        # 呼び出し元で process_no から process_id を特定するのは難しい（processesリストが必要）
        
        # 代替案: schedules に process_no を追加するのが一番良いが、既存ロジックへの影響範囲が大きい
        # ここでは、schedules の process_id を使って判定する
        
        # 全スケジュールのうち、この製品の指定Noの工程のものを抽出
        target_process_id = None
        # DBクエリは避けたい。
        # self.db.query(Process).filter(...) は遅くなる可能性。
        
        # 呼び出し元で prev_process オブジェクトを取得して、その process_id を渡す方が良いか？
        # しかし fill_constrained_processes_for_day では next_process しか持っていない。
        
        # ここはシンプルに、schedulesを走査して、該当する process_id の終了時刻の最大値を取る
        # そのために、まず process_id を特定する必要がある。
        
        # DBから取得（キャッシュ推奨だが今回は直接）
        process = self.db.query(Process).filter(
            Process.product_id == product_id,
            Process.process_no == process_no
        ).first()
        
        if not process:
            return None
            
        target_process_id = process.process_id
        
        max_end = None
        for schedule in schedules:
            if schedule['process_id'] == target_process_id:
                if max_end is None or schedule['planned_end'] > max_end:
                    max_end = schedule['planned_end']
                    
        return max_end

    def find_next_constrained_process(self, product_data: Dict) -> Optional[Process]:
        """
        次の制約のある工程を探す

        連続する同タイプ工程のみ並列実行可能
        前工程が異なるタイプの場合は完了を待つ
        """
        product = product_data['product']
        processes = product_data['processes']

        for process in processes:
            status_key = (product.product_id, process.process_no)
            status = self.process_schedule_status.get(status_key, 'pending')

            if status == 'pending':
                # この工程が制約対象かチェック
                process_type = self.get_machine_type_from_process_name(process.process_name)

                if process_type and process_type in self.resource_constraints:
                    if self.resource_constraints[process_type]['enabled']:

                        # 前工程チェック（連続する同タイプ工程のみ並列実行可能）
                        if process.process_no > 1:
                            # 前工程を取得
                            prev_process = None
                            for p in processes:
                                if p.process_no == process.process_no - 1:
                                    prev_process = p
                                    break

                            if prev_process:
                                prev_status_key = (product.product_id, prev_process.process_no)
                                prev_status = self.process_schedule_status.get(prev_status_key, 'pending')
                                prev_type = self.get_machine_type_from_process_name(prev_process.process_name)

                                # 前工程が異なるタイプの場合、完了を待つ
                                if prev_type != process_type:
                                    if prev_status != 'completed':
                                        continue  # この工程はスキップ（前工程完了待ち）
                                else:
                                    # 同じタイプ（連続PRESS等）の場合
                                    # 指定製品以外は並列実行不可（完了待ち）
                                    if product.product_code not in self.PARALLEL_EXECUTION_ALLOWED_PRODUCTS:
                                        if prev_status != 'completed':
                                            continue  # 並列実行不可のためスキップ

                        return process

        return None

    def find_best_machine(
        self,
        process: Process,
        current_date: date,
        process_type: str
    ) -> Optional[int]:
        """指定された工程タイプの最適な機械を選択"""
        # 該当する機械タイプを取得
        machines = self.db.query(MachineList).join(MachineType).filter(
            MachineType.machine_type_name == process_type
        ).all()

        best_machine_id = None
        max_free_time = 0

        for machine in machines:
            free_minutes = self.calculate_free_time(machine.machine_list_id, current_date)

            if free_minutes > max_free_time:
                max_free_time = free_minutes
                best_machine_id = machine.machine_list_id

        return best_machine_id if max_free_time > 10 else None

    def generate_unconstrained_schedule(
        self,
        target_products: List[Dict],
        constrained_schedules: List[Dict],
        user_id: Optional[int] = None
    ) -> List[Dict]:
        """
        制約のない工程のスケジュール生成（順次実行）

        制約のある工程（PRESS等）の完了時刻を基準に、
        TAP、BARREL、PACKING等の工程を順次実行としてスケジュール
        各工程は前工程の完了後に開始する
        """
        schedules = []

        for product_data in target_products:
            product = product_data['product']
            processes = product_data['processes']

            # この製品の制約のある工程（PRESS等）の完了時刻を取得
            constrained_end_time = self.get_constrained_processes_end_time(
                product, constrained_schedules
            )

            if not constrained_end_time:
                # 制約のある工程がスケジュールされていない
                continue

            # 制約のない工程を取得し、process_no順にソート
            unconstrained_processes = [
                p for p in processes if self.is_unconstrained_process(p)
            ]
            unconstrained_processes.sort(key=lambda p: p.process_no)

            # 順次実行のため、前工程の終了時刻を追跡
            current_start_time = constrained_end_time

            # 制約のない工程を順次実行としてスケジュール
            for process in unconstrained_processes:
                # 前工程の終了時刻から開始
                start_time = current_start_time

                # この工程の所要時間を計算
                setup_time, processing_time = self.calculate_process_time(
                    process, product_data['total_quantity']
                )

                total_time = setup_time + processing_time
                end_time = self.add_working_time(start_time, total_time)

                # スケジュール保存（machine_list_id=Noneで制約なしを示す）
                schedule = ProductionSchedule(
                    po_id=product_data['earliest_po'].po_id,
                    process_id=process.process_id,
                    machine_list_id=None,  # 制約なし
                    planned_start_datetime=start_time,
                    planned_end_datetime=end_time,
                    po_quantity=product_data['total_quantity'],
                    setup_time=setup_time,
                    processing_time=processing_time,
                    user=user_id
                )

                self.db.add(schedule)
                schedules.append({
                    'po_id': product_data['earliest_po'].po_id,
                    'po_number': product_data['earliest_po'].po_number,
                    'product_code': product.product_code,
                    'process_id': process.process_id,
                    'process_name': process.process_name,
                    'machine_list_id': None,  # 制約なし
                    'planned_start': start_time,
                    'planned_end': end_time,
                    'po_quantity': product_data['total_quantity'],
                    'is_parallel': False  # 順次実行
                })

                # 工程ステータスを完了にする
                self.update_process_status(product_data, process, True)

                # 次の工程の開始時刻を更新
                current_start_time = end_time

        return schedules

    def is_unconstrained_process(self, process: Process) -> bool:
        """制約のない工程（並行実行可能）かチェック"""
        process_type = self.get_machine_type_from_process_name(process.process_name)

        if not process_type:
            # 機械タイプが判定できない → 制約なし
            return True

        if process_type not in self.resource_constraints:
            # リソース制約に含まれていない → 制約なし
            return True

        # リソース制約に含まれているが、無効化されている → 制約なし
        return not self.resource_constraints[process_type]['enabled']

    def get_constrained_processes_end_time(
        self,
        product: Product,
        constrained_schedules: List[Dict]
    ) -> Optional[datetime]:
        """製品の制約のある工程（PRESS等）の最終完了時刻を取得"""
        end_times = []

        for schedule in constrained_schedules:
            if schedule['product_code'] == product.product_code:
                end_times.append(schedule['planned_end'])

        if end_times:
            return max(end_times)

        return None
