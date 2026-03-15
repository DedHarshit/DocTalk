from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ReminderCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=200)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., description="e.g. daily, twice daily, weekly")
    times: list[str] = Field(..., description="e.g. ['08:00', '20:00']")
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None
    active: bool = True


class ReminderUpdate(BaseModel):
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    times: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class ReminderResponse(BaseModel):
    id: str
    medicine_name: str
    dosage: str
    frequency: str
    times: list[str]
    start_date: date
    end_date: Optional[date]
    notes: Optional[str]
    active: bool
    created_at: str
