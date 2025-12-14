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
