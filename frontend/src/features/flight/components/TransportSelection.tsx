import React, { useEffect, useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { StepCard } from '../../../components/common/StepCard';
import { TransportCard } from './TransportCard';
import type { TransportOption } from './TransportCard';
import './transport.css';

export const TransportSelection: React.FC = () => {
    const { 
        intent,
        nodes,
        sessionId,
        stepStatus, 
        generateStep, 
        confirmStep, 
        setStepStatus 
    } = usePlanningStore();

    const [outboundList, setOutboundList] = useState<TransportOption[]>([]);
    const [inboundList, setInboundList] = useState<TransportOption[]>([]);
    const [selectedOutbound, setSelectedOutbound] = useState<string | null>(null);
    const [selectedInbound, setSelectedInbound] = useState<string | null>(null);

    const isConfirmed = stepStatus.flight === 'confirmed';
    
    const outboundOpt = outboundList.find(o => o.flight_id === selectedOutbound);
    const inboundOpt = inboundList.find(o => o.flight_id === selectedInbound);
    const totalPrice = (outboundOpt?.price || 0) + (inboundOpt?.price || 0);

    const needsInbound = intent.result?.updated_intent?.return_date;

    const fetchFlights = async () => {
        if (!intent.result) return;
        const origin = intent.result.updated_intent.origin?.city || '北京';
        const dest = intent.result.updated_intent.destinations?.[0]?.city || '上海';
        const date = intent.result.updated_intent.departure_date;
        const return_date = intent.result.updated_intent.return_date;
        const travelers = intent.result.updated_intent.travelers?.total || 1;

        if (!date) return;

        try {
            const data = await generateStep("flight", "/flights/search", "POST", {
                origin,
                destination: dest,
                date,
                return_date,
                passengers: travelers
            });
            const cands = data?.candidates || [];
            
            // Filter by date or fallback mapping
            const outbound = cands.filter((c: any) => c.departure_time?.startsWith(date));
            const inbound = return_date ? cands.filter((c: any) => c.departure_time?.startsWith(return_date)) : [];
            
            const finalOutbound = outbound.length > 0 ? outbound : cands;
            setOutboundList(finalOutbound);
            setInboundList(inbound);
            
            if (finalOutbound.length > 0) setSelectedOutbound(finalOutbound[0].flight_id);
            if (inbound.length > 0) setSelectedInbound(inbound[0].flight_id);

        } catch (e) {
            console.error("Flight fetch failed", e);
        }
    };

    useEffect(() => {
        if (stepStatus.flight === 'pending' && !nodes['L1_flight']?.data) {
            fetchFlights();
        } else if (nodes['L1_flight']?.data) {
            const data = nodes['L1_flight'].data;
            if (data.outbound) {
                setOutboundList([data.outbound]);
                setSelectedOutbound(data.outbound.flight_id);
            }
            if (data.inbound) {
                setInboundList([data.inbound]);
                setSelectedInbound(data.inbound.flight_id);
            }
            if (nodes['L1_flight'].status === 'confirmed') {
                setStepStatus('flight', 'confirmed');
            }
        }
        // eslint-disable-next-line
    }, []);

    const handleConfirm = async () => {
        if (!outboundOpt) return;
        const body = {
            outbound: outboundOpt,
            inbound: inboundOpt || null,
            is_locked: true,
            confidence_level: "L1", 
            visa_reminder_shown: false
        };
        await confirmStep("flight", `/flights/anchor/confirm?session_id=${sessionId}`, body);
    };

    return (
        <StepCard
           title="大交通选择"
           status={stepStatus.flight}
           dataSourceLabel="实时数据（刚刚）"
           dataSourceType="realtime"
           onRegenerate={!isConfirmed ? fetchFlights : undefined}
           onConfirm={!isConfirmed && outboundOpt ? handleConfirm : undefined}
        >
            <div className={`transport-layout ${needsInbound ? 'two-cols' : 'one-col'}`}>
                <div className="transport-column">
                   <h3 className="column-title">去程·{intent.result?.updated_intent?.departure_date}</h3>
                   <div className="transport-list">
                      {outboundList.length === 0 && stepStatus.flight !== 'isGenerating' && <p className="empty-msg">暂无去程数据</p>}
                      {outboundList.map(opt => (
                         <TransportCard 
                            key={opt.flight_id} 
                            option={opt} 
                            selected={selectedOutbound === opt.flight_id}
                            onSelect={() => setSelectedOutbound(opt.flight_id)}
                            disabled={isConfirmed}
                         />
                      ))}
                   </div>
                </div>

                {needsInbound && (
                    <div className="transport-column">
                       <h3 className="column-title">返程·{intent.result?.updated_intent?.return_date}</h3>
                       <div className="transport-list">
                          {inboundList.length === 0 && stepStatus.flight !== 'isGenerating' && <p className="empty-msg">暂无返程数据</p>}
                          {inboundList.map(opt => (
                             <TransportCard 
                                key={opt.flight_id} 
                                option={opt} 
                                selected={selectedInbound === opt.flight_id}
                                onSelect={() => setSelectedInbound(opt.flight_id)}
                                disabled={isConfirmed}
                             />
                          ))}
                       </div>
                    </div>
                )}
            </div>

            <div className="transport-summary">
                <span className="summary-label">已选交通总价</span>
                <span className="summary-price">¥{totalPrice.toLocaleString()} / 人</span>
            </div>
        </StepCard>
    );
};

export default TransportSelection;
