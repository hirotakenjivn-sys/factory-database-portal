from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# Stamp Trace Schemas
class StampTraceBase(BaseModel):
    lot_id: int
    process_id: int
    po_id: Optional[int] = None  # POに紐づかない作業の場合はNULL
    employee_id: int
    ok_quantity: int
    ng_quantity: int
    result: Optional[str] = None
    date: date
    note: Optional[str] = None
    done: bool = False


class StampTraceCreate(StampTraceBase):
    user: Optional[str] = None


class StampTraceResponse(StampTraceBase):
    stamp_trace_id: int
    timestamp: datetime
    user: Optional[str] = None
    employee_name: Optional[str] = None
    process_name: Optional[str] = None
    done: bool = False

    model_config = ConfigDict(from_attributes=True)


# Outsource Trace Schemas
class OutsourceTraceBase(BaseModel):
    lot_id: int
    process_id: int
    po_id: Optional[int] = None  # POに紐づかない作業の場合はNULL
    supplier_id: int
    ok_quantity: int
    ng_quantity: int
    date: date
    note: Optional[str] = None


class OutsourceTraceCreate(OutsourceTraceBase):
    user: Optional[str] = None


class OutsourceTraceResponse(OutsourceTraceBase):
    outsource_trace_id: int
    timestamp: datetime
    user: Optional[str] = None
    supplier_name: Optional[str] = None
    process_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Combined Trace Response for Search Results
class TraceDetailResponse(BaseModel):
    product_code: str
    product_id: int
    customer_name: str
    lot_number: str
    lot_id: int
    po_number: str
    po_id: int
    delivery_date: date
    po_quantity: int
    stamp_traces: List[StampTraceResponse]
    outsource_traces: List[OutsourceTraceResponse]

    model_config = ConfigDict(from_attributes=True)


# Search Request
class TraceSearchRequest(BaseModel):
    search_type: str  # 'product', 'lot', 'po'
    search_value: str
