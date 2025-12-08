from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    employee_no: str
    name: str
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    user: Optional[str] = None


class EmployeeUpdate(BaseModel):
    employee_no: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    user: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    employee_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
