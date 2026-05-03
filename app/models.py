from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class DetectionDetail(BaseModel):
    class_name: str = Field(alias="class")
    confidence: float
    x: float
    y: float
    width: float
    height: float

class TrafficAnalysis(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    jumlah_kendaraan: int
    density_score: float
    status: str
    rincian: dict
    raw_predictions: List[DetectionDetail]