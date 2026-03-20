from typing import List, Dict, Any
from datetime import date
from app.schemas.daily_schedule import DailyItinerary, GenerateScheduleRequest, AdjustScheduleRequest
from app.schemas.attraction import ConfirmedAttraction, Coordinates
from app.services.daily_schedule.allocator import Allocator

class DailyScheduleService:
    def __init__(self):
        pass

    def generate_schedule(self, request: GenerateScheduleRequest) -> DailyItinerary:
        """
        Main entry for generating a schedule.
        In a complete system, this would:
        1. Fetch confirmed attractions from DB using plan_id
        2. Fetch constraints and flight anchors
        3. Pass them to the Allocator
        """
        # MVP Mock Data for demonstration
        mock_attractions = [
            ConfirmedAttraction(
                attraction_id="A001",
                name="Mock Museum",
                cluster_id=1,
                suggested_duration_hours=2.5,
                coordinates=Coordinates(lat=39.9, lng=116.4),
                last_updated="2023-01-01"
            ),
            ConfirmedAttraction(
                attraction_id="A002",
                name="Mock Mountain",
                cluster_id=1,
                suggested_duration_hours=4.0,
                coordinates=Coordinates(lat=39.95, lng=116.45),
                last_updated="2023-01-01"
            )
        ]
        
        mock_constraints = {
            "has_toddler": False,
            "has_elderly": False
        }
        
        allocator = Allocator(
            attractions=mock_attractions,
            start_date=request.start_date,
            end_date=request.end_date,
            constraints=mock_constraints
        )
        
        itinerary = allocator.generate_schedule()
        
        # In a complete system, we would save this itinerary to DB and 
        # possibly trigger state machine to NEXT phase (L6 Transport).
        
        return itinerary

    def adjust_schedule(self, request: AdjustScheduleRequest) -> DailyItinerary:
        """
        Handles manual adjustments by the user.
        Overrides the existing itinerary with the new one.
        """
        # In a real system:
        # 1. Update DB with request.itinerary
        # 2. Trigger cross-module impact (e.g., mark L6, L8 stale)
        
        # Simulating state impact for Task 6-4
        print(f"Schedule for plan {request.plan_id} adjusted manually.")
        print(">>> Node L6_transport: STALE")
        print(">>> Node L8_cost: STALE")
        
        return request.itinerary

daily_schedule_service = DailyScheduleService()
