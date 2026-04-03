from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.module_05.hotel_service import HotelService
from app.schemas.intent import ConstraintObject

class HotelPlannerModule(BasePlannerModule):
    node_key: str = "L4_hotel"

    def __init__(self):
        self.service = HotelService()

    async def validate_input(self, state: PlanningState) -> bool:
        """L4 依赖于 L3 (景点) 已确认"""
        l3 = state.nodes.get("L3_attractions")
        return l3 is not None and l3.status in [NodeStatus.CONFIRMED]

    async def generate(self, state: PlanningState) -> dict:
        """基于景点分布和日期生成酒店推荐"""
        constraints = ConstraintObject(**state.constraints)
        l3_node = state.nodes.get("L3_attractions")
        attractions_data = l3_node.data
        
        # 提取确认的景点列表作为重心计算依据
        confirmed_attractions = attractions_data.get("confirmed_attractions", [])
        
        # 调用酒店推荐服务
        # 注意：get_hotel_recommendations 是异步的
        results = await self.service.get_hotel_recommendations(
            attractions=confirmed_attractions,
            check_in=constraints.departure_date,
            check_out=constraints.return_date,
            budget=float(constraints.preferences.budget.per_person or 1000)
        )
        
        return results.model_dump()
