import React, { useState, useEffect } from 'react';
import HotelList from './HotelList';
import ManualHotelEntry from './ManualHotelEntry';
import type { HotelSelection, HotelRecord } from '../types';

const HotelRecommendation: React.FC = () => {
  const [data, setData] = useState<HotelSelection | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isManualMode, setIsManualMode] = useState<boolean>(false);

  // Mock initial attractions data - in real app, this comes from state/props
  const attractions = [
    { name: "Eiffel Tower", coordinates: { lat: 48.8584, lng: 2.2945 } },
    { name: "Louvre Museum", coordinates: { lat: 48.8606, lng: 2.3376 } }
  ];

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/hotels/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attractions,
          check_in: '2024-06-01',
          check_out: '2024-06-05'
        })
      });

      if (!response.ok) {
        throw new Error('API服务暂时不可用');
      }

      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || '获取推荐失败');
      // If API fails, we could potentially auto-trigger manual mode or show a button
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleRefresh = () => {
    fetchRecommendations();
  };

  const handleSelectAlternative = (hotel: HotelRecord) => {
    if (!data) return;
    setData({
      ...data,
      selected_hotel: hotel,
      alternatives: [data.selected_hotel!, ...data.alternatives.filter(h => h.hotel_id !== hotel.hotel_id)].slice(0, 5)
    });
  };

  const handleManualConfirm = (hotel: HotelRecord) => {
    setData({
      selected_hotel: hotel,
      alternatives: [],
      recommended_area: hotel.area,
      area_rationale: '用户手动录入选定'
    });
    setIsManualMode(false);
  };

  if (loading) return <div className="hotel-loading">正在智能搜索最优酒店...</div>;

  if (error) {
    return (
      <div className="hotel-error-state">
        <p>⚠️ {error}</p>
        <button onClick={() => setIsManualMode(true)}>手动录入酒店信息</button>
        {isManualMode && (
          <ManualHotelEntry 
            onConfirm={handleManualConfirm} 
            onCancel={() => setIsManualMode(false)} 
          />
        )}
      </div>
    );
  }

  return (
    <div className="hotel-feature-wrapper">
      {data && (
        <HotelList 
          data={data} 
          onRefresh={handleRefresh} 
          onSelectAlternative={handleSelectAlternative}
        />
      )}
      
      <div className="feature-footer">
        <button className="btn-secondary" onClick={() => setIsManualMode(true)}>找不到满意的？手动录入</button>
      </div>

      {isManualMode && (
        <ManualHotelEntry 
          onConfirm={handleManualConfirm} 
          onCancel={() => setIsManualMode(false)} 
        />
      )}
    </div>
  );
};

export default HotelRecommendation;
