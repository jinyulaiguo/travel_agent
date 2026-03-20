import React, { useState } from 'react';
import type { HotelRecord } from '../types';
import '../hotel.css';

interface ManualHotelEntryProps {
  onConfirm: (hotel: HotelRecord) => void;
  onCancel: () => void;
}

const ManualHotelEntry: React.FC<ManualHotelEntryProps> = ({ onConfirm, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    area: '',
    price: '',
    rating: '',
    source: 'Manual Input'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.area) return;

    const manualHotel: HotelRecord = {
      hotel_id: `manual_${Date.now()}`,
      name: formData.name,
      area: formData.area,
      coordinates: { lat: 0, lng: 0 }, // Placeholder
      price_per_night: {
        value: parseFloat(formData.price) || 0,
        confidence_level: 'L5',
        note: '用户手动录入'
      },
      price_snapshot_time: new Date().toISOString(),
      ota_rating: parseFloat(formData.rating) || 5.0,
      ota_source: formData.source,
      distance_to_cluster_center_km: 0,
      booking_url: '#',
      confidence_level: 'L5',
      is_locked: true,
      is_manual_input: true,
      amenities: [],
      rationale: '用户手动录入'
    };

    onConfirm(manualHotel);
  };

  return (
    <div className="manual-entry-overlay">
      <div className="manual-entry-modal">
        <h4>手动录入酒店信息</h4>
        <p className="subtitle">当自动查询不可用时，您可以手动输入已知的酒店详情。</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>酒店名称 *</label>
            <input 
              type="text" 
              required 
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="例如：巴黎香格里拉大酒店"
            />
          </div>

          <div className="form-group">
            <label>住宿区域/地址 *</label>
            <input 
              type="text" 
              required 
              value={formData.area}
              onChange={(e) => setFormData({...formData, area: e.target.value})}
              placeholder="例如：埃菲尔铁塔周边 / 第16区"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>每晚价格 (¥)</label>
              <input 
                type="number" 
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>评分 (0-10)</label>
              <input 
                type="number" 
                step="0.1" 
                min="0" 
                max="10"
                value={formData.rating}
                onChange={(e) => setFormData({...formData, rating: e.target.value})}
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-cancel" onClick={onCancel}>取消</button>
            <button type="submit" className="btn-confirm">确认提交</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ManualHotelEntry;
