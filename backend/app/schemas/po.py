from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class POBase(BaseModel):
    po_number: str
    product_id: int
    delivery_date: date
    date_receive_po: date
    po_quantity: int


class POCreate(POBase):
    is_delivered: Optional[bool] = False
    user: Optional[str] = None


class POUpdate(BaseModel):
    po_number: Optional[str] = None
    product_id: Optional[int] = None
    delivery_date: Optional[date] = None
    date_receive_po: Optional[date] = None
    po_quantity: Optional[int] = None
    is_delivered: Optional[bool] = None
    user: Optional[str] = None


class POResponse(POBase):
    po_id: int
    is_delivered: bool
    timestamp: datetime
    user: Optional[str] = None
    customer_name: Optional[str] = None
    product_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DeletedPOResponse(BaseModel):
    deleted_po_id: int
    po_id: int
    po_number: str
    product_id: int
    delivery_date: date
    date_receive_po: date
    po_quantity: int
    is_delivered: bool
    original_timestamp: datetime
    original_user: Optional[str] = None
    deleted_timestamp: datetime
    deleted_by_user: str

    model_config = ConfigDict(from_attributes=True)
