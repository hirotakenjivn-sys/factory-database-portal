from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class PO(Base):
    __tablename__ = "po"

    po_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_number = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    delivery_date = Column(Date, nullable=False, index=True)
    date_receive_po = Column(Date, nullable=False)
    po_quantity = Column(Integer, nullable=False)
    is_delivered = Column(Boolean, default=False, nullable=False, index=True)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    product = relationship("Product", back_populates="pos")


class DeletedPO(Base):
    __tablename__ = "deleted_po"

    deleted_po_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_id = Column(Integer, nullable=False)
    po_number = Column(String(100), nullable=False)
    product_id = Column(Integer, nullable=False)
    delivery_date = Column(Date, nullable=False)
    date_receive_po = Column(Date, nullable=False)
    po_quantity = Column(Integer, nullable=False)
    is_delivered = Column(Boolean, nullable=False)
    original_timestamp = Column(DateTime, nullable=False)
    original_user = Column(String(100))
    deleted_timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    deleted_by_user = Column(String(100), nullable=False)
