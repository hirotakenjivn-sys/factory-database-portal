from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supplier_name = Column(String(255), nullable=False)
    supplier_business = Column(String(255))
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
