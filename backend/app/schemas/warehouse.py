from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class FinishedProductBase(BaseModel):
    product_id: int
    lot_id: int
    finished_quantity: int
    date_finished: date


class FinishedProductCreate(FinishedProductBase):
    pass


class FinishedProductUpdate(BaseModel):
    product_id: Optional[int] = None
    lot_id: Optional[int] = None
    finished_quantity: Optional[int] = None
    date_finished: Optional[date] = None


class FinishedProduct(FinishedProductBase):
    finished_product_id: int
    timestamp: Optional[datetime]
    user: Optional[str]

    class Config:
        from_attributes = True


class FinishedProductWithDetails(FinishedProduct):
    product_code: Optional[str] = None
    lot_number: Optional[str] = None
    customer_name: Optional[str] = None

    class Config:
        from_attributes = True
