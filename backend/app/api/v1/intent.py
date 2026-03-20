from fastapi import APIRouter, HTTPException, Depends
from app.schemas.intent import ConstraintObject, IntentParseResult
from app.services.intent_parser_service import IntentParserService
from typing import Optional

router = APIRouter(prefix="/intent", tags=["intent"])

# 本处通过依赖注入模拟 Service 实力的获取
def get_intent_service():
    return IntentParserService()

@router.post("/parse", response_model=IntentParseResult)
async def parse_intent(
    user_text: str,
    current_intent: Optional[ConstraintObject] = None,
    service: IntentParserService = Depends(get_intent_service)
):
    """
    意图解析与澄清接口 (功能 1-1 to 1-4)
    通过自然语言输入实时提取意图，并返回是否需要追问。
    """
    result = await service.parse_user_input(user_text, current_intent)
    return result

@router.post("/confirm", response_model=ConstraintObject)
async def confirm_intent(
    intent: ConstraintObject,
    service: IntentParserService = Depends(get_intent_service)
):
    """
    意图确认接口 (功能 1-5)
    锁定意图，将其标记为 CONFIRMED。
    """
    confirmed = await service.confirm_intent(intent)
    return confirmed
