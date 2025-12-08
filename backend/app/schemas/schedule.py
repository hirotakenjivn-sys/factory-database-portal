from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ============================================
# Holiday Type Schemas
# ============================================

class HolidayTypeBase(BaseModel):
    date_type: str


class HolidayTypeCreate(HolidayTypeBase):
    pass


class HolidayType(HolidayTypeBase):
    holiday_type_id: int

    class Config:
        from_attributes = True


# ============================================
# Calendar (Holiday) Schemas
# ============================================

class CalendarBase(BaseModel):
    date_holiday: date
    holiday_type_id: int


class CalendarCreate(CalendarBase):
    pass


class CalendarUpdate(BaseModel):
    date_holiday: Optional[date] = None
    holiday_type_id: Optional[int] = None


class Calendar(CalendarBase):
    calendar_id: int
    timestamp: Optional[datetime] = None
    user: Optional[str] = None

    class Config:
        from_attributes = True


class CalendarWithDetails(Calendar):
    date_type: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# Production Schedule Schemas
# ============================================

class ProductionScheduleBase(BaseModel):
    po_id: int
    process_id: int
    machine_list_id: Optional[int] = None
    planned_start_datetime: datetime
    planned_end_datetime: datetime
    po_quantity: int
    setup_time: Optional[float] = 0
    processing_time: Optional[float] = 0


class ProductionScheduleCreate(ProductionScheduleBase):
    pass


class ProductionScheduleUpdate(BaseModel):
    po_id: Optional[int] = None
    process_id: Optional[int] = None
    machine_list_id: Optional[int] = None
    planned_start_datetime: Optional[datetime] = None
    planned_end_datetime: Optional[datetime] = None
    po_quantity: Optional[int] = None
    setup_time: Optional[float] = None
    processing_time: Optional[float] = None


class ProductionSchedule(ProductionScheduleBase):
    schedule_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[str] = None

    class Config:
        from_attributes = True
