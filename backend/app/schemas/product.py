from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    product_code: str
    customer_id: int
    is_active: bool = True


class ProductCreate(ProductBase):
    user: Optional[str] = None


class ProductUpdate(BaseModel):
    product_code: Optional[str] = None
    customer_id: Optional[int] = None
    is_active: Optional[bool] = None
    user: Optional[str] = None


class ProductResponse(ProductBase):
    product_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
