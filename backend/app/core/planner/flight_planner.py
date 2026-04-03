from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.flight import FlightService
from app.schemas.intent import ConstraintObject

class FlightPlannerModule(BasePlannerModule):
    node_key: str = "L1_flight"

    def __init__(self):
        self.service = FlightService()

    async def validate_input(self, state: PlanningState) -> bool:
        """校验 L0 (意图) 是否已确认，且具备必要的航班搜索信息"""
        l0 = state.nodes.get("L0_intent")
        if not l0 or l0.status not in [NodeStatus.CONFIRMED]:
            return False
            
        constraints = state.constraints
        if not constraints:
            return False
            
        # 必须有出发地、目的地和出发日期
        c = ConstraintObject(**constraints)
        return bool(c.origin and c.destinations and c.departure_date)

    async def generate(self, state: PlanningState) -> dict:
        """调用 FlightService 搜索航班数据"""
        constraints = ConstraintObject(**state.constraints)
        
        # 提取第一个目的地作为搜索目标
        dest = constraints.destinations[0]
        
        results = await self.service.search_flights(
            origin=constraints.origin.city if constraints.origin else "SHA",
            destination=dest.city,
            date=constraints.departure_date,
            passengers=constraints.travelers.total
        )
        
        return results.model_dump()
