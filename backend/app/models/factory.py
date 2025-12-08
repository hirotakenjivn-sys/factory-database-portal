from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from ..database import Base


class Factory(Base):
    __tablename__ = "factories"

    factory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factory_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))


class MachineList(Base):
    __tablename__ = "machine_list"

    machine_list_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factory_id = Column(Integer, ForeignKey("factories.factory_id"), nullable=False)
    machine_no = Column(String(100), nullable=False)
    machine_type = Column(Enum('PRESS', 'TAP', 'BARREL', name='machine_type_enum'), nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))


class WorkingHours(Base):
    __tablename__ = "working_hours"

    working_hours_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factory_id = Column(Integer, ForeignKey("factories.factory_id"), nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
