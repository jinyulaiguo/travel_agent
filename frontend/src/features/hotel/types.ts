export interface Coordinates {
  lat: number;
  lng: number;
}

export interface HotelRecord {
  hotel_id: string;
  name: string;
  area: string;
  coordinates: Coordinates;
  price_per_night: number;
  price_snapshot_time: string;
  ota_rating: number;
  ota_source: string;
  distance_to_cluster_center_km: number;
  booking_url: string;
  confidence_level: "L1" | "L2" | "L5";
  is_locked: boolean;
  is_manual_input: boolean;
  amenities: string[];
  rationale?: string;
}

export interface HotelSelection {
  selected_hotel: HotelRecord | null;
  alternatives: HotelRecord[];
  recommended_area: string;
  area_rationale: string;
}
