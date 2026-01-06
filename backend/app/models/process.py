from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ProcessNameType(Base):
    __tablename__ = "process_name_types"

    process_name_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    process_name = Column(String(100), nullable=False)
    day_or_spm = Column(Boolean, comment="TRUE: SPM, FALSE: DAY")
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))


class Process(Base):
    __tablename__ = "processes"

    process_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
    process_no = Column(Integer, nullable=False)
    process_name_id = Column(Integer, ForeignKey("process_name_types.process_name_id"), nullable=False, index=True)
    rough_cycletime = Column(Integer)
    setup_time = Column(Integer, comment="段取時間（分）")
    production_limit = Column(Integer, comment="生産可能限界")
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    product = relationship("Product", back_populates="processes")
    process_name_type = relationship("ProcessNameType")
