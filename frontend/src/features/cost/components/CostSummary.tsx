import React, { useEffect, useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { StepCard } from '../../../components/common/StepCard';
import { DonutChart } from './DonutChart';
import type { DataPoint } from './DonutChart';
import './cost.css';

const CATEGORY_MAP: Record<string, { label: string, color: string }> = {
  flight: { label: '大交通', color: '#3b82f6' },
  hotel: { label: '酒店住宿', color: '#10b981' },
  admission: { label: '景点门票', color: '#f59e0b' },
  transport: { label: '当地交通', color: '#8b5cf6' },
  dining: { label: '餐饮美食', color: '#ec4899' },
  misc: { label: '备用金/杂费', color: '#64748b' }
};

export const CostSummary: React.FC = () => {
    const { 
        sessionId,
        stepStatus, 
        generateStep, 
        setStepStatus,
        advanceStep
    } = usePlanningStore();

    const [summary, setSummary] = useState<any>(null);

    const isConfirmed = stepStatus.cost === 'confirmed';

    const fetchCost = async () => {
        if (!sessionId) return;
        try {
            const data = await generateStep("cost", `/cost/summary?session_id=${sessionId}`, "GET");
            setSummary(data);
        } catch (e) {
            console.error("Cost fetch failed:", e);
        }
    };

    useEffect(() => {
        if (stepStatus.cost === 'pending') {
            fetchCost();
        }
        // eslint-disable-next-line
    }, []);

    const handleConfirm = () => {
        setStepStatus('cost', 'confirmed');
        advanceStep();
    };

    const chartData: DataPoint[] = summary?.items?.map((item: any) => {
        const cat = CATEGORY_MAP[item.category] || { label: item.category, color: '#000' };
        return {
            label: cat.label,
            value: item.converted_amount_max_cny?.value || 0,
            color: cat.color
        };
    }) || [];

    return (
        <StepCard
           title="费用汇总"
           status={stepStatus.cost}
           dataSourceLabel="模型估算"
           dataSourceType="model"
           onRegenerate={!isConfirmed ? fetchCost : undefined}
           onConfirm={!isConfirmed && summary ? handleConfirm : undefined}
        >
            <div className="cost-summary-container">
                {summary ? (
                    <>
                        {summary.target_budget_cny && (
                            <div className="budget-comparison">
                                <div className="budget-target">
                                    您的预期预算: <b>¥{summary.target_budget_cny.toLocaleString()}</b>
                                </div>
                                {summary.budget_status_message && (
                                    <div className={`budget-status ${summary.total_min_cny > summary.target_budget_cny ? 'warning' : 'success'}`}>
                                        {summary.budget_status_message}
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="cost-total-display">
                            <span className="cost-total-label">方案预估总费用</span>
                            <h2 className="cost-total-value">
                                ¥{summary.total_min_cny?.toLocaleString()} ~ ¥{summary.total_max_cny?.toLocaleString()}
                            </h2>
                        </div>
                        
                        <div className="cost-details">
                            <div className="cost-chart-section">
                                <DonutChart data={chartData} size={200} strokeWidth={24} />
                            </div>
                            
                            <div className="cost-legend-section">
                                {summary.items?.map((item: any, idx: number) => {
                                    const cat = CATEGORY_MAP[item.category] || { label: item.category, color: '#cbd5e1' };
                                    const amount = item.converted_amount_max_cny?.value || 0;
                                    return (
                                        <div className="cost-legend-item" key={idx}>
                                            <div className="legend-marker" style={{ backgroundColor: cat.color }}></div>
                                            <div className="legend-info">
                                                <div className="legend-name">{cat.label} <span className="legend-desc">({item.description})</span></div>
                                            </div>
                                            <div className="legend-amount">
                                                ¥{amount.toLocaleString()}
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="empty-msg">正在生成总费用拆解表...</div>
                )}
            </div>
        </StepCard>
    );
};

export default CostSummary;
