from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .attraction import Coordinates

class DailyItineraryItem(BaseModel):
    type: str = Field(..., description="Item type: 'attraction', 'fixed_slot', or 'buffer'")
    attraction_id: Optional[str] = None
    name: str = Field(..., description="Name of the attraction or notes for buffer/fixed_slot")
    planned_start_time: str = Field(..., description="Format: HH:MM")
    planned_end_time: str = Field(..., description="Format: HH:MM")
    duration_hours: float
    notes: Optional[str] = None

class DailyItineraryDay(BaseModel):
    day: int = Field(..., description="Day index starting from 1")
    date: date
    hotel_start_coordinates: Optional[Coordinates] = None
    items: List[DailyItineraryItem]
    total_active_hours: float
    has_conflicts: bool = False

class DailyItinerary(BaseModel):
    days: List[DailyItineraryDay]

class GenerateScheduleRequest(BaseModel):
    # This aligns the needed inputs for schedule generation based on previous modules.
    destination_cities: List[str]
    start_date: date
    end_date: date
    # Normally we would reference complex nested objects here.
    # For simplicity of API triggering, we can assume the generator fetches 
    # data from the state machine or database based on a journey/plan ID.
    plan_id: str

class AdjustScheduleRequest(BaseModel):
    plan_id: str
    itinerary: DailyItinerary
