from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
from .attraction import Coordinates

class PriceRange(BaseModel):
    min: float
    max: float
    currency: str = "CNY"

class RestaurantRecord(BaseModel):
    id: str
    name: Dict[str, str]  # {"zh": "...", "en": "..."}
    city: str
    coordinates: Coordinates
    address: str
    cuisine_type: List[str]
    avg_price_per_person: PriceRange
    established_year: int
    stability_rating: float = Field(..., ge=1, le=5)  # 1-5
    meal_periods: List[str]  # ["lunch", "dinner"]
    last_updated: str  # YYYY-MM-DD
    data_source: str
    description: Optional[str] = None
    confidence_level: str = "L4"

class SpecialtyDish(BaseModel):
    name: Dict[str, str]  # {"zh": "...", "en": "..."}
    description: str
    price_range: Optional[PriceRange] = None

class DiningEtiquette(BaseModel):
    title: str
    content: str

class DailyDiningPlan(BaseModel):
    day: int
    date: date
    classic_recommendations: List[RestaurantRecord] = Field(default_factory=list)
    popular_references: List[RestaurantRecord] = Field(default_factory=list)
    local_specialties: List[SpecialtyDish] = Field(default_factory=list)
    etiquette_tips: List[DiningEtiquette] = Field(default_factory=list)
    verification_reminder: str = "建议在大众点评 / Google Maps 核实最新营业状态后前往"

class DiningPlanState(BaseModel):
    daily_plans: List[DailyDiningPlan]
    confidence_level: str = "L4"
    last_updated: str
