from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class HolidayType(Base):
    __tablename__ = "holiday_types"

    holiday_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_type = Column(String(50), nullable=False, comment="例: 祝日, 会社休日, 土日")


class Calendar(Base):
    __tablename__ = "calendar"

    calendar_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_holiday = Column(Date, nullable=False, unique=True, index=True)
    holiday_type_id = Column(Integer, ForeignKey("holiday_types.holiday_type_id"), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
