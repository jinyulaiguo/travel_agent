from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from app.schemas.confidence import ConfidenceLevel, ConfidenceWrapper

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
    suggested_duration_hours: ConfidenceWrapper[float]
    opening_hours: ConfidenceWrapper[Dict[str, Union[Dict[str, str], str]]]
    admission_fee: ConfidenceWrapper[AdmissionFee]
    crowd_index: ConfidenceWrapper[int] = Field(..., description="1-5")
    attraction_tags: List[str]
    suitable_for: List[str]
    notes: str
    last_updated: str
    data_source: str
    confidence_level: ConfidenceLevel = ConfidenceLevel.L4

class ConfirmedAttraction(BaseModel):
    attraction_id: str
    name: str  # Display name
    cluster_id: Optional[int] = None
    suggested_duration_hours: ConfidenceWrapper[float]
    coordinates: Coordinates
    attraction_tags: List[str] = Field(default_factory=list)
    opening_hours: ConfidenceWrapper[Dict[str, Any]]
    confidence_level: ConfidenceLevel = ConfidenceLevel.L4
    last_updated: str
    is_custom: bool = False

class AttractionList(BaseModel):
    confirmed_attractions: List[ConfirmedAttraction]
    total_estimated_hours: float

class AttractionRecommendationRequest(BaseModel):
    cities: List[str]
    available_days: int
    travel_style: List[str]
