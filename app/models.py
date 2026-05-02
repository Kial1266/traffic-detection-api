from datetime import datetime, timezone

from pydantic import BaseModel, Field, conint, constr
from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    waktu_frame = Column(Integer, nullable=False)
    jumlah_kendaraan = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class TrafficLogCreate(BaseModel):
    waktu_frame: conint(ge=0)
    jumlah_kendaraan: conint(ge=0)
    status: constr(min_length=1, max_length=32)


class TrafficLogRead(BaseModel):
    id: int
    waktu_frame: int
    jumlah_kendaraan: int
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True,
    }