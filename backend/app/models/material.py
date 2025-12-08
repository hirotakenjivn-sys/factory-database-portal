from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class MaterialRate(Base):
    __tablename__ = "material_rates"

    material_rate_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    thickness = Column(Numeric(10, 2))
    width = Column(Numeric(10, 2))
    pitch = Column(Numeric(10, 2))
    h = Column(Numeric(10, 2))
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
