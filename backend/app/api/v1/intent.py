from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.intent import ConstraintObject, IntentParseResult, IntentParseRequest
from app.services.intent_parser_service import IntentParserService
from typing import Optional

router = APIRouter(tags=["intent"])

# 本处通过依赖注入模拟 Service 实力的获取
def get_intent_service():
    return IntentParserService()

@router.post("/parse", response_model=IntentParseResult)
async def parse_intent(
    request: IntentParseRequest,
    service: IntentParserService = Depends(get_intent_service)
):
    """
    意图解析与澄清接口 (功能 1-1 to 1-4)
    通过自然语言输入实时提取意图，并返回是否需要追问。
    """
    result = await service.parse_user_input(request.user_text, request.current_intent)
    return result

@router.post("/confirm", response_model=ConstraintObject)
async def confirm_intent(
    intent: ConstraintObject,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db),
    service: IntentParserService = Depends(get_intent_service)
):
    """
    意图确认接口 (功能 1-5)
    锁定意图，将其标记为 CONFIRMED，并持久化到 PlanningState。
    """
    # 兼容前端不传 query param 的情况，从 body 中提取 session_id
    id_to_use = session_id or intent.session_id
    user_id_to_use = user_id or "default_user"
    
    if not id_to_use:
        raise HTTPException(status_code=400, detail="session_id is required")
        
    confirmed = await service.confirm_intent(intent, db, id_to_use, user_id_to_use)
    return confirmed
