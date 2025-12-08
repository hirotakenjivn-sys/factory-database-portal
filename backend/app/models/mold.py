from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class BrokenMold(Base):
    __tablename__ = "broken_mold"

    broken_mold_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    process_id = Column(Integer, ForeignKey("processes.process_id"), nullable=False)
    date_broken = Column(Date, nullable=False)
    date_hope_repaired = Column(Date)
    date_schedule_repaired = Column(Date)
    note = Column(Text)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
