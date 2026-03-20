from fastapi import APIRouter, Depends, HTTPException
from app.schemas.daily_schedule import DailyItinerary, GenerateScheduleRequest, AdjustScheduleRequest
from app.services.daily_schedule_service import daily_schedule_service

router = APIRouter()

@router.post("/generate", response_model=DailyItinerary, summary="自动生成每日行程 (L5)")
async def generate_schedule(request: GenerateScheduleRequest):
    """
    根据确定的景点、时间和约束条件，自动分配每日游览时间轴。
    如果超出单日建议时长，多出景点会挪至次日。
    """
    try:
        itinerary = daily_schedule_service.generate_schedule(request)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/adjust", response_model=DailyItinerary, summary="手动调整每日行程 (L5)")
async def adjust_schedule(request: AdjustScheduleRequest):
    """
    用户手动拖拽调整后的行程提交接口。
    会覆盖原有结果，并在内部状态机标志后续 L6(交通)、L8(费用) 模块信息过期。
    """
    try:
        new_itinerary = daily_schedule_service.adjust_schedule(request)
        return new_itinerary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
