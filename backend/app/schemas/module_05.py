from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Coordinates(BaseModel):
    lat: float
    lng: float

class HotelRecord(BaseModel):
    hotel_id: str
    name: str
    area: str
    coordinates: Coordinates
    price_per_night: float
    price_snapshot_time: datetime
    ota_rating: float
    ota_source: str
    distance_to_cluster_center_km: float
    booking_url: str
    confidence_level: str = "L1" # L1, L2, L5
    is_locked: bool = False
    is_manual_input: bool = False
    amenities: List[str] = Field(default_factory=list)
    rationale: Optional[str] = None

class HotelSelection(BaseModel):
    selected_hotel: Optional[HotelRecord] = None
    alternatives: List[HotelRecord] = Field(default_factory=list)
    recommended_area: str
    area_rationale: str
