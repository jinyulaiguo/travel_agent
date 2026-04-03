from typing import List, Dict, Any
from datetime import datetime, timedelta, date, time
from app.schemas.daily_schedule import (
    DailyItinerary, DailyItineraryDay, DailyItineraryItem, Coordinates
)
from app.schemas.attraction import ConfirmedAttraction
from app.services.daily_schedule.time_checker import apply_boundary_limits, check_availability

# Simple tags dictionary for categorizing intensity
HIGH_INTENSITY_TAGS = {"爬山", "徒步", "登山", "探险", "主题公园", "高强度"}
LOW_INTENSITY_TAGS = {"博物馆", "美术馆", "展览", "购物", "剧院", "咖啡馆", "低强度"}

class Allocator:
    def __init__(self, attractions: List[ConfirmedAttraction], start_date: date, end_date: date, constraints: Dict[str, Any]):
        self.attractions = attractions
        self.start_date = start_date
        self.end_date = end_date
        self.constraints = constraints
        self.total_days = (end_date - start_date).days + 1
        
        # Determine max daily active hours based on constraints
        self.max_daily_hours = 10.0
        if constraints.get("has_toddler", False):
            self.max_daily_hours = 8.0
        
        # Mobility restrictions
        self.is_mobility_restricted = constraints.get("has_elderly", False) or constraints.get("mobility_impaired", False)

    def _get_intensity(self, attraction: ConfirmedAttraction) -> str:
        tags = set(attraction.attraction_tags)
        if tags & HIGH_INTENSITY_TAGS:
            return "high"
        if tags & LOW_INTENSITY_TAGS:
            return "low"
        return "medium"

    def _sort_attractions(self) -> List[ConfirmedAttraction]:
        # Filter out high-intensity attractions if mobility restricted
        filtered = self.attractions
        if self.is_mobility_restricted:
            # Move high intensity to bottom or keep as "backup"? For now just keep but mark
            pass
        
        # Sort primarily by cluster_id to ensure spatial continuity
        # Within same cluster, try to put high intensity earlier for morning?
        # Actually generate_schedule will pick from sorted list, so we sort by (cluster, intensity_weight)
        return sorted(filtered, key=lambda a: (a.cluster_id or 0, -self._get_intensity_weight(self._get_intensity(a))))

    def _get_intensity_weight(self, intensity: str) -> int:
        if intensity == "high": return 2
        if intensity == "medium": return 1
        return 0

    def generate_schedule(self) -> DailyItinerary:
        sorted_attractions = self._sort_attractions()
        days_itinerary = []
        
        # Track scheduled attractions across the entire generate_schedule call
        scheduled_ids = set()
        
        # Bound configs
        bound_config = {
            "first_day_activity_start": self.constraints.get("first_day_activity_start", "14:00"),
            "last_day_cutoff_time": self.constraints.get("last_day_cutoff_time", "17:00")
        }
        
        # Hard constraints: fixed_timeslots
        fixed_slots = self.constraints.get("hard_constraints", {}).get("fixed_timeslots", [])
        
        for day_index in range(self.total_days):
            current_date = self.start_date + timedelta(days=day_index)
            date_str = current_date.isoformat()
            is_first_day = (day_index == 0)
            is_last_day = (day_index == self.total_days - 1)
            
            # Boundary calculations
            start_time_limit, end_time_limit = apply_boundary_limits(date_str, bound_config, is_first_day, is_last_day)
            
            current_dt = datetime.combine(current_date, start_time_limit)
            end_dt = datetime.combine(current_date, end_time_limit)
            max_dt = current_dt + timedelta(hours=self.max_daily_hours)
            if max_dt < end_dt:
                end_dt = max_dt
                
            day_items: List[DailyItineraryItem] = []
            has_conflicts = False
            total_active_hours = 0.0
            
            # 1. Process Fixed Slots for today
            day_fixed_slots = [s for s in fixed_slots if s.get("date") == date_str]
            for slot in sorted(day_fixed_slots, key=lambda x: x['start_time']):
                slot_start_time = datetime.strptime(slot['start_time'], "%H:%M").time()
                slot_end_time = datetime.strptime(slot['end_time'], "%H:%M").time()
                slot_duration = round((datetime.combine(current_date, slot_end_time) - datetime.combine(current_date, slot_start_time)).total_seconds() / 3600.0, 2)
                day_items.append(DailyItineraryItem(
                    type="fixed_slot",
                    name=f"固定行程：{slot.get('description', '未命名')}",
                    planned_start_time=slot['start_time'],
                    planned_end_time=slot['end_time'],
                    duration_hours=slot_duration
                ))

            # 2. Process Attractions for today
            for attraction in sorted_attractions:
                if attraction.attraction_id in scheduled_ids:
                    continue
                
                duration_hrs = attraction.suggested_duration_hours
                
                # Check for overlap with fixed slots and move current_dt if needed
                for item in day_items:
                    if item.type == "fixed_slot":
                        f_start = datetime.combine(current_date, datetime.strptime(item.planned_start_time, "%H:%M").time())
                        f_end = datetime.combine(current_date, datetime.strptime(item.planned_end_time, "%H:%M").time())
                        # If current activity would overlap, skip to after the fixed slot
                        if current_dt < f_end and (current_dt + timedelta(hours=duration_hrs) > f_start):
                            current_dt = f_end + timedelta(minutes=30)
                
                if current_dt + timedelta(hours=duration_hrs) > end_dt:
                    continue
                    
                # Time availability checker
                is_available, adjusted_start, warning = check_availability(
                    attraction.opening_hours, date_str, current_dt.time(), duration_hrs
                )
                
                if adjusted_start > current_dt.time():
                    wait_dt = datetime.combine(current_date, adjusted_start)
                    day_items.append(DailyItineraryItem(
                        type="buffer",
                        name="等待开门暂歇",
                        planned_start_time=current_dt.strftime("%H:%M"),
                        planned_end_time=wait_dt.strftime("%H:%M"),
                        duration_hours=round((wait_dt - current_dt).total_seconds() / 3600.0, 2)
                    ))
                    current_dt = wait_dt

                if current_dt + timedelta(hours=duration_hrs) > end_dt:
                    continue

                planned_end_dt = current_dt + timedelta(hours=duration_hrs)
                
                day_items.append(DailyItineraryItem(
                    type="attraction",
                    attraction_id=attraction.attraction_id,
                    name=attraction.name,
                    planned_start_time=current_dt.strftime("%H:%M"),
                    planned_end_time=planned_end_dt.strftime("%H:%M"),
                    duration_hours=duration_hrs,
                    coordinates=attraction.coordinates,
                    notes=warning if warning else None
                ))
                
                scheduled_ids.add(attraction.attraction_id)
                current_dt = planned_end_dt
                total_active_hours += duration_hrs
                
                # Buffer after attraction
                if current_dt < end_dt:
                    buffer_end = min(current_dt + timedelta(hours=0.5), end_dt)
                    day_items.append(DailyItineraryItem(
                        type="buffer",
                        name="交通缓冲",
                        planned_start_time=current_dt.strftime("%H:%M"),
                        planned_end_time=buffer_end.strftime("%H:%M"),
                        duration_hours=0.5
                    ))
                    current_dt = buffer_end
                    total_active_hours += 0.5
            
            days_itinerary.append(DailyItineraryDay(
                day=day_index + 1,
                date=current_date,
                hotel_start_coordinates=None,
                items=sorted(day_items, key=lambda x: x.planned_start_time),
                total_active_hours=round(total_active_hours, 2),
                has_conflicts=has_conflicts
            ))
            
        return DailyItinerary(days=days_itinerary)
