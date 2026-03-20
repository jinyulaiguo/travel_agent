from pydantic import BaseModel, Field
from typing import List, Optional

class DestinationItem(BaseModel):
    city: str = Field(..., description="城市名称")
    country_code: str = Field(..., description="国家代码")
    lat: Optional[float] = Field(None, description="纬度")
    lng: Optional[float] = Field(None, description="经度")
    allocated_days: int = Field(..., description="建议游玩天数")
    recommend_reason: Optional[str] = Field(None, description="推荐理由")
    order: int = Field(0, description="游玩顺序，从0开始")

class DestinationConfig(BaseModel):
    confirmed_destinations: List[DestinationItem] = Field(..., description="确认的目的地列表")
    total_days: int = Field(..., description="总可用天数")
    first_day_available_hours: float = Field(..., description="首日实际可用时间（小时）")
    last_day_cutoff_time: str = Field(..., description="最后一天截止时间，格式 HH:MM")

class DestinationRecommendation(BaseModel):
    recommend_type: str = Field(..., description="建议游玩类型，例如: 推荐单城精华游")
    candidates: List[DestinationItem] = Field(..., description="系统推荐的候选目的地组合")

class DestinationConfirmRequest(BaseModel):
    destinations: List[DestinationItem] = Field(..., description="用户最终确认的目的地配置列表")
    force_override: bool = Field(False, description="是否强制覆盖并重算下游节点（用于已锁定时修改）")
