from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class FinishedProduct(Base):
    __tablename__ = "finished_products"

    finished_product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("lot.lot_id"), nullable=False)
    finished_quantity = Column(Integer, nullable=False)
    date_finished = Column(Date, nullable=False)
    is_shipped = Column(Boolean, default=False, nullable=False, index=True)  # 出荷済みフラグ
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    product = relationship("Product", back_populates="finished_products")
    lot = relationship("Lot", back_populates="finished_products")
