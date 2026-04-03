from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.itinerary_service import ItineraryService

class ItineraryPlannerModule(BasePlannerModule):
    node_key: str = "L5_itinerary"

    def __init__(self):
        # 注意：ItineraryService 内部可能需要 db session，
        # 我们在 generate 中根据需要传入。
        self.service = ItineraryService()

    async def validate_input(self, state: PlanningState) -> bool:
        """
        L5 汇聚节点，依赖 L3 (景点) 和 L4 (酒店) 均已确认。
        注：PRD 中 L3 和 L4 是并行的，L5 是它们的汇聚点。
        """
        l3 = state.nodes.get("L3_attractions")
        l4 = state.nodes.get("L4_hotel")
        return (
            l3 is not None and l3.status in [NodeStatus.CONFIRMED] and
            l4 is not None and l4.status in [NodeStatus.CONFIRMED]
        )

    async def generate(self, state: PlanningState) -> dict:
        """调用 ItineraryService 生成聚合后的行程单"""
        # generate_travel_plan 是异步方法
        plan = await self.service.generate_travel_plan(state)
        
        return plan.model_dump()
