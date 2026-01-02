from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProcessBase(BaseModel):
    product_id: int
    process_no: int
    process_name: str
    rough_cycletime: Optional[Decimal] = None
    setup_time: Optional[Decimal] = None
    production_limit: Optional[int] = None


class ProcessCreate(ProcessBase):
    user: Optional[str] = None


class ProcessUpdate(BaseModel):
    product_id: Optional[int] = None
    process_no: Optional[int] = None
    process_name: Optional[str] = None
    rough_cycletime: Optional[Decimal] = None
    setup_time: Optional[Decimal] = None
    production_limit: Optional[int] = None
    user: Optional[str] = None


class ProcessResponse(ProcessBase):
    process_id: int
    timestamp: Optional[datetime] = None
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProcessWithDetailsResponse(ProcessResponse):
    customer_name: str
    product_code: str

    model_config = ConfigDict(from_attributes=True)


# ProcessNameType schemas
class ProcessNameTypeBase(BaseModel):
    process_name: str
    day_or_spm: Optional[bool] = None


class ProcessNameTypeCreate(ProcessNameTypeBase):
    user: Optional[str] = None


class ProcessNameTypeUpdate(BaseModel):
    process_name: Optional[str] = None
    day_or_spm: Optional[bool] = None
    user: Optional[str] = None


class ProcessNameTypeResponse(ProcessNameTypeBase):
    process_name_id: int
    timestamp: Optional[datetime] = None
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
