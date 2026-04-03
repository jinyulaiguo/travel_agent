from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.attraction.attraction_service import AttractionService
from app.services.attraction.knowledge_base_service import KnowledgeBaseService
from app.schemas.attraction import AttractionRecommendationRequest
from app.schemas.intent import ConstraintObject

class AttractionPlannerModule(BasePlannerModule):
    node_key: str = "L3_attractions"

    def __init__(self):
        self.kb_service = KnowledgeBaseService()
        self.service = AttractionService(self.kb_service)

    async def validate_input(self, state: PlanningState) -> bool:
        """L3 依赖于 L2 (目的地) 已确认"""
        l2 = state.nodes.get("L2_destination")
        return l2 is not None and l2.status in [NodeStatus.CONFIRMED]

    async def generate(self, state: PlanningState) -> dict:
        """基于目的地和偏好生成景点推荐"""
        constraints = ConstraintObject(**state.constraints)
        l2_node = state.nodes.get("L2_destination")
        dest_data = l2_node.data
        
        # 提取确认的目的地名称
        cities = [d["city"] for d in dest_data.get("confirmed_destinations", [])]
        
        request = AttractionRecommendationRequest(
            cities=cities,
            available_days=dest_data.get("total_days", 3),
            travel_style=constraints.preferences.travel_style
        )
        
        # 调用核心算法进行地理聚类推荐
        # 注意：recommend_attractions 目前是同步的，在此处异步包装
        results = self.service.recommend_attractions(request)
        
        return results.model_dump()
