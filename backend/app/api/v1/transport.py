from fastapi import APIRouter, HTTPException
from typing import List
from ...schemas.transport import TransportPlan, TransportRequest, DailyTransportPlan
from ...services.transport import TransportService

router = APIRouter()
transport_service = TransportService()

@router.post("/plan", response_model=TransportPlan, summary="为每日行程规划境内交通 (L6)")
async def plan_transport(request: TransportRequest):
    """
    根据每日地点的坐标序列集合，自动生成分段交通方案和费用估算。
    """
    try:
        daily_plans = []
        total_min = 0.0
        total_max = 0.0
        
        for daily_req in request.daily_requests:
            # Convert LocationPoint objects to dictionaries
            locs = [{"name": l.name, "coords": l.coords} for l in daily_req.locations]
            
            day_plan = transport_service.plan_daily_transport(
                day_number=daily_req.day_number,
                locations=locs,
                hotel_coords=daily_req.hotel_coords
            )
            daily_plans.append(day_plan)
            total_min += day_plan.total_estimated_cost_min
            total_max += day_plan.total_estimated_cost_max
            
        return TransportPlan(
            daily_plans=daily_plans,
            total_cost_min=total_min,
            total_cost_max=total_max,
            currency="THB"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"交通规划失败: {str(e)}")
