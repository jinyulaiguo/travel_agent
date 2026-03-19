from enum import Enum
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

class NodeStatus(str, Enum):
    PENDING = "pending"       # 待生成
    GENERATING = "generating" # 生成中
    GENERATED = "generated"   # 已生成，等待确认
    CONFIRMED = "confirmed"   # 用户已确认，节点固化
    REJECTED = "rejected"     # 用户否决，待重算
    STALE = "stale"           # 上游变更，需重算
    LOCKED = "locked"         # 用户锁定，不受上游影响
    SKIPPED = "skipped"       # 用户跳过

class NodeData(BaseModel):
    status: NodeStatus = NodeStatus.PENDING
    data: dict[str, Any] | None = None          # 模块输出的结构化数据
    confirmed_at: datetime | None = None
    locked: bool = False
    snapshots: list[dict] = Field(default_factory=list) # 历史快照，支持回滚

class PlanningState(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    # 根约束（L0 输出）
    constraints: dict[str, Any] | None = None
    # 各节点状态
    nodes: dict[str, NodeData] = Field(default_factory=lambda: {
        "L0_intent": NodeData(),
        "L1_flight": NodeData(),
        "L2_destination": NodeData(),
        "L3_attractions": NodeData(),
        "L4_hotel": NodeData(),
        "L5_itinerary": NodeData(),
        "L6_transport": NodeData(),
        "L7_dining": NodeData(),
        "L8_cost": NodeData(),
        "L9_export": NodeData(),
    })
