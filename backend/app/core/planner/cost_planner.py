from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.cost_summary_service import CostSummaryService

class CostPlannerModule(BasePlannerModule):
    node_key: str = "L8_cost"

    def __init__(self):
        self.service = CostSummaryService()

    async def validate_input(self, state: PlanningState) -> bool:
        """
        L8 汇聚节点，理论上当行程 (L5) 确认后即可开始动态估算。
        不过为了数据完整性，通常在所有上游（L1-L7）有数据时计算。
        按 PRD 设计，它监听 L6 和 L7 的完成。
        """
        l6 = state.nodes.get("L6_transport")
        l7 = state.nodes.get("L7_dining")
        return (
            l6 is not None and l6.status in [NodeStatus.CONFIRMED] and
            l7 is not None and l7.status in [NodeStatus.CONFIRMED]
        )

    async def generate(self, state: PlanningState) -> dict:
        """调用 CostSummaryService 进行全量费用汇总"""
        results = await self.service.aggregate_costs(state)
        
        return results.model_dump()
