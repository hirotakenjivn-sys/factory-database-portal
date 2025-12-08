from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    customer_name: str
    is_active: bool = True


class CustomerCreate(CustomerBase):
    user: Optional[str] = None


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    is_active: Optional[bool] = None
    user: Optional[str] = None


class CustomerResponse(CustomerBase):
    customer_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
