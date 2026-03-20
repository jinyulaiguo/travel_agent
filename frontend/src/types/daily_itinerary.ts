export interface Coordinates {
  lat: number;
  lng: number;
}

export interface DailyItineraryItem {
  id: string; // Unique ID for dnd-kit
  type: 'attraction' | 'fixed_slot' | 'buffer';
  attraction_id?: string;
  name: string;
  planned_start_time: string;
  planned_end_time: string;
  duration_hours: number;
  notes?: string;
}

export interface DailyItineraryDay {
  day: number;
  date: string;
  hotel_start_coordinates?: Coordinates;
  items: DailyItineraryItem[];
  total_active_hours: number;
  has_conflicts: boolean;
}

export interface DailyItinerary {
  days: DailyItineraryDay[];
}
