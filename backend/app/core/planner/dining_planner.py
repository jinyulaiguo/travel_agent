from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.schemas.dining import DiningPlanState, DailyDiningPlan
from app.schemas.daily_schedule import DailyItinerary
from app.services.dining_service import DiningService
from app.db.session import SessionLocal
from datetime import datetime

class DiningPlannerModule(BasePlannerModule):
    node_key: str = "L7_dining"

    async def validate_input(self, state: PlanningState) -> bool:
        """校验 L2 (目的地) 和 L5 (行程) 是否已确认"""
        l2 = state.nodes.get("L2_destination")
        l5 = state.nodes.get("L5_itinerary")
        return (
            l2 is not None and l2.status == NodeStatus.CONFIRMED and
            l5 is not None and l5.status == NodeStatus.CONFIRMED
        )

    async def generate(self, state: PlanningState) -> dict:
        """生成每日餐饮推荐"""
        # 1. 提取上游数据
        itinerary_node = state.nodes.get("L5_itinerary")
        dest_node = state.nodes.get("L2_destination")
        
        if not itinerary_node or not itinerary_node.data or not dest_node or not dest_node.data:
            return {}
            
        itinerary = DailyItinerary(**itinerary_node.data)
        dest_data = dest_node.data
        
        # 获取 L3 景点的坐标映射，用于更精确的定位
        attractions_node = state.nodes.get("L3_attractions")
        attraction_coords = {}
        if attractions_node and attractions_node.data:
            for attr in attractions_node.data.get("confirmed_attractions", []):
                attraction_coords[attr["attraction_id"]] = attr["coordinates"]

        # 获取主要城市中心点（作为兜底）
        city = "清迈" 
        center_lat, center_lng = 18.79, 98.98
        if "confirmed_destinations" in dest_data and dest_data["confirmed_destinations"]:
            dest = dest_data["confirmed_destinations"][0]
            city = dest.get("city", "清迈")
            center_lat = dest.get("lat", 18.79)
            center_lng = dest.get("lng", 98.98)

        daily_plans = []
        async with SessionLocal() as db:
            for day_itinerary in itinerary.days:
                # 尝试找到当天第一个景点的坐标作为推荐中心
                day_lat, day_lng = center_lat, center_lng
                for item in day_itinerary.items:
                    if item.type == "attraction" and item.attraction_id in attraction_coords:
                        coords = attraction_coords[item.attraction_id]
                        day_lat, day_lng = coords["lat"], coords["lng"]
                        break
                
                # 调用服务层获取推荐
                classic = await DiningService.recommend_classic_restaurants(db, city, day_lat, day_lng)
                popular = await DiningService.recommend_popular_restaurants(db, city, day_lat, day_lng)
                specialties = await DiningService.get_city_specialties(db, city)
                etiquette = await DiningService.get_city_etiquette(db, city)
                
                daily_plans.append(DailyDiningPlan(
                    day=day_itinerary.day,
                    date=day_itinerary.date,
                    classic_recommendations=classic,
                    popular_references=popular,
                    local_specialties=specialties,
                    etiquette_tips=etiquette
                ))
            
        plan_state = DiningPlanState(
            daily_plans=daily_plans,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return plan_state.model_dump()
