from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


# ==================== Material Type ====================
class MaterialTypeBase(BaseModel):
    material_name: str
    note: Optional[str] = None


class MaterialTypeCreate(MaterialTypeBase):
    user: Optional[str] = None


class MaterialTypeUpdate(BaseModel):
    material_name: Optional[str] = None
    note: Optional[str] = None
    user: Optional[str] = None


class MaterialTypeResponse(MaterialTypeBase):
    material_type_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Material Form ====================
class MaterialFormBase(BaseModel):
    material_form_code: str
    form_name: str


class MaterialFormCreate(MaterialFormBase):
    pass


class MaterialFormResponse(MaterialFormBase):
    model_config = ConfigDict(from_attributes=True)


# ==================== Material Spec ====================
class MaterialSpecBase(BaseModel):
    material_type_id: int
    material_form_code: str
    thickness_mm: Optional[Decimal] = None
    width_mm: Optional[Decimal] = None
    length_mm: Optional[Decimal] = None
    thickness_tol_plus: Optional[Decimal] = None
    thickness_tol_minus: Optional[Decimal] = None
    width_tol_plus: Optional[Decimal] = None
    width_tol_minus: Optional[Decimal] = None
    length_tol_plus: Optional[Decimal] = None
    length_tol_minus: Optional[Decimal] = None


class MaterialSpecCreate(MaterialSpecBase):
    user: Optional[str] = None


class MaterialSpecUpdate(BaseModel):
    material_type_id: Optional[int] = None
    material_form_code: Optional[str] = None
    thickness_mm: Optional[Decimal] = None
    width_mm: Optional[Decimal] = None
    length_mm: Optional[Decimal] = None
    thickness_tol_plus: Optional[Decimal] = None
    thickness_tol_minus: Optional[Decimal] = None
    width_tol_plus: Optional[Decimal] = None
    width_tol_minus: Optional[Decimal] = None
    length_tol_plus: Optional[Decimal] = None
    length_tol_minus: Optional[Decimal] = None
    user: Optional[str] = None


class MaterialSpecResponse(MaterialSpecBase):
    material_spec_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialSpecWithDetails(MaterialSpecResponse):
    material_name: Optional[str] = None
    form_name: Optional[str] = None


# ==================== Material Item ====================
class MaterialItemBase(BaseModel):
    material_code: str
    material_spec_id: int
    description: Optional[str] = None


class MaterialItemCreate(MaterialItemBase):
    user: Optional[str] = None


class MaterialItemUpdate(BaseModel):
    material_spec_id: Optional[int] = None
    description: Optional[str] = None
    user: Optional[str] = None


class MaterialItemResponse(MaterialItemBase):
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialItemWithDetails(MaterialItemResponse):
    material_name: Optional[str] = None
    form_name: Optional[str] = None
    thickness_mm: Optional[Decimal] = None
    width_mm: Optional[Decimal] = None
    length_mm: Optional[Decimal] = None


# ==================== Material Lot ====================
class MaterialLotBase(BaseModel):
    material_code: str
    lot_no: str
    supplier_id: Optional[int] = None
    received_date: Optional[date] = None
    inspection_status: Optional[str] = "PENDING"


class MaterialLotCreate(MaterialLotBase):
    user: Optional[str] = None


class MaterialLotUpdate(BaseModel):
    material_code: Optional[str] = None
    lot_no: Optional[str] = None
    supplier_id: Optional[int] = None
    received_date: Optional[date] = None
    inspection_status: Optional[str] = None
    user: Optional[str] = None


class MaterialLotResponse(MaterialLotBase):
    lot_id: int
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialLotWithDetails(MaterialLotResponse):
    supplier_name: Optional[str] = None
    material_name: Optional[str] = None
    description: Optional[str] = None


# ==================== Material Transaction ====================
class MaterialTransactionBase(BaseModel):
    lot_id: int
    factory_id: int
    sheet_qty: Optional[int] = 0
    coil_qty: Optional[int] = 0
    weight_kg: Optional[Decimal] = 0
    transaction_type: str  # IN, OUT
    note: Optional[str] = None


class MaterialTransactionCreate(MaterialTransactionBase):
    transaction_date: Optional[datetime] = None
    user: Optional[str] = None


class MaterialTransactionResponse(MaterialTransactionBase):
    transaction_id: int
    transaction_date: datetime
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialTransactionWithDetails(MaterialTransactionResponse):
    lot_no: Optional[str] = None
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    factory_name: Optional[str] = None


# ==================== Material Stock Snapshot ====================
class MaterialStockSnapshotBase(BaseModel):
    lot_id: int
    factory_id: int
    sheet_qty: Optional[int] = 0
    coil_qty: Optional[int] = 0
    weight_kg: Optional[Decimal] = 0


class MaterialStockSnapshotResponse(MaterialStockSnapshotBase):
    last_updated: datetime
    timestamp: datetime
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialStockWithDetails(MaterialStockSnapshotResponse):
    lot_no: Optional[str] = None
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    factory_name: Optional[str] = None
    supplier_name: Optional[str] = None
