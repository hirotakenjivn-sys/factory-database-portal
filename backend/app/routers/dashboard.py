from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from ..database import get_db
from ..models.po import PO
from ..models.mold import BrokenMold

router = APIRouter()


@router.get("/cards")
async def get_dashboard_cards(db: Session = Depends(get_db)):
    """
    ダッシュボードカード用の統計データ
    """
    # 過去30日のPO売上（仮計算）
    thirty_days_ago = date.today() - timedelta(days=30)
    total_sales = db.query(func.sum(PO.po_quantity)).filter(
        PO.date_receive_po >= thirty_days_ago
    ).scalar() or 0

    # 本日生産数（仮データ）
    today_production = 5300

    # 金型故障中件数
    broken_molds = db.query(func.count(BrokenMold.broken_mold_id)).filter(
        BrokenMold.date_schedule_repaired >= date.today()
    ).scalar() or 0

    # 遅延件数（仮データ）
    delayed = 5

    return {
        "total_sales": total_sales,
        "today_production": today_production,
        "broken_molds": broken_molds,
        "delayed": delayed
    }


@router.get("/sales-weekly")
async def get_sales_weekly(db: Session = Depends(get_db)):
    """
    週別PO売上推移（仮データ）
    """
    return [
        {"week": 1, "quantity": 12000},
        {"week": 2, "quantity": 15000},
        {"week": 3, "quantity": 11000},
        {"week": 4, "quantity": 14000}
    ]


@router.get("/production-daily")
async def get_production_daily(db: Session = Depends(get_db)):
    """
    直近7日の生産数推移（仮データ）
    """
    today = date.today()
    return [
        {"date": str(today - timedelta(days=6)), "quantity": 5200},
        {"date": str(today - timedelta(days=5)), "quantity": 5400},
        {"date": str(today - timedelta(days=4)), "quantity": 5100},
        {"date": str(today - timedelta(days=3)), "quantity": 5500},
        {"date": str(today - timedelta(days=2)), "quantity": 5300},
        {"date": str(today - timedelta(days=1)), "quantity": 4800},
        {"date": str(today), "quantity": 5000}
    ]
