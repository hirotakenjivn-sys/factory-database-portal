from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SupplierBase(BaseModel):
    supplier_name: str
    supplier_business: Optional[str] = None


class SupplierCreate(SupplierBase):
    user: Optional[str] = None


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_business: Optional[str] = None
    user: Optional[str] = None


class SupplierResponse(SupplierBase):
    supplier_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
