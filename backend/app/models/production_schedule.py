from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, String
from sqlalchemy.sql import func
from ..database import Base


class ProductionSchedule(Base):
    __tablename__ = "production_schedule"

    schedule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_id = Column(Integer, ForeignKey("po.po_id", ondelete="CASCADE"), nullable=False, index=True)
    process_id = Column(Integer, ForeignKey("processes.process_id", ondelete="CASCADE"), nullable=False, index=True)
    machine_list_id = Column(Integer, ForeignKey("machine_list.machine_list_id", ondelete="SET NULL"), nullable=True, index=True)
    planned_start_datetime = Column(DateTime, nullable=False, index=True)
    planned_end_datetime = Column(DateTime, nullable=False, index=True)
    po_quantity = Column(Integer, nullable=False)
    setup_time = Column(DECIMAL(10, 2), default=0, comment="段取時間（分）")
    processing_time = Column(DECIMAL(10, 2), default=0, comment="加工時間（分）")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100), nullable=True)
