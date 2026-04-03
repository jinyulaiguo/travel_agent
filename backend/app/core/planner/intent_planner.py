from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.intent_parser_service import IntentParserService
from app.schemas.intent import ConstraintObject, IntentParseResult

class IntentPlannerModule(BasePlannerModule):
    node_key: str = "L0_intent"

    def __init__(self):
        self.service = IntentParserService()

    async def validate_input(self, state: PlanningState) -> bool:
        """L0 是根节点，始终可以执行，但通常它依赖于初始的 user_text"""
        # 如果已经有确认的意图，通常不需要重新生成，除非被标记为 REJECTED 或 STALE
        return True

    async def generate(self, state: PlanningState) -> dict:
        """
        L0 意图解析节点实现。
        注意：在 SSE 流运行模式下，L0 通常已经由 /intent/confirm 固化。
        如果流程运行到这里，我们确保它处于有效状态。
        """
        node = state.nodes.get(self.node_key)
        
        # 如果 constraints 已经存在且被确认，直接返回
        if state.constraints and node and node.status == NodeStatus.CONFIRMED:
            return node.data or {}

        # 实际上，在当前的架构中，L0 的意图解析是在对话阶段完成的。
        # 这里的 generate 更多是作为状态机节点的闭环。
        if not state.constraints:
            return {}
            
        return state.constraints
