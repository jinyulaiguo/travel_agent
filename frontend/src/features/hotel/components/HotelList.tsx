import React, { useState, useEffect } from 'react';
import type { HotelSelection, HotelRecord } from '../types';
import './hotel.css';

interface HotelListProps {
  data: HotelSelection;
  onRefresh: () => void;
  onSelectAlternative: (hotel: HotelRecord) => void;
}

const HotelList: React.FC<HotelListProps> = ({ data, onRefresh, onSelectAlternative }) => {
  const { selected_hotel, alternatives, recommended_area, area_rationale } = data;
  const [timeLeft, setTimeLeft] = useState<number>(1800); // 30 minutes in seconds

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const isExpired = timeLeft === 0;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="hotel-list-container">
      <div className="area-recommendation">
        <h3>📍 推荐住宿区域：{recommended_area}</h3>
        <p className="rationale">{area_rationale}</p>
      </div>

      {selected_hotel && (
        <div className="selected-hotel-card">
          <div className="card-header">
            <span className="badge-primary">首选推荐</span>
            {isExpired && <span className="badge-warning">⚠️ 价格可能过期，建议刷新</span>}
            <span className="snapshot-time">
              价格快照：{new Date(selected_hotel.price_snapshot_time).toLocaleTimeString()} 
              ({formatTime(timeLeft)})
            </span>
          </div>
          
          <div className="hotel-info">
            <div className="main-info">
              <h4>{selected_hotel.name}</h4>
              <p className="area-text">{selected_hotel.area} · 距离重心 {selected_hotel.distance_to_cluster_center_km}km</p>
              <div className="rating">
                <span className="score">{selected_hotel.ota_rating}</span>
                <span className="source">/ 10 ({selected_hotel.ota_source})</span>
              </div>
            </div>
            
            <div className="price-info">
              <p className="price">¥{selected_hotel.price_per_night}<span> / 晚</span></p>
              <a href={selected_hotel.booking_url} target="_blank" rel="noopener noreferrer" className="btn-book">立即预订</a>
            </div>
          </div>

          <div className="amenities">
            {selected_hotel.amenities.slice(0, 4).map((a, i) => (
              <span key={i} className="amenity-tag">{a}</span>
            ))}
          </div>

          <div className="rationale-box">
             <p><strong>推荐理由：</strong>{selected_hotel.rationale}</p>
          </div>

          <button className="btn-refresh" onClick={onRefresh}>刷新价格</button>
        </div>
      )}

      {alternatives.length > 0 && (
        <div className="alternatives-section">
          <h5>更多备选方案</h5>
          <div className="alternatives-grid">
            {alternatives.map((hotel) => (
              <div key={hotel.hotel_id} className="alt-card">
                <div className="alt-header">
                  <h6>{hotel.name}</h6>
                  <span className="alt-price">¥{hotel.price_per_night}</span>
                </div>
                <p>{hotel.ota_rating}分 · {hotel.distance_to_cluster_center_km}km</p>
                <button className="btn-switch" onClick={() => onSelectAlternative(hotel)}>替换为此酒店</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="disclaimer">※ 酒店价格为查询时快照，实际以平台下单价格为准。</p>
    </div>
  );
};

export default HotelList;
