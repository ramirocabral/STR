from typing import List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    instances: Optional[List[List[float]]] = None

    date: Optional[str] = Field(
        None, description="Timestamp ISO8601, e.g., '2025-03-10T03:00Z'"
    )
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rain: Optional[float] = None
    snow: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    clouds: Optional[float] = None
    sunrise: Optional[int] = None
    sunset: Optional[int] = None
    working_day: Optional[bool] = None
    holiday: Optional[bool] = None

