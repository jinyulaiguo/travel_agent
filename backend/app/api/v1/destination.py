from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from app.schemas.flight import FlightAnchor
from app.schemas.intent import ConstraintObject
from app.schemas.destination import (
    DestinationRecommendation,
    DestinationConfirmRequest,
    DestinationConfig
)
from app.services.destination_service import destination_service
from app.schemas.state import PlanningState

from app.services.state_service import StateService
from app.api import deps
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["destination"])

class RecommendationRequest(BaseModel):
    session_id: str
    user_id: str = "default_user"

@router.post("/recommend", response_model=DestinationRecommendation)
async def get_recommendations(
    req: RecommendationRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    根据给定的意图生成目的地游玩建议
    """
    try:
        state = await StateService.get_state(db, req.session_id, req.user_id)
        if not state.constraints:
             raise HTTPException(status_code=400, detail="意图未初始化")
        
        constraints = ConstraintObject(**state.constraints)
        recommendations = destination_service.generate_recommendations(constraints)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm", response_model=DestinationConfig)
async def confirm_destination(
    request_data: DestinationConfirmRequest,
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    确认目的地配置。
    需传入用户确定的目的地，并锁定L2节点。
    """
    try:
        state = await StateService.get_state(db, session_id, user_id)
        
        # 获取 L1 航班锚点
        l1_node = state.nodes.get("L1_flight")
        if not l1_node or not l1_node.data:
            raise HTTPException(status_code=400, detail="请先确认航班信息 (L1)")
            
        flight = FlightAnchor(**l1_node.data)
        
        config = destination_service.lock_destination(
            request=request_data,
            flight=flight,
            state=state
        )
        
        # 持久化到状态机
        await StateService.confirm_node(db, session_id, user_id, "L2_destination", config.model_dump(mode='json'))
        
        return config
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
