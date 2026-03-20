from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TransportMode(str, Enum):
    WALKING = "walking"
    TRANSIT = "transit"
    DRIVING = "driving"
    GRAB = "grab"
    SHUTTLE = "shuttle"
    CHARTER = "charter"
    MOPED_TUKTUK = "moped_tuktuk"

class TransportSegment(BaseModel):
    origin: str = Field(..., description="Starting point name")
    destination: str = Field(..., description="Destination point name")
    origin_coords: Optional[str] = Field(None, description="Coordinates of origin (lat,lng)")
    destination_coords: Optional[str] = Field(None, description="Coordinates of destination (lat,lng)")
    distance_km: float = Field(..., description="Estimated distance in kilometers")
    duration_minutes: float = Field(..., description="Estimated duration in minutes")
    recommended_mode: TransportMode = Field(..., description="Recommended transport mode")
    alternative_mode: Optional[TransportMode] = Field(None, description="Alternative transport mode")
    price_estimate_min: float = Field(0.0, description="Minimum price estimate")
    price_estimate_max: float = Field(0.0, description="Maximum price estimate")
    currency: str = Field("THB", description="Currency for price estimate")
    reliability_level: str = Field("L5", description="Reliability level of data (L3/L5)")
    instruction: str = Field(..., description="Human-readable instruction")
    warning: Optional[str] = Field(None, description="Important note or warning")

class DailyTransportPlan(BaseModel):
    day_number: int
    segments: List[TransportSegment]
    total_estimated_cost_min: float
    total_estimated_cost_max: float
    currency: str = "THB"

class TransportPlan(BaseModel):
    daily_plans: List[DailyTransportPlan]
    total_cost_min: float
    total_cost_max: float
    currency: str = "THB"

class LocationPoint(BaseModel):
    name: str
    coords: Optional[str] = None

class DailyTransportRequest(BaseModel):
    day_number: int
    locations: List[LocationPoint]
    hotel_coords: Optional[str] = None

class TransportRequest(BaseModel):
    daily_requests: List[DailyTransportRequest]
