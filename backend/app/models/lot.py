from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Lot(Base):
    __tablename__ = "lot"

    lot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lot_number = Column(String(100), nullable=False, unique=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    date_created = Column(Date, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    product = relationship("Product", back_populates="lots")
    finished_products = relationship("FinishedProduct", back_populates="lot")
