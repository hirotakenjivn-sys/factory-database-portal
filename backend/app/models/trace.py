from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class StampTrace(Base):
    __tablename__ = "stamp_traces"

    stamp_trace_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey("lot.lot_id"), nullable=False, index=True)
    process_id = Column(Integer, ForeignKey("processes.process_id"), nullable=False, index=True)
    po_id = Column(Integer, ForeignKey("po.po_id"), nullable=True, index=True)  # POに紐づかない作業の場合はNULL
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    ok_quantity = Column(Integer, nullable=False)
    ng_quantity = Column(Integer, nullable=False)
    result = Column(String(50))  # pass, fail, rework
    done = Column(Boolean, default=False)
    date = Column(Date, nullable=False, index=True)
    note = Column(Text)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    lot = relationship("Lot")
    process = relationship("Process")
    po = relationship("PO")
    employee = relationship("Employee")


class OutsourceTrace(Base):
    __tablename__ = "outsource_traces"

    outsource_trace_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey("lot.lot_id"), nullable=False, index=True)
    process_id = Column(Integer, ForeignKey("processes.process_id"), nullable=False, index=True)
    po_id = Column(Integer, ForeignKey("po.po_id"), nullable=True, index=True)  # POに紐づかない作業の場合はNULL
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    ok_quantity = Column(Integer, nullable=False)
    ng_quantity = Column(Integer, nullable=False)
    date = Column(Date, nullable=False, index=True)
    note = Column(Text)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    lot = relationship("Lot")
    process = relationship("Process")
    po = relationship("PO")
    supplier = relationship("Supplier")
