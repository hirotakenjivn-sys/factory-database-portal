from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MaterialRateBase(BaseModel):
    product_id: int
    thickness: Optional[Decimal] = None
    width: Optional[Decimal] = None
    pitch: Optional[Decimal] = None
    h: Optional[Decimal] = None


class MaterialRateCreate(MaterialRateBase):
    user: Optional[str] = None


class MaterialRateUpdate(BaseModel):
    product_id: Optional[int] = None
    thickness: Optional[Decimal] = None
    width: Optional[Decimal] = None
    pitch: Optional[Decimal] = None
    h: Optional[Decimal] = None
    user: Optional[str] = None


class MaterialRateResponse(MaterialRateBase):
    material_rate_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialRateWithDetails(MaterialRateResponse):
    product_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
