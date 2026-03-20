from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Any
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.itinerary import (
    TravelPlan, ShareLinkCreate, ShareLinkResponse, ReplaceOptionRequest
)
from app.services.itinerary_service import ItineraryService
# 假设状态管理在核心模块，下面使用一个桩代码模拟获取状态
# from app.core.state_manager import StateManager

router = APIRouter()

# 模拟获状态对象的依赖注入
async def get_planning_state(plan_id: str):
    # 这里应从数据库/Redis读取状态
    from app.schemas.state import PlanningState
    return PlanningState(plan_id=plan_id, current_node="L9_output", nodes={})

@router.get("/{plan_id}", response_model=TravelPlan, summary="获取完整行程单")
async def get_travel_plan(plan_id: str, state=Depends(get_planning_state)):
    if not state:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    service = ItineraryService()
    plan = await service.generate_travel_plan(state)
    return plan

@router.post("/{plan_id}/share", response_model=ShareLinkResponse, summary="生成只读分享链接")
async def create_share_link(
    plan_id: str, 
    req: ShareLinkCreate, 
    db: Session = Depends(get_db)
):
    service = ItineraryService(db)
    return service.create_share_link(plan_id, req)

@router.get("/share/{token}", response_model=TravelPlan, summary="通过分享口令获取只读行程单")
async def view_shared_plan(token: str, db: Session = Depends(get_db)):
    service = ItineraryService(db)
    # 此处假设直接调用内部查询。有效的话会得到 plan_id
    plan_id = service.get_plan_id_by_token(token)
    if not plan_id:
        raise HTTPException(status_code=404, detail="Share token invalid or expired")
    
    # 模拟获取 state，然后查数据（应当实现成复用逻辑）
    from app.schemas.state import PlanningState
    state = PlanningState(plan_id=plan_id, current_node="L9_output", nodes={})
    return await service.generate_travel_plan(state)

@router.post("/{plan_id}/items/{item_id}/replace", summary="备选方案替换")
async def replace_alternative(
    plan_id: str, 
    item_id: str, 
    req: ReplaceOptionRequest,
    state=Depends(get_planning_state)
):
    service = ItineraryService()
    success = await service.replace_alternative(state, item_id, req.alternative_id)
    if not success:
        raise HTTPException(status_code=400, detail="Replace failed")
    
    return {"message": "Alternative replaced and downstream nodes stale propagated"}

@router.get("/{plan_id}/pdf", summary="导出 PDF")
async def export_pdf(plan_id: str, state=Depends(get_planning_state)):
    service = ItineraryService()
    plan = await service.generate_travel_plan(state)
    
    # 这里应当使用真实的 WeasyPrint 生成字节
    pdf_bytes = service.generate_pdf_bytes(plan)
    
    if pdf_bytes == b"WeasyPrint required but not installed.":
        # 由于开发环境可能未安装该库，暂返回明文
        return Response(content=pdf_bytes, media_type="text/plain")
        
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={plan_id}_travel_plan.pdf"}
    )
