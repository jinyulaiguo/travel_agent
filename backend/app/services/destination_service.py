from typing import List, Tuple
from datetime import timedelta
from fastapi import HTTPException

from app.schemas.flight import FlightAnchor
from app.schemas.intent import ConstraintObject, Location
from app.schemas.destination import (
    DestinationItem,
    DestinationConfig,
    DestinationRecommendation,
    DestinationConfirmRequest
)
from app.schemas.state import PlanningState, NodeStatus

class DestinationService:
    def calculate_time_constraints(self, flight: FlightAnchor) -> Tuple[float, str]:
        """
        Calculates first day available hours and last day cutoff time based on flight schedule.
        Assumes 2 hours to clear airport/check-in, and day ends at 22:00.
        Last day cutoff is 3 hours before departure.
        """
        # First day calculation
        arrival_time = flight.outbound.arrival_time
        arrival_float = arrival_time.hour + arrival_time.minute / 60.0
        # Assuming day ends at 22:00, and it takes 2 hours to start activity
        available_hours = max(0.0, 22.0 - arrival_float - 2.0)

        # Last day calculation
        cutoff_time_str = "20:00" # Default if no inbound flight
        if flight.inbound:
            departure_time = flight.inbound.departure_time
            cutoff_dt = departure_time - timedelta(hours=3)
            # If cutoff is previous day (flight is very early like 02:00 AM), we just cap it to min 00:00 of departure day, actually just use HH:MM.
            # However, if it's negative relatively, returning HH:MM is still valid.
            cutoff_time_str = cutoff_dt.strftime("%H:%M")
            
        return round(available_hours, 1), cutoff_time_str

    def generate_recommendations(self, intent: ConstraintObject) -> DestinationRecommendation:
        """
        Generate destination recommendations based on available days and selected cities.
        """
        days = intent.available_days or 3 # Fallback
        locations = intent.destinations
        
        if not locations:
            # Fallback if no destination provided
            locations = [Location(city="未知城市", country="未知", country_code="XX")]
            
        candidates = []
        
        if days <= 3:
            recommend_type = "推荐单城精华游"
            # Allocate all days to the first city
            candidates.append(
                DestinationItem(
                    city=locations[0].city,
                    country_code=locations[0].country_code,
                    lat=locations[0].lat,
                    lng=locations[0].lng,
                    allocated_days=days,
                    recommend_reason="短途旅行，专注于一城",
                    order=0
                )
            )
        elif 4 <= days <= 6:
            recommend_type = "可深度游单城或浅玩两城"
            if len(locations) >= 2:
                days1 = days // 2 + (days % 2)
                days2 = days // 2
                candidates.append(
                    DestinationItem(
                        city=locations[0].city, country_code=locations[0].country_code,
                        lat=locations[0].lat, lng=locations[0].lng,
                        allocated_days=days1, recommend_reason="主打城市深度体验", order=0
                    )
                )
                candidates.append(
                    DestinationItem(
                        city=locations[1].city, country_code=locations[1].country_code,
                        lat=locations[1].lat, lng=locations[1].lng,
                        allocated_days=days2, recommend_reason="顺路游玩周边城市", order=1
                    )
                )
            else:
                candidates.append(
                    DestinationItem(
                        city=locations[0].city, country_code=locations[0].country_code,
                        lat=locations[0].lat, lng=locations[0].lng,
                        allocated_days=days, recommend_reason="单城深度从容游览", order=0
                    )
                )
        else:
            recommend_type = "可考虑多城组合行程"
            # Distribute days across up to 3 cities evenly
            num_cities = min(len(locations), 3)
            base_days = days // max(1, num_cities)
            remainder = days % max(1, num_cities)
            
            for i in range(num_cities):
                allocated = base_days + (1 if i < remainder else 0)
                candidates.append(
                    DestinationItem(
                        city=locations[i].city, country_code=locations[i].country_code,
                        lat=locations[i].lat, lng=locations[i].lng,
                        allocated_days=allocated, recommend_reason="城际核心景点串联", order=i
                    )
                )

        return DestinationRecommendation(
            recommend_type=recommend_type,
            candidates=candidates
        )

    def lock_destination(self, request: DestinationConfirmRequest, flight: FlightAnchor, state: PlanningState) -> DestinationConfig:
        """
        Locks the destination configuration and updates node states.
        """
        # Calculate time constraints
        avail_hours, cutoff_time = self.calculate_time_constraints(flight)
        
        total_days = sum(item.allocated_days for item in request.destinations)
        
        config = DestinationConfig(
            confirmed_destinations=request.destinations,
            total_days=total_days,
            first_day_available_hours=avail_hours,
            last_day_cutoff_time=cutoff_time
        )
        
        # Check current state of L2
        l2_node = state.nodes.get("L2_destination")
        
        # If already confirmed and NOT forced override, reject and warn
        if l2_node and l2_node.status in [NodeStatus.CONFIRMED, NodeStatus.LOCKED] and not request.force_override:
            raise HTTPException(
                status_code=409,
                detail="目的地已锁定。修改目的地将导致后续节点（景点、酒店、行程、交通、预算）全量重算。如果确认修改，请设置 force_override=true。"
            )
            
        # Perform updates
        if l2_node:
            l2_node.status = NodeStatus.CONFIRMED
            l2_node.data = config.model_dump()
            
        # Mark downstream as stale if L2 was modified
        downstream_nodes = ["L3_attractions", "L4_hotel", "L5_itinerary", "L6_transport", "L7_dining", "L8_cost"]
        for node_key in downstream_nodes:
            downstream = state.nodes.get(node_key)
            if downstream and downstream.status not in [NodeStatus.PENDING, NodeStatus.SKIPPED]:
                downstream.status = NodeStatus.STALE
                
        # Move L3 from PENDING to GENERATE? In our state machine PENDING is default. We can set it to PENDING if it's not started.
        l3_node = state.nodes.get("L3_attractions")
        if l3_node and l3_node.status == NodeStatus.PENDING:
            # We just leave it pending or ready
            pass

        return config

destination_service = DestinationService()
