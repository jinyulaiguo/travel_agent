from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.module_05 import HotelSelection, HotelRecord, Coordinates
from app.services.module_05.location_cluster import LocationClusterService
from app.tools.hotel_search import hotel_search_mock
from app.tools.map_route import map_route_mock

class HotelService:
    """
    Main service for hotel recommendation logic (Module 05).
    """
    
    def __init__(self):
        self.cluster_service = LocationClusterService()

    async def get_hotel_recommendations(
        self, 
        attractions: List[Dict[str, Any]], 
        check_in: str, 
        check_out: str,
        budget: Optional[float] = None
    ) -> HotelSelection:
        """
        Process hotel recommendations based on attractions and user constraints.
        """
        if not attractions:
            return HotelSelection(recommended_area="N/A", area_rationale="No attractions provided.")

        # 1. Calculate cluster center of attractions
        centroid_lat, centroid_lng = self.cluster_service.calculate_centroid(attractions)
        center_coords = {"lat": centroid_lat, "lng": centroid_lng}
        
        # 2. Search for hotels near the center (currently using mock)
        raw_hotels = hotel_search_mock(center_coords, check_in, check_out)
        
        processed_records = []
        
        # 3. Process each hotel (calculate distance and score)
        for h in raw_hotels:
            # Calculate physical distance to center
            dist = self.cluster_service.haversine_distance(
                centroid_lat, centroid_lng, 
                h["coordinates"]["lat"], h["coordinates"]["lng"]
            )
            
            # Use map_route to get "travel time" to the center (representative of convenience)
            # In a real scenario, this might be called for a couple of top hotels only
            route_info = map_route_mock(
                f"{h['coordinates']['lat']},{h['coordinates']['lng']}",
                f"{centroid_lat},{centroid_lng}",
                mode="driving"
            )
            
            record = HotelRecord(
                hotel_id=h["hotel_id"],
                name=h["name"],
                area=h["area"],
                coordinates=Coordinates(**h["coordinates"]),
                price_per_night=h["price_per_night"],
                price_snapshot_time=h["price_snapshot_time"],
                ota_rating=h["ota_rating"],
                ota_source=h["ota_source"],
                distance_to_cluster_center_km=round(dist, 2),
                booking_url=h["booking_url"],
                amenities=h["amenities"],
                rationale=f"距离景点重心约 {round(dist, 1)}km，评价 {h['ota_rating']} 分。"
            )
            processed_records.append(record)

        # Sort by ota_rating and distance (simple mock scoring)
        # In reality,Task 5-2 specifies a scoring algorithm
        processed_records.sort(key=lambda x: (x.ota_rating / 10.0 - x.distance_to_cluster_center_km / 10.0), reverse=True)

        selected = processed_records[0] if processed_records else None
        alternatives = processed_records[1:6] # Up to 5 alternatives

        # Generate area rationale
        area_rationale = self.cluster_service.generate_area_rationale(
            "商业中心及景点集散区", # Mock area name
            attractions,
            random_duration := 15.0 # Mock average duration
        )

        return HotelSelection(
            selected_hotel=selected,
            alternatives=alternatives,
            recommended_area="城市中心商业区",
            area_rationale=area_rationale
        )
