import React, { useEffect, useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { StepCard } from '../../../components/common/StepCard';
import { MapPin, Calendar, Clock } from 'lucide-react';
import './destination.css';

interface DestinationItem {
    city: string;
    country_code: string;
    lat?: number;
    lng?: number;
    allocated_days: number;
    recommend_reason?: string;
    order: number;
}

export const DestinationSelection: React.FC = () => {
    const { 
        sessionId,
        nodes,
        stepStatus, 
        generateStep, 
        confirmStep, 
        setStepStatus 
    } = usePlanningStore();

    const [destinations, setDestinations] = useState<DestinationItem[]>([]);
    const [totalDays, setTotalDays] = useState(0);
    const [firstDayHours, setFirstDayHours] = useState(0);
    const [lastDayCutoff, setLastDayCutoff] = useState('');

    const isConfirmed = stepStatus.destination === 'confirmed';

    const fetchRecommendations = async () => {
        if (!sessionId) return;
        try {
            const data = await generateStep("destination", "/destination/recommend", "POST", { session_id: sessionId });
            if (data?.candidates) {
                setDestinations(data.candidates);
                setTotalDays(data.candidates.reduce((sum: number, d: any) => sum + d.allocated_days, 0));
            }
        } catch (e) {
            console.error("Destination fetch failed", e);
        }
    };

    useEffect(() => {
        if (stepStatus.destination === 'pending' && !nodes['L2_destination']?.data) {
            fetchRecommendations();
        } else if (nodes['L2_destination']?.data) {
            const data = nodes['L2_destination'].data;
            setDestinations(data.confirmed_destinations || []);
            setTotalDays(data.total_days || 0);
            setFirstDayHours(data.first_day_available_hours || 0);
            setLastDayCutoff(data.last_day_cutoff_time || '');
            
            if (nodes['L2_destination'].status === 'confirmed') {
                setStepStatus('destination', 'confirmed');
            }
        }
        // eslint-disable-next-line
    }, []);

    const updateDays = (index: number, delta: number) => {
        if (isConfirmed) return;
        const newDests = [...destinations];
        const newVal = newDests[index].allocated_days + delta;
        if (newVal >= 1) {
            newDests[index].allocated_days = newVal;
            setDestinations(newDests);
            setTotalDays(newDests.reduce((sum, d) => sum + d.allocated_days, 0));
        }
    };

    const handleConfirm = async () => {
        const body = {
            destinations: destinations,
            force_override: false
        };
        await confirmStep("destination", `/destination/confirm?session_id=${sessionId}`, body);
    };

    // Helper to get L1 data for the banner
    const flightData = nodes['L1_flight']?.data;
    const arrivalTime = flightData?.outbound?.arrival_time ? new Date(flightData.outbound.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null;
    const departureTime = flightData?.inbound?.departure_time ? new Date(flightData.inbound.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null;

    return (
        <StepCard
           title="目的地与停留确认"
           status={stepStatus.destination}
           dataSourceLabel="智能时长演算"
           dataSourceType="model"
           onRegenerate={!isConfirmed ? fetchRecommendations : undefined}
           onConfirm={!isConfirmed && destinations.length > 0 ? handleConfirm : undefined}
        >
            <div className="destination-container">
                {arrivalTime && (
                    <div className="destination-info-banner">
                        <Clock size={18} className="info-icon" />
                        <div className="info-text">
                            由于您于 <strong>{arrivalTime}</strong> 抵达，第一天有效游览时间约为 <strong>{firstDayHours || '--'}</strong> 小时。
                            {departureTime && <span> 末日行程建议在 <strong>{lastDayCutoff || '--'}</strong> 前结束。</span>}
                        </div>
                    </div>
                )}

                <div className="destination-list">
                    {destinations.length === 0 && stepStatus.destination !== 'isGenerating' && (
                        <p className="empty-msg">加载推荐目的地中...</p>
                    )}
                    
                    <div className="destination-items">
                        {destinations.map((dest, i) => (
                            <div key={i} className={`destination-item-card ${isConfirmed ? 'frozen' : ''}`}>
                                <div className="city-info">
                                    <MapPin size={16} className="pin-icon" />
                                    <span className="city-name">{dest.city}</span>
                                </div>
                                <div className="reason-area">
                                    <span className="reason-text">{dest.recommend_reason || '系统推荐目的地'}</span>
                                </div>
                                <div className="days-area">
                                    <div className="days-label">停留天数</div>
                                    <div className="days-control">
                                        <button 
                                            className="day-btn" 
                                            onClick={() => updateDays(i, -1)}
                                            disabled={isConfirmed || dest.allocated_days <= 1}
                                        >-</button>
                                        <span className="day-val">{dest.allocated_days}</span>
                                        <button 
                                            className="day-btn" 
                                            onClick={() => updateDays(i, 1)}
                                            disabled={isConfirmed}
                                        >+</button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {destinations.length > 0 && (
                    <div className="destination-summary">
                        <Calendar size={16} />
                        <span>总行程覆盖 <strong>{totalDays}</strong> 天</span>
                        {nodes['L1_flight']?.data && (
                             <span className="sync-tag"><CheckCircle size={12} /> 已同步交通时间轴</span>
                        )}
                    </div>
                )}
            </div>
        </StepCard>
    );
};

export default DestinationSelection;

// Supplementary icons
const CheckCircle = ({size}: {size: number}) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
);
