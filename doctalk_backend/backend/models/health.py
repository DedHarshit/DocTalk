from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

MetricType = Literal[
    "blood_pressure",
    "blood_sugar",
    "weight",
    "heart_rate",
    "spo2",
    "temperature",
]


class MetricLog(BaseModel):
    metric_type: MetricType
    value: float
    unit: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


class MetricResponse(BaseModel):
    id: str
    metric_type: str
    value: float
    unit: Optional[str]
    notes: Optional[str]
    recorded_at: str
    created_at: str


class MetricSummary(BaseModel):
    metric_type: str
    count: int
    average: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    latest_value: Optional[float]
    latest_recorded_at: Optional[str]


class MetricAlert(BaseModel):
    metric_type: str
    value: float
    message: str
    severity: Literal["info", "warning", "critical"]
    recorded_at: str


# Normal ranges for alert generation
NORMAL_RANGES = {
    "heart_rate": {"min": 60, "max": 100, "unit": "bpm"},
    "spo2": {"min": 95, "max": 100, "unit": "%"},
    "temperature": {"min": 36.1, "max": 37.2, "unit": "°C"},
    "blood_sugar": {"min": 70, "max": 140, "unit": "mg/dL"},
    "weight": {"min": None, "max": None, "unit": "kg"},
    "blood_pressure": {"min": None, "max": None, "unit": "mmHg"},
}
