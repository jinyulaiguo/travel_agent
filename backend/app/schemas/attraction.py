from pydantic import BaseModel, Field, model_validator, BeforeValidator
from typing import List, Dict, Optional, Union, Any, Annotated, TypeVar
from app.schemas.confidence import ConfidenceLevel, ConfidenceWrapper
import sys

class Coordinates(BaseModel):
    lat: float
    lng: float

class AdmissionFee(BaseModel):
    adult: float
    child: float
    currency: str

class OpeningHours(BaseModel):
    hours: Dict[str, Union[Dict[str, str], str]]

class AttractionRecord(BaseModel):
    id: str
    name: Dict[str, str]
    city: str
    country_code: str
    coordinates: Coordinates
    suggested_duration_hours: float
    opening_hours: Dict[str, Any]
    admission_fee: AdmissionFee
    crowd_index: int = Field(..., description="1-5")
    attraction_tags: List[str]
    suitable_for: List[str]
    notes: str
    last_updated: str
    data_source: str
    confidence_level: ConfidenceLevel = ConfidenceLevel.L4

class ConfirmedAttraction(BaseModel):
    attraction_id: str
    name: str
    cluster_id: Optional[int] = None
    suggested_duration_hours: float
    coordinates: Coordinates
    attraction_tags: List[str] = Field(default_factory=list)
    opening_hours: Dict[str, Any]
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
