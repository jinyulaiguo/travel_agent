from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any

class Coordinates(BaseModel):
    lat: float
    lng: float

class AdmissionFee(BaseModel):
    adult: float
    child: float
    currency: str

class OpeningHours(BaseModel):
    # Simplified format: {"mon-sun": {"open": "HH:MM", "close": "HH:MM"}} or "closed"
    # To handle flexible keys and values, we can use Dict[str, Union[Dict[str, str], str]]
    hours: Dict[str, Union[Dict[str, str], str]]

class AttractionRecord(BaseModel):
    id: str
    name: Dict[str, str]  # {"zh": "名称", "en": "Name"}
    city: str
    country_code: str
    coordinates: Coordinates
    suggested_duration_hours: float
    opening_hours: Dict[str, Union[Dict[str, str], str]]
    admission_fee: AdmissionFee
    crowd_index: int = Field(..., ge=1, le=5)
    attraction_tags: List[str]
    suitable_for: List[str]
    notes: str
    last_updated: str
    data_source: str
    confidence_level: str = "L4"

class ConfirmedAttraction(BaseModel):
    attraction_id: str
    name: str  # Display name
    cluster_id: Optional[int] = None
    suggested_duration_hours: float
    coordinates: Coordinates
    attraction_tags: List[str] = Field(default_factory=list)
    opening_hours: Dict[str, Any] = Field(default_factory=dict)
    confidence_level: str = "L4"
    last_updated: str
    is_custom: bool = False

class AttractionList(BaseModel):
    confirmed_attractions: List[ConfirmedAttraction]
    total_estimated_hours: float

class AttractionRecommendationRequest(BaseModel):
    cities: List[str]
    available_days: int
    travel_style: List[str]
