from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.iot_button_event import IotButtonEvent
from ..schemas.iot import IotButtonEventCreate, IotButtonEvent as IotButtonEventSchema

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
