import math
from typing import List, Dict, Any, Optional
from ..schemas.transport import TransportMode, TransportSegment, DailyTransportPlan, TransportPlan
from ..tools.map_route import map_route_mock

class TransportService:
    @staticmethod
    def calculate_haversine_distance(coord1: str, coord2: str) -> float:
        """Calculate the great circle distance between two points on the earth."""
        try:
            lat1, lon1 = map(float, coord1.split(','))
            lat2, lon2 = map(float, coord2.split(','))
        except (ValueError, AttributeError):
            return 0.0

        R = 6371  # Earth radius in kilometers
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def get_transport_recommendation(
        origin: str,
        destination: str,
        origin_coords: Optional[str],
        destination_coords: Optional[str],
        is_airport: bool = False,
        has_transit: bool = True
    ) -> TransportSegment:
        # 1. Get distance and duration from tool or fallback
        try:
            # Use mock tool
            route_data = map_route_mock(origin, destination)
            distance_km = route_data.get("distance_km", 0.0)
            duration_min = route_data.get("duration_minutes", 0.0)
            reliability = "L3" # Since we have a tool, but it's mock
        except Exception:
            # Fallback to Haversine if tool fails
            if origin_coords and destination_coords:
                distance_km = TransportService.calculate_haversine_distance(origin_coords, destination_coords) * 1.3
                duration_min = distance_km * 3 # Rough estimate 20km/h
                reliability = "L5"
            else:
                distance_km = 0.0
                duration_min = 0.0
                reliability = "L5"

        # 2. Logic for mode selection
        recommended_mode = TransportMode.DRIVING
        alternative_mode = None
        price_min, price_max = 0.0, 0.0
        instruction = ""

        if is_airport:
            recommended_mode = TransportMode.SHUTTLE
            alternative_mode = TransportMode.GRAB
            price_min, price_max = 150.0, 500.0
            instruction = f"从 {origin} 到 {destination}，建议使用机场大巴或正规出租车。"
        elif distance_km < 1.0:
            recommended_mode = TransportMode.WALKING
            alternative_mode = TransportMode.GRAB
            price_min, price_max = 0.0, 0.0
            instruction = "距离较近，建议步行前往。"
        elif 1.0 <= distance_km <= 5.0:
            if has_transit:
                recommended_mode = TransportMode.TRANSIT
                alternative_mode = TransportMode.GRAB
                price_min, price_max = 20.0, 60.0 # Standard transit fare
                instruction = "建议乘坐地铁或公交，经济快捷。"
            else:
                recommended_mode = TransportMode.GRAB
                alternative_mode = TransportMode.MOPED_TUKTUK
                price_min, price_max = distance_km * 15, distance_km * 25
                instruction = "该区域公共交通不便，建议使用 Grab 呼叫车辆。"
        else: # > 5km
            recommended_mode = TransportMode.GRAB
            alternative_mode = TransportMode.CHARTER
            price_min, price_max = distance_km * 12, distance_km * 22
            instruction = "行程距离较长，建议使用 Grab 呼叫车辆。"

        return TransportSegment(
            origin=origin,
            destination=destination,
            origin_coords=origin_coords,
            destination_coords=destination_coords,
            distance_km=round(distance_km, 2),
            duration_minutes=round(duration_min, 1),
            recommended_mode=recommended_mode,
            alternative_mode=alternative_mode,
            price_estimate_min=round(price_min, 0),
            price_estimate_max=round(price_max, 0),
            currency="THB",
            reliability_level=reliability,
            instruction=instruction,
            warning="以实际 App 显示为准，受时段/路况影响"
        )

    def plan_daily_transport(
        self, 
        day_number: int, 
        locations: List[Dict[str, Any]], 
        hotel_coords: Optional[str] = None
    ) -> DailyTransportPlan:
        """
        locations: List of dicts with 'name' and 'coords'
        hotel_coords: Initial start and final end point coordinate
        """
        segments = []
        total_min, total_max = 0.0, 0.0
        
        # Add hotel as start and end if available
        all_points = []
        if hotel_coords:
            all_points.append({"name": "酒店", "coords": hotel_coords})
        
        all_points.extend(locations)
        
        if hotel_coords:
            all_points.append({"name": "酒店", "coords": hotel_coords})

        for i in range(len(all_points) - 1):
            p1 = all_points[i]
            p2 = all_points[i+1]
            
            # Check if it's airport (very rough check for demo)
            is_airport = "机场" in p1['name'] or "机场" in p2['name'] or "Airport" in p1['name'] or "Airport" in p2['name']
            
            segment = self.get_transport_recommendation(
                origin=p1['name'],
                destination=p2['name'],
                origin_coords=p1.get('coords'),
                destination_coords=p2.get('coords'),
                is_airport=is_airport
            )
            segments.append(segment)
            total_min += segment.price_estimate_min
            total_max += segment.price_estimate_max

        return DailyTransportPlan(
            day_number=day_number,
            segments=segments,
            total_estimated_cost_min=total_min,
            total_estimated_cost_max=total_max,
            currency="THB"
        )
