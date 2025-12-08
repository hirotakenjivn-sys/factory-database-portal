from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SPMBase(BaseModel):
    product_id: int
    process_name: str
    press_no: str
    cycle_time: Decimal


class SPMCreate(SPMBase):
    user: Optional[str] = None


class SPMUpdate(BaseModel):
    product_id: Optional[int] = None
    process_name: Optional[str] = None
    press_no: Optional[str] = None
    cycle_time: Optional[Decimal] = None
    user: Optional[str] = None


class SPMResponse(SPMBase):
    spm_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SPMWithDetails(SPMResponse):
    product_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
