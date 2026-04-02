from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IotButtonEventBase(BaseModel):
    button_name: str
    raspi_no: Optional[str] = None
    note: Optional[str] = None


class IotButtonEventCreate(IotButtonEventBase):
    pass


class IotButtonEvent(IotButtonEventBase):
    event_id: int
    pressed_at: datetime
    user: str

    class Config:
        from_attributes = True


# Press-raspi互換スキーマ
class IotPressEventItem(BaseModel):
    ts_ms: int


class IotPressEventIn(BaseModel):
    raspi_no: str = "unknown"
    events: list[IotPressEventItem]


class IotPressEventOut(BaseModel):
    status: str = "ok"
    total: int


class IotPressEventsResponse(BaseModel):
    events: list[int]


class IotPressEventRaw(BaseModel):
    id: int
    ts_ms: int
    raspi_no: str

    class Config:
        from_attributes = True
