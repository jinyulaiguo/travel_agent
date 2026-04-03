import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

def hotel_search_mock(
    location: Dict[str, float], 
    check_in: str, 
    check_out: str, 
    budget_range: Optional[Tuple[float, float]] = None
) -> List[Dict[str, Any]]:
    """
    Mock implementation of hotel_search tool.
    Returns 3 recommended + 5 alternative hotels.
    """
    lat = location.get("lat", 0.0)
    lng = location.get("lng", 0.0)
    
    # Check if we are in Beijing (rough check)
    is_beijing = 39.0 < lat < 41.0 and 115.0 < lng < 118.0
    
    # Common amenities for mock data
    amenities_list = ["Free WiFi", "Breakfast included", "Air conditioning", "Pool", "Gym", "Parking"]
    
    beijing_hotels = [
        "北京饭店 (Beijing Hotel)",
        "王府半岛酒店 (The Peninsula Beijing)",
        "璞瑄酒店 (The PuXuan Hotel)",
        "北京瑞吉酒店 (The St. Regis Beijing)",
        "北京华尔道夫酒店 (Waldorf Astoria Beijing)",
        "北京四季酒店 (Four Seasons Hotel Beijing)",
        "北京柏悦酒店 (Park Hyatt Beijing)",
        "北京康莱德酒店 (Conrad Beijing)"
    ]
    
    hotels = []
    
    # Generate 8 hotels (3 recommended + 5 alternatives)
    for i in range(8):
        # Slightly vary coordinates around the center for mock effect
        hotel_lat = lat + random.uniform(-0.015, 0.015)
        hotel_lng = lng + random.uniform(-0.015, 0.015)
        
        # Mock OTA ratings and prices
        ota_rating = round(random.uniform(7.5, 9.8), 1)
        price = random.uniform(200, 1500)
        
        # Mock price snapshot timing (within the last 5 minutes)
        snapshot_time = datetime.now() - timedelta(minutes=random.randint(0, 5))
        
        name = beijing_hotels[i] if is_beijing and i < len(beijing_hotels) else f"Mock Hotel {i+1}"
        area = "王府井/故宫周边" if is_beijing else "Downtown / Central Area"
        
        hotel = {
            "hotel_id": f"hotel_{i+100}",
            "name": name,
            "area": area,
            "coordinates": {"lat": hotel_lat, "lng": hotel_lng},
            "price_per_night": round(price, 2),
            "price_snapshot_time": snapshot_time,
            "ota_rating": ota_rating,
            "ota_source": random.choice(["Booking.com", "Agoda", "Trip.com", "Ctrip"]),
            "booking_url": f"https://www.booking.com/hotel/mock_{i+1}.html",
            "amenities": random.sample(amenities_list, random.randint(2, 5)),
            "distance_to_cluster_center_km": 0.0, # Will be calculated by service
            "is_recommended": i < 3
        }
        hotels.append(hotel)
        
    return hotels
