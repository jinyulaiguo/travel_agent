from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid

class Location(BaseModel):
    city: str = Field(description="城市名称")
    country: str = Field(description="国家名称")
    country_code: str = Field(description="国家代码(ISO 3166-1 alpha-2)")
    lat: Optional[float] = Field(None, description="纬度")
    lng: Optional[float] = Field(None, description="经度")

class Origin(BaseModel):
    city: str = Field(description="出发城市名称")
    country_code: str = Field(description="出发国家代码")

class Travelers(BaseModel):
    adults: int = Field(1, description="成人数")
    children: int = Field(0, description="儿童数")
    elderly: int = Field(0, description="老人数")
    total: int = Field(1, description="总人数")

class Budget(BaseModel):
    total: Optional[int] = Field(None, description="总预算")
    per_person: Optional[int] = Field(None, description="人均预算")
    currency: str = Field("CNY", description="货币单位，默认 CNY")

class Preferences(BaseModel):
    travel_style: List[str] = Field(
        default_factory=lambda: ["文化古迹", "自然风光"], 
        description="偏好标签，例如: 文化古迹, 自然风光, 美食, 购物, 休闲"
    )
    pace: Literal["relaxed", "moderate", "intensive"] = Field("moderate", description="行程节奏：轻松 / 适中 / 高强度")
    accommodation_tier: Literal["budget", "comfort", "luxury"] = Field("comfort", description="住宿档次：经济 / 舒适 / 豪华")
    budget: Budget = Field(default_factory=Budget)

class FixedTimeSlot(BaseModel):
    date: str = Field(description="日期 YYYY-MM-DD")
    start_time: str = Field(description="开始时间 HH:MM")
    end_time: str = Field(description="结束时间 HH:MM")
    description: str = Field(description="活动描述")

class MobilityConstraints(BaseModel):
    has_elderly: bool = Field(False, description="是否有老人")
    has_toddler: bool = Field(False, description="是否有幼儿")
    mobility_impaired: bool = Field(False, description="是否行动不便")
    wheelchair: bool = Field(False, description="是否需要轮椅")

class HardConstraints(BaseModel):
    fixed_timeslots: List[FixedTimeSlot] = Field(default_factory=list, description="固定时间点安排")
    excluded_attractions: List[str] = Field(default_factory=list, description="禁止景点或区域名称列表")
    mobility_constraints: MobilityConstraints = Field(default_factory=MobilityConstraints)

class ConstraintObject(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="规划会话唯一ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="创建时间")
    
    departure_date: Optional[str] = Field(None, description="出发日期 YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="返回日期 YYYY-MM-DD")
    available_days: Optional[int] = Field(None, description="可出行总天数")
    time_confidence: Optional[Literal["exact", "estimated"]] = Field(None, description="时间精确度")
    
    origin: Optional[Origin] = Field(None, description="出发地")
    destinations: List[Location] = Field(default_factory=list, description="目的地列表")
    is_multi_destination: bool = Field(False, description="是否多目的地")
    
    travelers: Travelers = Field(default_factory=Travelers)
    preferences: Preferences = Field(default_factory=Preferences)
    hard_constraints: HardConstraints = Field(default_factory=HardConstraints)
    
    default_fields_used: List[str] = Field(default_factory=list, description="记录哪些字段使用了默认值")
    
    turn_count: int = Field(0, description="追问轮次计数")
    is_confirmed: bool = Field(False, description="用户是否已最终确认")
    
    @model_validator(mode='after')
    def validate_dates_and_destinations(self) -> 'ConstraintObject':
        if self.departure_date and self.return_date:
            if self.return_date < self.departure_date:
                raise ValueError("return_date must be greater than or equal to departure_date")
        self.is_multi_destination = len(self.destinations) > 1
        return self

class IntentParseResult(BaseModel):
    updated_intent: ConstraintObject
    requires_clarification: bool = Field(False, description="是否需要进一步澄清/追问")
    clarification_message: Optional[str] = Field(None, description="给用户的追问或提示信息")
