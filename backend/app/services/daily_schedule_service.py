from typing import List, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.daily_schedule import DailyItinerary, GenerateScheduleRequest, AdjustScheduleRequest
from app.schemas.attraction import ConfirmedAttraction, Coordinates
from app.services.daily_schedule.allocator import Allocator
from app.services.state_service import StateService

class DailyScheduleService:
    def __init__(self):
        pass

    async def generate_schedule(self, db: AsyncSession, request: GenerateScheduleRequest) -> DailyItinerary:
        """
        Main entry for generating a schedule.
        """
        # 1. Fetch real confirmed attractions from L3 node if available
        # We use plan_id as session_id for simplicity as seen in previous logic
        state = await StateService.get_state(db, request.plan_id, "default_user")
        
        attractions = []
        l3_node = state.nodes.get("L3_attractions")
        if l3_node and l3_node.data and "confirmed_attractions" in l3_node.data:
            from app.schemas.attraction import AttractionList
            try:
                attr_list = AttractionList.model_validate(l3_node.data)
                attractions = attr_list.confirmed_attractions
            except Exception as e:
                print(f"Failed to parse confirmed attractions: {e}")
        
        # 2. Fallback to Mock Data if no confirmed attractions yet (for testing/demo)
        if not attractions:
            attractions = [
                ConfirmedAttraction(
                    attraction_id="A001",
                    name="故宫博物院",
                    cluster_id=1,
                    suggested_duration_hours=3.5,
                    coordinates=Coordinates(lat=39.916, lng=116.397),
                    attraction_tags=["博物馆", "历史"],
                    opening_hours={},
                    last_updated="2024-01-01"
                ),
                ConfirmedAttraction(
                    attraction_id="A002",
                    name="天坛公园",
                    cluster_id=1,
                    suggested_duration_hours=2.0,
                    coordinates=Coordinates(lat=39.883, lng=116.412),
                    attraction_tags=["公园", "历史"],
                    opening_hours={},
                    last_updated="2024-01-01"
                ),
                ConfirmedAttraction(
                    attraction_id="A003",
                    name="颐和园",
                    cluster_id=2,
                    suggested_duration_hours=4.0,
                    coordinates=Coordinates(lat=39.999, lng=116.273),
                    attraction_tags=["园林", "历史"],
                    opening_hours={},
                    last_updated="2024-01-01"
                )
            ]
        
        # 3. Build constraints from state or request
        mock_constraints = {
            "has_toddler": False,
            "has_elderly": False,
            "hard_constraints": state.constraints.get("hard_constraints", {}) if state.constraints else {}
        }
        
        allocator = Allocator(
            attractions=attractions,
            start_date=request.start_date,
            end_date=request.end_date,
            constraints=mock_constraints
        )
        
        itinerary = allocator.generate_schedule()
        
        # Auto-save to L5 node in GENERATED status
        # Note: API might not expect auto-save, but for HIL consistency
        # StateService.confirm_node would be for user confirmation, so we 
        # just manually update the node data here or return it for confirmStep.
        
        return itinerary

    async def adjust_schedule(self, db: AsyncSession, request: AdjustScheduleRequest) -> DailyItinerary:
        """
        Handles manual adjustments and persists to L5 node.
        """
        # Save to State Machine as CONFIRMED
        await StateService.confirm_node(
            db, 
            request.plan_id, 
            "default_user", 
            "L5_itinerary", 
            request.itinerary.model_dump(mode='json')
        )
        
        # Handle cross-module impact (L6, L8) via StateService handles it implicitly via ImpactPropagator
        
        return request.itinerary

daily_schedule_service = DailyScheduleService()
