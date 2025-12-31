from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class FactoryBase(BaseModel):
    factory_name: str


class FactoryCreate(FactoryBase):
    user: Optional[str] = None


class FactoryUpdate(BaseModel):
    factory_name: Optional[str] = None
    user: Optional[str] = None


class FactoryResponse(FactoryBase):
    factory_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MachineTypeBase(BaseModel):
    machine_type_name: str


class MachineTypeCreate(MachineTypeBase):
    user: Optional[str] = None


class MachineTypeUpdate(BaseModel):
    machine_type_name: Optional[str] = None
    user: Optional[str] = None


class MachineTypeResponse(MachineTypeBase):
    machine_type_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MachineListBase(BaseModel):
    factory_id: int
    machine_no: str
    machine_type_id: Optional[int] = None


class MachineListCreate(MachineListBase):
    user: Optional[str] = None


class MachineListUpdate(BaseModel):
    factory_id: Optional[int] = None
    machine_no: Optional[str] = None
    machine_type_id: Optional[int] = None
    user: Optional[str] = None


class MachineListResponse(MachineListBase):
    machine_list_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MachineListWithDetails(MachineListResponse):
    factory_name: Optional[str] = None
    machine_type_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WorkingHoursBase(BaseModel):
    factory_id: int
    hours: Decimal


class WorkingHoursCreate(WorkingHoursBase):
    user: Optional[str] = None


class WorkingHoursUpdate(BaseModel):
    factory_id: Optional[int] = None
    hours: Optional[Decimal] = None
    user: Optional[str] = None


class WorkingHoursResponse(WorkingHoursBase):
    working_hours_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
