import math
from typing import Dict, Optional
from app.schemas.attraction import Coordinates

class MapService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def map_route(self, origin: Coordinates, destination: Coordinates, mode: str = "driving") -> Dict:
        """
        Calculate distance and estimated travel time.
        Fallback to Haversine distance if no API key or API fails.
        """
        # In a real implementation, we would call Google Maps or AMap API here.
        # For now, we implement the fallback logic.
        
        distance_km = self._calculate_haversine_distance(origin, destination)
        
        # Estimate time based on mode (km/h)
        speeds = {
            "walking": 5,
            "driving": 40,  # Average city speed
            "transit": 20
        }
        speed = speeds.get(mode, 40)
        
        estimated_minutes = (distance_km / speed) * 60
        
        # Add some "buffer" for traffic/stops
        if mode == "driving":
            estimated_minutes *= 1.2
        elif mode == "transit":
            estimated_minutes += 10  # Waiting time
            
        return {
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(estimated_minutes),
            "mode": mode,
            "status": "fallback_calculated",
            "description": f"预估{self._translate_mode(mode)}约需 {round(estimated_minutes)} 分钟 (基于直线距离 {round(distance_km, 2)}km 计算)"
        }

    def _calculate_haversine_distance(self, coord1: Coordinates, coord2: Coordinates) -> float:
        R = 6371.0  # Earth radius in km
        lat1, lon1 = math.radians(coord1.lat), math.radians(coord1.lng)
        lat2, lon2 = math.radians(coord2.lat), math.radians(coord2.lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def _translate_mode(self, mode: str) -> str:
        translations = {
            "walking": "步行",
            "driving": "驾车",
            "transit": "公交/地铁"
        }
        return translations.get(mode, mode)
