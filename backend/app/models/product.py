from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_code = Column(String(100), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    customer = relationship("Customer", back_populates="products")
    processes = relationship("Process", back_populates="product")
    pos = relationship("PO", back_populates="product")
    lots = relationship("Lot", back_populates="product")
    finished_products = relationship("FinishedProduct", back_populates="product")
