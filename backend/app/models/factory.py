from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Factory(Base):
    __tablename__ = "factories"

    factory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factory_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))


class MachineType(Base):
    __tablename__ = "machine_types"

    machine_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_type_name = Column(String(50), nullable=False, unique=True)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))


class MachineList(Base):
    __tablename__ = "machine_list"

    machine_list_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factory_id = Column(Integer, ForeignKey("factories.factory_id"), nullable=False)
    machine_no = Column(String(100), nullable=False)
    machine_type_id = Column(Integer, ForeignKey("machine_types.machine_type_id"), nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))

    # Relationships
    machine_type = relationship("MachineType")


class WorkingHours(Base):
    __tablename__ = "working_hours"

    working_hours_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factory_id = Column(Integer, ForeignKey("factories.factory_id"), nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
