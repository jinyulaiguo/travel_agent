from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.daily_schedule import DailyItinerary, GenerateScheduleRequest, AdjustScheduleRequest
from app.services.daily_schedule_service import daily_schedule_service

router = APIRouter()

@router.post("/generate", response_model=DailyItinerary, summary="自动生成每日行程 (L5)")
async def generate_schedule(request: GenerateScheduleRequest, db: AsyncSession = Depends(deps.get_db)):
    """
    根据确定的景点、时间和约束条件，自动分配每日游览时间轴。
    """
    try:
        itinerary = await daily_schedule_service.generate_schedule(db, request)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/adjust", response_model=DailyItinerary, summary="手动调整每日行程 (L5)")
async def adjust_schedule(request: AdjustScheduleRequest, db: AsyncSession = Depends(deps.get_db)):
    """
    用户手动拖拽调整后的行程提交接口。
    """
    try:
        new_itinerary = await daily_schedule_service.adjust_schedule(db, request)
        return new_itinerary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
