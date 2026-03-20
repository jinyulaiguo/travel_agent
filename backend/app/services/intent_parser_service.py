import os
import json
from datetime import datetime, timezone
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.schemas.intent import ConstraintObject, IntentParseResult
from app.config import settings

class IntentParserService:
    """
    意图解析服务
    基于 DeepSeek 进行意图的解析和结构化抽取
    """
    def __init__(self):
        # 从统一个配置项读取
        self.llm = ChatOpenAI(
            model="deepseek-chat", 
            api_key=settings.DEEPSEEK_API_KEY or "sk-dummy", 
            base_url=settings.DEEPSEEK_BASE_URL,
            max_retries=2,
            temperature=0.0
        )
        self.structured_llm = self.llm.with_structured_output(IntentParseResult)

    async def parse_user_input(
        self, 
        user_text: str, 
        current_intent: Optional[ConstraintObject] = None
    ) -> IntentParseResult:
        if current_intent is None:
            current_intent = ConstraintObject()
            
        current_intent.turn_count += 1
        
        current_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        system_prompt = f"""
你是一个专业的旅游规划助手，负责将用户的自然语言输入转化为结构化的出行意图约束对象(ConstraintObject)。
当前时间是：{current_date_str}

规则：
1. 提取时间信息（如：五一，下周末等），并考虑冲突情况（如返回早于出发则清空并追问）。尽量转化为YYYY-MM-DD格式。
2. 提取目的地信息（包括城市、国家），支持多目的地解析。
3. 提取偏好信息（风格、节奏、住宿、预算、人数）。如果用户未提及且当前意图也没包含，则尝试推测，无从推测时给予合理默认值（总预算无限制可为 null）。
4. 提取特殊约束（例如：带轮椅、行动受限）。如果涉及特殊要求，务必体现在 hard_constraints。
5. 检查关键信息是否缺失（主要是出发日期/天数，以及目的地）。
    - 如果缺失且 turn_count <= 2，请设置 requires_clarification=true，并在 clarification_message 中友好提问。
    - 如果轮次 turn_count >= 3 仍缺失，请主动采用安全的默认值（例如默认5天，或随便推荐一个目的地），并在 clarification_message 告知用户，此时 requires_clarification=false。
"""
        
        human_prompt = f"""
当前的意图状态(JSON格式):
{current_intent.model_dump_json(exclude_none=True)}

当前的轮次(turn_count): {current_intent.turn_count}

用户的最新输入:
"{user_text}"

请基于以上状态和用户输入，输出更新后的 IntentParseResult。
注意：请结合最新的用户输入全量更新意图字段，如果有缺失的信息可以向用户追问。
"""
        
        try:
            # 调用 DeepSeek 的 Structured Output
            result: IntentParseResult = await self.structured_llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            
            # 保护 session_id 和 turn_count, 防止大模型篡改
            result.updated_intent.turn_count = current_intent.turn_count
            result.updated_intent.session_id = current_intent.session_id
            
            return result
        except Exception as e:
            # 出错时降级处理
            return IntentParseResult(
                updated_intent=current_intent,
                requires_clarification=True,
                clarification_message=f"抱歉，我暂时无法处理您的请求。原因: {str(e)}"
            )

    async def confirm_intent(self, intent: ConstraintObject) -> ConstraintObject:
        """最终确认意图"""
        intent.is_confirmed = True
        return intent
