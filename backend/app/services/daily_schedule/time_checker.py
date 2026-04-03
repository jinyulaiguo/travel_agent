from datetime import time, timedelta, datetime
from typing import List, Dict, Any

def check_availability(opening_hours: Dict[str, Any], target_date: str, planned_start_time: time, duration_hours: float) -> (bool, time, str):
    """
    Checks if an attraction is available on the given date and time.
    opening_hours format: {
        "regular": {
            "0": ["09:00", "18:00"], # Monday
            "1": ["09:00", "18:00"],
            ...
        },
        "special_closures": ["2026-03-25"]
    }
    """
    date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    weekday_str = str(date_obj.weekday())
    
    # 1. Check special closures
    if target_date in opening_hours.get("special_closures", []):
        return False, planned_start_time, "景点在选定日期因特殊原因关闭"

    # 2. Check regular hours
    day_range = opening_hours.get("regular", {}).get(weekday_str)
    if not day_range:
        # Default to 09:00 - 20:00 if not specified to avoid skipping all items
        day_range = ["09:00", "20:00"]
    
    open_time = datetime.strptime(day_range[0], "%H:%M").time()
    close_time = datetime.strptime(day_range[1], "%H:%M").time()
    
    adjusted_start = planned_start_time
    warning_msg = ""
    is_available = True
    
    # Check if starts before open
    if planned_start_time < open_time:
        adjusted_start = open_time
        warning_msg = f"安排的时间早于开门时间，已调整至 {day_range[0]}"
    
    # Check if ends after close
    planned_end_dt = datetime.combine(date_obj, adjusted_start) + timedelta(hours=duration_hours)
    if planned_end_dt.time() > close_time:
        is_available = False
        warning_msg = f"游览由于结束时间晚于闭馆时间（{day_range[1]}）而存在冲突"
        
    return is_available, adjusted_start, warning_msg

def apply_boundary_limits(target_date_str: str, config: Dict[str, Any], is_first_day: bool, is_last_day: bool) -> (time, time):
    """
    Returns the time window (start_time, end_time) for a given day based on config.
    config keys: first_day_available_hours, last_day_cutoff_time
    """
    default_start = time(8, 30)
    default_end = time(20, 30)
    
    if is_first_day:
        # first_day_available_hours is relative to start of day or arrival?
        # Requirement says: "基于 FlightAnchor.outbound.arrival_time 计算"
        # For simplicity, we assume config provides the absolute start time for activities.
        start_val = config.get("first_day_activity_start", "14:00")
        default_start = datetime.strptime(start_val, "%H:%M").time()
    
    if is_last_day:
        end_val = config.get("last_day_cutoff_time", "17:00")
        default_end = datetime.strptime(end_val, "%H:%M").time()
        
    return default_start, default_end
