from typing import List, Dict, Any, Optional
from app.services.dining_service import DiningService
from app.db.session import async_session_factory

async def restaurant_lookup(
    city: str, 
    lat: float, 
    lng: float, 
    radius_km: float = 2.0,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    按城市和坐标检索餐饮知识库。
    
    参数:
    - city (str): 城市名称
    - lat, lng (float): 中心点坐标
    - radius_km (float): 检索半径，默认 2.0km
    - tags (List[str]): 偏好标签
    
    返回:
    - Dict: 包含经典餐厅和热门餐厅列表
    """
    async with async_session_factory() as db:
        classic = await DiningService.recommend_classic_restaurants(
            db, city, lat, lng, limit=2
        )
        popular = await DiningService.recommend_popular_restaurants(
            db, city, lat, lng, limit=3
        )
        
        # 转换并返回
        return {
            "recommended_restaurants": [r.model_dump() for r in classic],
            "popular_alternatives": [r.model_dump() for r in popular],
            "query_context": {
                "city": city,
                "radius_km": radius_km,
                "center": {"lat": lat, "lng": lng}
            }
        }
