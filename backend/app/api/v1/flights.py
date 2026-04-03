from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.flight import FlightSearchRequest, FlightList, FlightAnchor
from app.services.flight import FlightService
from app.services.state_service import StateService
from app.adapters.base import ConfidenceLevel

router = APIRouter(tags=["flights"])
flight_service = FlightService()

@router.post("/search", response_model=FlightList)
async def search_flights(request: FlightSearchRequest):
    """
    搜索航班接口，带有超时和自动降级
    """
    try:
        results = await flight_service.search_flights(
            origin=request.origin,
            destination=request.destination,
            date=request.date,
            passengers=request.passengers,
            return_date=request.return_date
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anchor/confirm", response_model=FlightAnchor)
async def confirm_flight(
    anchor: FlightAnchor,
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    确认航班信息并持久化到 PlanningState (L1节点)。
    """
    await StateService.confirm_node(db, session_id, user_id, "L1_flight", anchor.model_dump(mode='json'))
    return anchor

@router.post("/anchor/manual", response_model=FlightAnchor)
async def create_manual_anchor(
    anchor_data: FlightAnchor,
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    航班信息手动录入（API降级）与确认接口。
    标记为 LOCKED 状态及 L5 置信度。
    """
    anchor_data.is_locked = True
    anchor_data.confidence_level = ConfidenceLevel.L5_ESTIMATE
    
    anchor_data.outbound.is_manual_input = True
    if anchor_data.inbound:
        anchor_data.inbound.is_manual_input = True
        
    # 持久化逻辑
    await StateService.lock_node(db, session_id, user_id, "L1_flight")
    await StateService.confirm_node(db, session_id, user_id, "L1_flight", anchor_data.model_dump(mode='json'))
    
    return anchor_data
