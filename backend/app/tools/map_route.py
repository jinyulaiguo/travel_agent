import random
from typing import Dict, Any

def map_route_mock(origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    """
    Mock implementation of map_route tool.
    Calculates distance and travel time between two points.
    """
    # Simulate API call delay
    # In a real tool, this would call Google Maps or Amap API
    
    # Randomly generated data for mock
    base_distance_km = random.uniform(2.0, 15.0)
    
    # Adjust time based on mode
    if mode == "walking":
        duration_minutes = base_distance_km * 12  # ~12 min/km
    elif mode == "bicycling":
        duration_minutes = base_distance_km * 4   # ~4 min/km
    elif mode == "transit":
        duration_minutes = base_distance_km * 3 + random.uniform(5, 15)  # includes wait time
    else:  # driving
        duration_minutes = base_distance_km * 2 + random.uniform(0, 10)  # traffic
        
    return {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "distance_km": round(base_distance_km, 2),
        "duration_minutes": round(duration_minutes, 1),
        "status": "success",
        "description": f"从 {origin} 到 {destination} 的预计{mode}时间为 {round(duration_minutes, 1)} 分钟，距离约 {round(base_distance_km, 2)} 公里。"
    }
