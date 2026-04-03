from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.confidence import ConfidenceLevel, ConfidenceWrapper

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="出发地国家/城市代码，如 BJS")
    destination: str = Field(..., description="目的地国家/城市代码，如 TYO")
    date: str = Field(..., description="出发日期，格式 YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="返程日期，格式 YYYY-MM-DD，为空则是单程")
    passengers: int = Field(1, description="乘机总人数")

class FlightSegment(BaseModel):
    flight_id: str
    flight_no: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int
    transfer_cities: List[str] = []
    price: float
    price_snapshot_time: Optional[datetime] = None
    on_time_rate_30d: float = Field(..., description="近30天准点率，如 0.95")
    airline: str
    transport_type: str = Field("flight", description="交通方式(flight, train等)")
    ota_source: Optional[str] = Field("携程", description="数据来源(携程/12306/去哪儿/飞猪)")
    is_manual_input: bool = False

class FlightCandidate(FlightSegment):
    total_score: float = Field(0.0, description="综合评分")
    recommend_reason: Optional[str] = Field(None, description="推荐理由，不超过15字")

class FlightList(BaseModel):
    candidates: List[FlightCandidate] = []
    visa_reminder_shown: bool = False
    is_fallback: bool = False
    fallback_message: Optional[str] = None

class FlightAnchor(BaseModel):
    outbound: FlightSegment
    inbound: Optional[FlightSegment] = None
    is_locked: bool = False
    confidence_level: ConfidenceLevel = ConfidenceLevel.L1_REALTIME
    visa_reminder_shown: bool = False
