from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.destination_service import DestinationService
from app.schemas.flight import FlightList, FlightAnchor
from app.schemas.intent import ConstraintObject

class DestinationPlannerModule(BasePlannerModule):
    node_key: str = "L2_destination"

    def __init__(self):
        self.service = DestinationService()

    async def validate_input(self, state: PlanningState) -> bool:
        """L2 依赖于 L1 (航班) 已确认"""
        l1 = state.nodes.get("L1_flight")
        return l1 is not None and l1.status in [NodeStatus.CONFIRMED]

    async def generate(self, state: PlanningState) -> dict:
        """生成目的地推荐方案"""
        constraints = ConstraintObject(**state.constraints)
        l1_node = state.nodes.get("L1_flight")
        
        # 1. 生成基于意图的推荐 (天数分配)
        recommendation = self.service.generate_recommendations(constraints)
        
        # 2. 如果 L1 确认了，计算时间限制（首日可用小时，末日截止时间）
        l1_data = l1_node.data
        if l1_data:
            from app.schemas.flight import FlightAnchor
            flight = FlightAnchor(**l1_data)
            available_hours, cutoff_time = self.service.calculate_time_constraints(flight)
        else:
            available_hours = 6.0
            cutoff_time = "20:00"
        
        # 返回推荐结果
        result = recommendation.model_dump()
        result.update({
            "first_day_available_hours": available_hours,
            "last_day_cutoff_time": cutoff_time
        })
        
        return result
