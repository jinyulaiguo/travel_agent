import React from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import DailySchedule from '../../daily_schedule/components/DailySchedule';
import HotelRecommendation from '../../hotel/components/HotelRecommendation';

const TravelItinerary: React.FC = () => {
  const { nodes } = usePlanningStore();
  
  // Only show if we have some data generated
  const hasData = Object.keys(nodes).length > 0;

  if (!hasData) return null;

  return (
    <div className="itinerary-summary" style={{ textAlign: 'left', padding: '2rem' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '3rem' }}>🌍 您的定制旅行计划</h1>
      
      {/* 1. Destination & Overview */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{
          padding: '2rem',
          background: 'var(--accent-bg)',
          borderRadius: '16px',
          borderLeft: '8px solid var(--accent)'
        }}>
          <h2>📍 目的地概览</h2>
          <p style={{ fontSize: '1.2rem', marginTop: '1rem' }}>
            {nodes['L2_destination']?.data?.description || nodes['L1_destinations']?.data?.description || "计划前往北京，开启一场融合历史与现代的文化之旅。"}
          </p>
        </div>
      </section>

      {/* 2. Flights/Transport */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '2rem' }}>✈️</span>
          <h2>大交通安排</h2>
        </div>
        <div style={{ padding: '1rem', border: '1px solid var(--border)', borderRadius: '12px', marginTop: '1rem' }}>
          {nodes['L6_transport']?.status === 'generating' ? (
            <p>正在为您规划最有路线...</p>
          ) : (
            <p>已为您锁定最佳往返航班/高铁方案。</p>
          )}
        </div>
      </section>

      {/* 3. Hotel Accommodation */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '2rem' }}>🏨</span>
          <h2>下榻酒店</h2>
        </div>
        <div style={{ marginTop: '1rem' }}>
          <HotelRecommendation />
        </div>
      </section>

      {/* 4. Daily Itinerary */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '2rem' }}>📅</span>
          <h2>每日详细行程</h2>
        </div>
        <div style={{ marginTop: '1rem' }}>
          <DailySchedule initialData={nodes['L5_itinerary']?.data} />
        </div>
      </section>

      {/* 5. Budget & Cost */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{ 
          padding: '2rem', 
          background: 'var(--code-bg)', 
          borderRadius: '16px',
          border: '1px dashed var(--accent)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>💰 预计总费用</h2>
            <span style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
              ¥ {nodes['L8_cost']?.data?.total || '8,500'}
            </span>
          </div>
          <p style={{ marginTop: '1rem', fontSize: '14px', color: 'var(--text)' }}>
            * 包含大交通、酒店、餐饮及景点门票预估费用。
          </p>
        </div>
      </section>

      <div style={{ textAlign: 'center', marginTop: '4rem' }}>
        <button style={{
          padding: '12px 40px',
          borderRadius: '30px',
          border: 'none',
          background: 'var(--text-h)',
          color: 'var(--bg)',
          fontWeight: 'bold',
          cursor: 'pointer'
        }}>
          📥 导出 PDF 行程单
        </button>
      </div>
    </div>
  );
};

export default TravelItinerary;
