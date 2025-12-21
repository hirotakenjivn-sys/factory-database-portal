from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_no = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    password_hash = Column(String(255), nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = Column(String(100))
