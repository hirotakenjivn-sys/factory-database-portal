from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class BrokenMoldBase(BaseModel):
    process_id: int
    date_broken: date
    date_hope_repaired: Optional[date] = None
    date_schedule_repaired: Optional[date] = None
    note: Optional[str] = None


class BrokenMoldCreate(BrokenMoldBase):
    pass


class BrokenMoldUpdate(BaseModel):
    process_id: Optional[int] = None
    date_broken: Optional[date] = None
    date_hope_repaired: Optional[date] = None
    date_schedule_repaired: Optional[date] = None
    note: Optional[str] = None


class BrokenMold(BrokenMoldBase):
    broken_mold_id: int
    timestamp: Optional[datetime]
    user: Optional[str]

    class Config:
        from_attributes = True


class BrokenMoldWithDetails(BrokenMold):
    product_code: Optional[str] = None
    process_name: Optional[str] = None
    process_no: Optional[int] = None

    class Config:
        from_attributes = True
