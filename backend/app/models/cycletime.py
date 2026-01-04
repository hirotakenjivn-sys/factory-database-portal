from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Cycletime(Base):
    __tablename__ = "cycletimes"

    cycletime_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    process_name = Column(String(100), nullable=False)
    press_no = Column(String(100), nullable=False)
    cycle_time = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
