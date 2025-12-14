from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base


class IotButtonEvent(Base):
    __tablename__ = "iot_button_events"

    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    button_name = Column(String(100), nullable=False)
    raspi_no = Column(String(100), nullable=True)
    pressed_at = Column(DateTime, nullable=False, server_default=func.now())
    note = Column(Text, nullable=True)
    user = Column(String(100), default='raspi')
