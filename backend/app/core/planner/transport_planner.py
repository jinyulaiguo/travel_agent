from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.transport import TransportService
from app.schemas.itinerary import TravelPlan

class TransportPlannerModule(BasePlannerModule):
    node_key: str = "L6_transport"

    def __init__(self):
        self.service = TransportService()

    async def validate_input(self, state: PlanningState) -> bool:
        """L6 依赖于 L5 (行程单) 已确认"""
        l5 = state.nodes.get("L5_itinerary")
        return l5 is not None and l5.status in [NodeStatus.CONFIRMED]

    async def generate(self, state: PlanningState) -> dict:
        """计算每日交通方案"""
        l5_node = state.nodes.get("L5_itinerary")
        itinerary_data = TravelPlan(**l5_node.data)
        
        # 提取酒店坐标 (从 L4 确认中提取)
        l4_node = state.nodes.get("L4_hotel")
        hotel_coords = None
        if l4_node and l4_node.status in [NodeStatus.CONFIRMED]:
            hotel = l4_node.data.get("selected_hotel", {})
            if "coordinates" in hotel:
                coords = hotel["coordinates"]
                hotel_coords = f"{coords['lat']},{coords['lng']}"

        daily_plans = []
        for day in itinerary_data.daily_itineraries:
            # 提取当天景点的坐标
            locations = []
            for item in day.items:
                if item.type == "sightseeing": # Matches ItemType.SIGHTSEEING
                    # 尝试从景点 node (L3) 中反查坐标，
                    # 或者假设 itinerary.items 中已经包含了 metadata 
                    # 这里的简化处理：从 item 的 metadata 获取 (如果存在)
                    coords = item.metadata.get("coordinates") if item.metadata else None
                    if not coords:
                        # 兜底查询或默认
                        pass
                    
                    locations.append({
                        "name": item.name,
                        "coords": f"{coords['lat']},{coords['lng']}" if coords else None
                    })
            
            # 生成当天交通路径
            day_plan = self.service.plan_daily_transport(
                day_number=day.day_number,
                locations=locations,
                hotel_coords=hotel_coords
            )
            daily_plans.append(day_plan)
            
        # 组装返回数据 (对应 TransportPlan schema)
        return {
            "daily_plans": [p.model_dump() for p in daily_plans],
            "total_estimated_cost_min": sum(p.total_estimated_cost_min for p in daily_plans),
            "total_estimated_cost_max": sum(p.total_estimated_cost_max for p in daily_plans),
            "total_estimated_cost_cny": sum(p.total_estimated_cost_min for p in daily_plans) * 0.2, # 汇率
            "currency": "THB"
        }
