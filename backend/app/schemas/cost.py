from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.adapters.base import ConfidenceLevel

class CostCategory(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    ADMISSION = "admission"
    TRANSPORT = "transport"
    DINING = "dining"
    MISC = "misc"

class CostItem(BaseModel):
    category: CostCategory = Field(..., description="费用类别")
    source_module: str = Field(..., description="来源模块名称")
    amount_min: float = Field(..., description="费用下限（原币种）")
    amount_max: float = Field(..., description="费用上限（原币种）")
    currency: str = Field("CNY", description="原币种代码，如 CNY, THB, USD")
    converted_amount_min_cny: float = Field(..., description="折算后人民币下限")
    converted_amount_max_cny: float = Field(..., description="折算后人民币上限")
    confidence: ConfidenceLevel = Field(..., description="置信度级别")
    snapshot_time: Optional[datetime] = Field(None, description="价格快照时间")
    is_manual_override: bool = Field(False, description="是否为用户手动录入覆盖")
    expired_warning: bool = Field(False, description="是否快照已过期（超过30分钟）")
    description: Optional[str] = Field(None, description="费用项描述，如 '机票往返', '酒店3晚'")

class CostSummaryResponse(BaseModel):
    items: List[CostItem] = Field(..., description="各项费用详情列表")
    total_min_cny: float = Field(..., description="总费用估算下限 (CNY)")
    total_max_cny: float = Field(..., description="总费用估算上限 (CNY)")
    confirmed_cny: float = Field(..., description="已快照确认的实时金额 (CNY)")
    summary_text: str = Field(..., description="格式化的汇总文案，如 '预计 ¥8,000 ～ ¥12,000，其中已快照确认 ¥5,000'")
    currency_rates: dict = Field(default_factory=dict, description="涉及到的汇率参考，如 {'THB': 0.203}")
    updated_at: datetime = Field(default_factory=datetime.now, description="汇总更新时间")

class ManualCostOverrideRequest(BaseModel):
    category: CostCategory
    actual_amount: float = Field(..., description="用户录入的实际花费")
    currency: str = Field("CNY", description="录入时的币种")
