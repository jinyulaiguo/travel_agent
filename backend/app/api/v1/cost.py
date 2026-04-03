from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.schemas.cost import CostSummaryResponse, ManualCostOverrideRequest
from app.services.cost_summary_service import CostSummaryService
from app.schemas.state import PlanningState, NodeStatus, NodeData
from app.api import deps
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.state_service import StateService

router = APIRouter(tags=["cost"])

# 依赖注入单例服务 (实际项目中可使用更加完善的 DI)
cost_service = CostSummaryService()

@router.get("/summary", response_model=CostSummaryResponse)
async def get_cost_summary(
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    获取当前行程的费用摘要汇总。
    """
    state = await StateService.get_state(db, session_id, user_id)
    return await cost_service.aggregate_costs(state)

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
