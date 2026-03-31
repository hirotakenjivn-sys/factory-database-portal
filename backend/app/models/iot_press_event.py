from sqlalchemy import Column, Integer, BigInteger, String, Index
from ..database import Base


class IotPressEvent(Base):
    __tablename__ = "iot_press_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ts_ms = Column(BigInteger, nullable=False)
    raspi_no = Column(String(50), nullable=False, default="unknown")

    __table_args__ = (
        Index("idx_iot_press_ts_ms", "ts_ms"),
        Index("idx_iot_press_raspi_no", "raspi_no"),
    )
