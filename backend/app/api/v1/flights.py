from fastapi import APIRouter, HTTPException
from app.schemas.flight import FlightSearchRequest, FlightList, FlightAnchor
from app.services.flight import FlightService
from app.adapters.base import ConfidenceLevel

router = APIRouter(prefix="/api/v1/flights", tags=["flights"])
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
            passengers=request.passengers
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anchor/manual", response_model=FlightAnchor)
async def create_manual_anchor(anchor_data: FlightAnchor):
    """
    航班信息手动录入（API降级）与确认接口。
    标记为 LOCKED 状态及 L5 置信度。
    """
    anchor_data.is_locked = True
    anchor_data.confidence_level = ConfidenceLevel.L5_ESTIMATE
    
    anchor_data.outbound.is_manual_input = True
    if anchor_data.inbound:
        anchor_data.inbound.is_manual_input = True
        
    # TODO: 锚点持久化逻辑入库 (例如存入 ConstraintObject / 行程DB)
    
    return anchor_data
