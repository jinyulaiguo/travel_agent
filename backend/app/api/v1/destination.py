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

router = APIRouter(prefix="/api/v1/destination", tags=["destination"])

# Temporary wrapper for stateless API tests until a DB is integrated
class RecommendationRequest(BaseModel):
    intent: ConstraintObject
    flight: Optional[FlightAnchor] = None

class ConfirmRequestWrapper(BaseModel):
    request_data: DestinationConfirmRequest
    flight: FlightAnchor
    state: PlanningState

@router.post("/recommend", response_model=DestinationRecommendation)
async def get_recommendations(req: RecommendationRequest):
    """
    根据给定的意图和可选的航班信息，生成目的地游玩建议
    """
    try:
        recommendations = destination_service.generate_recommendations(req.intent)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm", response_model=DestinationConfig)
async def confirm_destination(req: ConfirmRequestWrapper):
    """
    确认目的地配置。
    需传入用户确定的目的地、航班锚点以及当前系统状态，从而验证状态机依赖并锁定L2节点。
    """
    try:
        config = destination_service.lock_destination(
            request=req.request_data,
            flight=req.flight,
            state=req.state
        )
        return config
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
