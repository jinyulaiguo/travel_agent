from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.schemas.cost import CostSummaryResponse, ManualCostOverrideRequest
from app.services.cost_summary_service import CostSummaryService
from app.schemas.state import PlanningState, NodeStatus, NodeData

router = APIRouter(prefix="/api/v1/cost", tags=["Cost"])

# 依赖注入单例服务 (实际项目中可使用更加完善的 DI)
cost_service = CostSummaryService()

@router.get("/summary", response_model=CostSummaryResponse)
async def get_cost_summary(session_id: str):
    """
    获取当前行程的费用摘要汇总。
    """
    # 模拟从数据库或状态中央读取 PlanningState
    # 这里为了演示创建一个带 Mock 数据的 State
    mock_state = PlanningState(
        session_id=session_id,
        user_id="user_123",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        constraints={
            "available_days": 5,
            "travelers": {"total": 2}
        },
        nodes={
            "L1_flight": NodeData(
                status=NodeStatus.CONFIRMED,
                data={
                    "outbound": {"airline": "Air China", "price": 1200, "price_snapshot_time": datetime.now().isoformat()},
                    "inbound": {"airline": "Air China", "price": 1300, "price_snapshot_time": datetime.now().isoformat()},
                    "confidence_level": "L1"
                }
            ),
            "L4_hotel": NodeData(
                status=NodeStatus.CONFIRMED,
                data={
                    "selected_hotel": {
                        "name": "Chiang Mai Resort",
                        "price_per_night": 600,
                        "confidence_level": "L1",
                        "price_snapshot_time": datetime.now().isoformat()
                    }
                }
            ),
            "L3_attractions": NodeData(
                status=NodeStatus.CONFIRMED,
                data={
                    "confirmed_attractions": [
                        {"name": "Wat Phra That", "admission_fee": {"adult": 50}},
                        {"name": "Old City", "admission_fee": {"adult": 0}}
                    ]
                }
            )
        }
    )
    
    return await cost_service.aggregate_costs(mock_state)

@router.post("/override")
async def override_cost(request: ManualCostOverrideRequest):
    """
    手动录入/覆盖某项费用。
    """
    # 实际应更新后端存储
    return {"message": "Cost override applied successfully", "category": request.category}

@router.post("/refresh")
async def refresh_costs(session_id: str):
    """
    一键刷新所有过期的价格快照。
    """
    # 实际应触发各模块 API 重新获取
    return {"message": "Refreshing all snapshot prices", "session_id": session_id}
