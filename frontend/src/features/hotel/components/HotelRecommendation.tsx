import React, { useState, useEffect } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { StepCard } from '../../../components/common/StepCard';
import type { HotelRecord, HotelSelection } from '../types';
import './hotel.css';

const HotelRecommendation: React.FC = () => {
    const { 
        sessionId,
        nodes,
        stepStatus, 
        generateStep, 
        confirmStep, 
        setStepStatus 
    } = usePlanningStore();

    const [hotels, setHotels] = useState<HotelRecord[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);

    const isConfirmed = stepStatus.hotel === 'confirmed';
    const selectedHotel = hotels.find(h => h.hotel_id === selectedId);

    const fetchHotels = async () => {
        if (!sessionId) return;
        try {
            const data: HotelSelection = await generateStep("hotel", `/hotels/recommend?session_id=${sessionId}`, "POST", {});
            
            const list = [];
            if (data.selected_hotel) list.push(data.selected_hotel);
            if (data.alternatives) list.push(...data.alternatives);
            
            setHotels(list);
            if (list.length > 0) setSelectedId(list[0].hotel_id);
        } catch (e) {
            console.error("Hotel fetch failed:", e);
        }
    };

    useEffect(() => {
        if (stepStatus.hotel === 'pending' && !nodes['L4_hotel']?.data) {
            fetchHotels();
        } else if (nodes['L4_hotel']?.data) {
            const data = nodes['L4_hotel'].data;
            const list = [];
            if (data.selected_hotel) list.push(data.selected_hotel);
            if (data.alternatives) list.push(...data.alternatives);
            setHotels(list);
            if (data.selected_hotel) setSelectedId(data.selected_hotel.hotel_id);
            
            if (nodes['L4_hotel'].status === 'confirmed') {
                setStepStatus('hotel', 'confirmed');
            }
        }
        // eslint-disable-next-line
    }, []);

    const handleConfirm = async () => {
        if (!selectedHotel) return;
        const body = {
            selected_hotel: selectedHotel,
            alternatives: hotels.filter(h => h.hotel_id !== selectedId),
            recommended_area: selectedHotel.area || "默认区域",
            area_rationale: selectedHotel.rationale || "用户选择"
        };
        await confirmStep("hotel", `/hotels/confirm?session_id=${sessionId}`, body);
    };

    return (
        <StepCard
           title="酒店推荐"
           status={stepStatus.hotel}
           dataSourceLabel="实时数据（刚刚）"
           dataSourceType="realtime"
           onRegenerate={!isConfirmed ? fetchHotels : undefined}
           onConfirm={!isConfirmed && selectedHotel ? handleConfirm : undefined}
        >
            <div className="hotel-list">
                {hotels.length === 0 && stepStatus.hotel !== 'isGenerating' && (
                    <p className="empty-msg">正在搜索最优酒店...</p>
                )}
                <div className="hotel-options" style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
                    {hotels.map(h => {
                        const isSelected = selectedId === h.hotel_id;
                        return (
                            <div 
                               key={h.hotel_id} 
                               className={`hotel-card ${isSelected ? 'selected' : ''} ${isConfirmed ? 'disabled' : ''}`}
                               onClick={() => !isConfirmed && setSelectedId(h.hotel_id)}
                               style={{
                                   display: 'flex',
                                   alignItems: 'center',
                                   gap: '16px',
                                   padding: '16px 20px',
                                   border: `1px solid ${isSelected ? '#3b82f6' : '#e2e8f0'}`,
                                   borderRadius: '12px',
                                   cursor: isConfirmed ? 'default' : 'pointer',
                                   background: isSelected ? '#eff6ff' : '#fff',
                                   transition: 'all 0.2s ease',
                                   boxShadow: isSelected ? '0 0 0 1px inset #3b82f6' : 'none',
                                   opacity: isConfirmed && !isSelected ? 0.6 : 1
                               }}
                            >
                                <div className="hc-radio">
                                   <div className={`radio-outer ${isSelected ? 'active' : ''}`} style={{
                                       width: 20, height: 20, borderRadius: '50%', border: `2px solid ${isSelected ? '#3b82f6' : '#cbd5e1'}`,
                                       display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff'
                                   }}>
                                     {isSelected && <div className="radio-inner" style={{width: 10, height: 10, borderRadius: '50%', background: '#3b82f6'}} />}
                                   </div>
                                </div>
                                <div className="hc-content" style={{ flex: 1 }}>
                                    <div className="hc-title" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                                        <span className="hc-name" style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>{h.name}</span>
                                        {h.ota_rating && <span className="hc-rating" style={{ fontSize: '12px', color: '#059669', background: '#ecfdf5', padding: '2px 8px', borderRadius: '4px', fontWeight: '600' }}>评分 {h.ota_rating}</span>}
                                    </div>
                                    <div className="hc-desc" style={{ fontSize: '13px', color: '#64748b', lineHeight: 1.5 }}>
                                        📍 {h.rationale || h.area || '暂无推荐理由'}
                                    </div>
                                </div>
                                <div className="hc-price" style={{ textAlign: 'right', minWidth: '80px' }}>
                                    <div className="price-val" style={{ fontSize: '1.25rem', fontWeight: '700', color: '#f59e0b' }}>¥{(h.price_per_night as any).value ?? h.price_per_night}</div>
                                    <div className="price-unit" style={{ fontSize: '12px', color: '#94a3b8' }}>/ 晚</div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>
        </StepCard>
    );
};

export default HotelRecommendation;
