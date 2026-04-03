import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { DailyItineraryItem } from '../../../types/daily_itinerary';

// Fix for default marker icons in Leaflet with React
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapRouteProps {
  items: DailyItineraryItem[];
}

// Helper to auto-fit map bounds to markers
const MapBoundsSetter: React.FC<{ positions: [number, number][] }> = ({ positions }) => {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 0) {
      const bounds = L.latLngBounds(positions);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [positions, map]);
  return null;
};

const MapRoute: React.FC<MapRouteProps> = ({ items }) => {
  // Extract coordinates for attractions
  const attractionItems = useMemo(() => 
    items.filter(item => item.type === 'attraction' && item.coordinates),
    [items]
  );

  const positions = useMemo(() => 
    attractionItems.map(item => [item.coordinates!.lat, item.coordinates!.lng] as [number, number]),
    [attractionItems]
  );

  if (positions.length === 0) {
    return (
      <div className="map-placeholder">
        <p>暂无地理位置信息，无法生成地图路线。</p>
      </div>
    );
  }

  return (
    <div className="map-route-card">
      <MapContainer 
        center={positions[0]} 
        zoom={13} 
        scrollWheelZoom={false}
        style={{ height: '300px', width: '100%', borderRadius: '12px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {attractionItems.map((item, idx) => (
          <Marker 
            key={`${item.attraction_id}-${idx}`} 
            position={[item.coordinates!.lat, item.coordinates!.lng]}
          >
            <Popup>
              <div className="map-popup">
                <strong>{idx + 1}. {item.name}</strong>
                <p>{item.planned_start_time} - {item.planned_end_time}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {positions.length > 1 && (
          <Polyline 
            positions={positions} 
            color="var(--accent)" 
            weight={4} 
            opacity={0.6}
            dashArray="10, 10" 
          />
        )}
        
        <MapBoundsSetter positions={positions} />
      </MapContainer>
    </div>
  );
};

export default MapRoute;
