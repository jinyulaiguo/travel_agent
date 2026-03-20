from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

class ItemType(str, Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    HOTEL = "hotel"
    DINING = "dining"
    SIGHTSEEING = "sightseeing"
    TRANSPORT = "transport"
    OTHER = "other"

from app.schemas.confidence import ConfidenceLevel, ConfidenceWrapper

class ItemType(str, Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    HOTEL = "hotel"
    DINING = "dining"
    SIGHTSEEING = "sightseeing"
    TRANSPORT = "transport"
    OTHER = "other"

class AlternativeOption(BaseModel):
    id: str = Field(..., description="Unique ID for the alternative option")
    name: str = Field(..., description="Name or title of the alternative")
    cost_estimate: Optional[ConfidenceWrapper[float]] = Field(None, description="Estimated cost")
    currency: Optional[str] = Field("CNY", description="Currency code")
    difference_summary: Optional[str] = Field(None, description="Summary of difference from main option")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Module specific metadata")

class ItineraryItem(BaseModel):
    id: str = Field(..., description="Unique ID for the itinerary item")
    type: ItemType = Field(..., description="Type of the item")
    name: str = Field(..., description="Name of the activity or place")
    description: Optional[str] = Field(None, description="Detailed description")
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    duration_minutes: Optional[ConfidenceWrapper[int]] = Field(None, description="Estimated duration in minutes")
    
    # Cost related
    cost_estimate: Optional[ConfidenceWrapper[float]] = Field(None, description="Base cost estimate")
    currency: Optional[str] = Field("CNY", description="Currency code")
    confidence_level: ConfidenceLevel = Field(ConfidenceLevel.L4, description="Confidence of the item data")
    
    # Other details
    location: Optional[str] = Field(None, description="Location name or address")
    booking_url: Optional[str] = Field(None, description="Associated booking link if any")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Module specific metadata")
    
    alternatives: List[AlternativeOption] = Field(default_factory=list, description="List of max 2 alternative options")

class DailyItinerary(BaseModel):
    date: date = Field(..., description="Date of this itinerary")
    day_number: int = Field(..., description="Day index (1-based)")
    items: List[ItineraryItem] = Field(default_factory=list, description="Items ordered by time")
    daily_cost_summary: Optional[Dict[str, float]] = Field(default_factory=dict, description="Cost summary for the day per currency")

class TravelPlan(BaseModel):
    plan_id: str = Field(..., description="ID of the travel state machine / context")
    destination: str = Field(..., description="Main destination")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    
    overview: Optional[str] = Field(None, description="Brief trip overview")
    important_reminders: List[str] = Field(default_factory=list, description="Visa, weather, packing reminders etc.")
    
    daily_itineraries: List[DailyItinerary] = Field(default_factory=list, description="Day by day breakdown")
    total_cost_summary: Optional[Dict[str, float]] = Field(default_factory=dict, description="Total aggregated costs")
    
    disclaimer: str = Field(
        "价格信息为查询时快照，实际以平台下单价格为准。景点开放时间以景点官方公告为准。签证及入境政策请前往官方渠道核实，本系统不提供签证建议。",
        description="Fixed disclaimer"
    )

class ReplaceOptionRequest(BaseModel):
    alternative_id: str = Field(..., description="The ID of the alternative option to replace the main item")

class ShareLinkCreate(BaseModel):
    expires_in_days: int = Field(30, description="Validity period in days")

class ShareLinkResponse(BaseModel):
    token: str = Field(..., description="The unique share token")
    share_url: str = Field(..., description="Full URL to access the shared plan")
    expires_at: datetime = Field(..., description="Expiration timestamp")
