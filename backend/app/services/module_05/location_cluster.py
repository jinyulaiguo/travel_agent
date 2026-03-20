from typing import List, Dict, Tuple
import math

class LocationClusterService:
    """
    Service for clustering attractions and finding a central location for accommodation.
    """
    
    @staticmethod
    def calculate_centroid(attractions: List[Dict[str, Any]]) -> Tuple[float, float]:
        """
        Calculates the centroid (geometric center) of a list of attractions.
        Each attraction should have 'lat' and 'lng' in its coordinates.
        """
        if not attractions:
            return (0.0, 0.0)
            
        total_lat = 0.0
        total_lng = 0.0
        
        for attraction in attractions:
            coords = attraction.get("coordinates") or {}
            total_lat += coords.get("lat", 0.0)
            total_lng += coords.get("lng", 0.0)
            
        return (total_lat / len(attractions), total_lng / len(attractions))

    @staticmethod
    def generate_area_rationale(area_name: str, attractions: List[Dict[str, Any]], avg_time: float) -> str:
        """
        Generates a rationale for the recommended accommodation area.
        """
        top_attractions = [a.get("name", "景点") for a in attractions[:2]]
        attraction_str = "、".join(top_attractions)
        
        return f"推荐入住 {area_name}，前往 {attraction_str} 等主要景点的平均交通时间约 {round(avg_time)} 分钟，地理位置极其便利。"

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # Convert decimal degrees to radians 
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r
