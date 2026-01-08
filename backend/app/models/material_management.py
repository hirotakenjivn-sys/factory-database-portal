from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class MaterialType(Base):
    """Material type master (e.g., SUS304, SPCC, etc.)"""
    __tablename__ = "material_types"

    material_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_name = Column(String(100), nullable=False, index=True)
    note = Column(Text)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    specs = relationship("MaterialSpec", back_populates="material_type")


class MaterialForm(Base):
    """Material form master (COIL, SHEET, etc.)"""
    __tablename__ = "material_forms"

    material_form_code = Column(String(20), primary_key=True, index=True)
    form_name = Column(String(50), nullable=False)

    # Relationships
    specs = relationship("MaterialSpec", back_populates="material_form")


class MaterialSpec(Base):
    """Material specifications with dimensions and tolerances"""
    __tablename__ = "material_specs"

    material_spec_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_type_id = Column(Integer, ForeignKey("material_types.material_type_id"), nullable=False, index=True)
    material_form_code = Column(String(20), ForeignKey("material_forms.material_form_code"), nullable=False, index=True)

    # Dimensions
    thickness_mm = Column(Numeric(10, 3))
    width_mm = Column(Numeric(10, 2))
    length_mm = Column(Numeric(10, 2))

    # Tolerances
    thickness_tol_plus = Column(Numeric(10, 4))
    thickness_tol_minus = Column(Numeric(10, 4))
    width_tol_plus = Column(Numeric(10, 3))
    width_tol_minus = Column(Numeric(10, 3))
    length_tol_plus = Column(Numeric(10, 3))
    length_tol_minus = Column(Numeric(10, 3))

    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    material_type = relationship("MaterialType", back_populates="specs")
    material_form = relationship("MaterialForm", back_populates="specs")
    items = relationship("MaterialItem", back_populates="spec")


class MaterialItem(Base):
    """Material items with unique codes"""
    __tablename__ = "material_items"

    material_code = Column(String(50), primary_key=True, index=True)
    material_spec_id = Column(Integer, ForeignKey("material_specs.material_spec_id"), nullable=False, index=True)
    description = Column(String(255))

    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    spec = relationship("MaterialSpec", back_populates="items")
    lots = relationship("MaterialLot", back_populates="material_item")


class MaterialLot(Base):
    """Material lots with supplier and inspection info"""
    __tablename__ = "material_lots"

    lot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_code = Column(String(50), ForeignKey("material_items.material_code"), nullable=False, index=True)
    lot_no = Column(String(100), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True, index=True)
    received_date = Column(Date)
    inspection_status = Column(String(20), default="PENDING")  # PENDING, PASSED, FAILED

    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    material_item = relationship("MaterialItem", back_populates="lots")
    transactions = relationship("MaterialTransaction", back_populates="lot")
    stock_snapshots = relationship("MaterialStockSnapshot", back_populates="lot")


class MaterialTransaction(Base):
    """Material inventory transactions (IN/OUT)"""
    __tablename__ = "material_transactions"

    transaction_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    transaction_date = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    lot_id = Column(Integer, ForeignKey("material_lots.lot_id"), nullable=False, index=True)
    factory_id = Column(Integer, ForeignKey("factories.factory_id"), nullable=False, index=True)

    # Quantities
    sheet_qty = Column(Integer, default=0)
    coil_qty = Column(Integer, default=0)
    weight_kg = Column(Numeric(12, 3), default=0)

    transaction_type = Column(String(10), nullable=False)  # IN, OUT
    note = Column(Text)

    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    lot = relationship("MaterialLot", back_populates="transactions")


class MaterialStockSnapshot(Base):
    """Current material stock by lot and factory"""
    __tablename__ = "material_stock_snapshot"

    lot_id = Column(Integer, ForeignKey("material_lots.lot_id"), primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.factory_id"), primary_key=True, index=True)

    # Current quantities
    sheet_qty = Column(Integer, default=0)
    coil_qty = Column(Integer, default=0)
    weight_kg = Column(Numeric(12, 3), default=0)

    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    lot = relationship("MaterialLot", back_populates="stock_snapshots")
