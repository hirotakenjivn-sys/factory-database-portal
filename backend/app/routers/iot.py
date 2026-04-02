from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models.iot_button_event import IotButtonEvent
from ..models.iot_press_event import IotPressEvent
from ..schemas.iot import (
    IotButtonEventCreate,
    IotButtonEvent as IotButtonEventSchema,
    IotPressEventIn,
    IotPressEventOut,
    IotPressEventsResponse,
    IotPressEventRaw,
)

router = APIRouter()


@router.post("/events", response_model=IotButtonEventSchema)
async def create_iot_event(event: IotButtonEventCreate, db: Session = Depends(get_db)):
    """
    IoTボタン押下イベントを記録する
    """
    db_event = IotButtonEvent(
        button_name=event.button_name,
        raspi_no=event.raspi_no,
        note=event.note
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.post("/events/press", response_model=IotPressEventOut)
async def create_press_events(payload: IotPressEventIn, db: Session = Depends(get_db)):
    """
    プレスショットイベントをバッチ受信する (Press-raspi互換)
    """
    objects = [
        IotPressEvent(ts_ms=ev.ts_ms, raspi_no=payload.raspi_no)
        for ev in payload.events
    ]
    db.add_all(objects)
    db.commit()
    total = db.query(IotPressEvent).count()
    return IotPressEventOut(status="ok", total=total)


@router.get("/events", response_model=IotPressEventsResponse)
async def get_press_events(
    start_ms: int = Query(..., description="開始タイムスタンプ (ms)"),
    end_ms: int = Query(..., description="終了タイムスタンプ (ms)"),
    raspi_no: Optional[str] = Query(None, description="ラズパイ番号でフィルタ"),
    db: Session = Depends(get_db),
):
    """
    プレスイベントを時間範囲で取得する (タイムライングラフ用)
    """
    stmt = (
        select(IotPressEvent.ts_ms)
        .where(IotPressEvent.ts_ms >= start_ms)
        .where(IotPressEvent.ts_ms <= end_ms)
    )
    if raspi_no:
        stmt = stmt.where(IotPressEvent.raspi_no == raspi_no)
    stmt = stmt.order_by(IotPressEvent.ts_ms.asc())
    rows = db.execute(stmt).scalars().all()
    return IotPressEventsResponse(events=list(rows))


@router.get("/events/raw", response_model=list[IotPressEventRaw])
async def get_press_events_raw(
    limit: int = Query(200, description="取得件数", ge=1, le=5000),
    raspi_no: Optional[str] = Query(None, description="ラズパイ番号でフィルタ"),
    db: Session = Depends(get_db),
):
    """
    プレスイベント生データを新しい順に返す
    """
    stmt = select(IotPressEvent).order_by(IotPressEvent.ts_ms.desc())
    if raspi_no:
        stmt = stmt.where(IotPressEvent.raspi_no == raspi_no)
    stmt = stmt.limit(limit)
    rows = db.execute(stmt).scalars().all()
    return rows
