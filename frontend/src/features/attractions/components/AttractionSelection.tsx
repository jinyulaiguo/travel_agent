import React, { useEffect, useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { StepCard } from '../../../components/common/StepCard';
import { AttractionCard } from './AttractionCard';
import type { AttractionOption } from './AttractionCard';
import './attractions.css';

export const AttractionSelection: React.FC = () => {
    const { 
        sessionId,
        nodes,
        stepStatus, 
        generateStep, 
        confirmStep, 
        setStepStatus 
    } = usePlanningStore();

    const [attractions, setAttractions] = useState<any[]>([]); // original backend ConfirmedAttraction
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

    const isConfirmed = stepStatus.attraction === 'confirmed';

    const fetchAttractions = async () => {
        if (!sessionId) return;
        try {
            const data = await generateStep("attraction", `/attractions/recommend?session_id=${sessionId}`, "POST", {});
            
            // Match backend AttractionList response model
            const rawList = data?.confirmed_attractions || [];
            
            setAttractions(rawList);
            // Default to empty selection instead of all to allow manual selection
            setSelectedIds(new Set());
        } catch (e) {
            console.error("Attraction fetch failed", e);
        }
    };

    useEffect(() => {
        if (stepStatus.attraction === 'pending' && !nodes['L3_attractions']?.data) {
            fetchAttractions();
        } else if (nodes['L3_attractions']?.data) {
            const data = nodes['L3_attractions'].data;
            const rawList = data.confirmed_attractions || [];
            
            setAttractions(rawList);
            const savedIds = new Set<string>();
            rawList.forEach((a: any) => {
                const id = a.attraction_id || a.id;
                if (id) savedIds.add(id);
            });
            setSelectedIds(savedIds);
            
            if (nodes['L3_attractions'].status === 'confirmed') {
                setStepStatus('attraction', 'confirmed');
            }
        }
        // eslint-disable-next-line
    }, []);

    const toggleSelect = (id: string) => {
        const newSet = new Set(selectedIds);
        if (newSet.has(id)) {
            newSet.delete(id);
        } else {
            newSet.add(id);
        }
        setSelectedIds(newSet);
    };

    const handleConfirm = async () => {
        const selectedAttractions = attractions.filter((a) => {
            const id = a.attraction_id || a.id;
            return selectedIds.has(id);
        });
        const body = {
            confirmed_attractions: selectedAttractions,
            total_estimated_hours: selectedAttractions.reduce((acc, curr) => acc + (curr.suggested_duration_hours || 0), 0)
        };
        await confirmStep("attraction", `/attractions/confirm?session_id=${sessionId}`, body);
    };

    return (
        <StepCard
           title="景点规划"
           status={stepStatus.attraction}
           dataSourceLabel="知识库 (2023-10)"
           dataSourceType="knowledge"
           onRegenerate={!isConfirmed ? fetchAttractions : undefined}
           onConfirm={!isConfirmed && selectedIds.size > 0 ? handleConfirm : undefined}
        >
            <div className="attraction-list">
                {attractions.length === 0 && stepStatus.attraction !== 'isGenerating' && (
                    <p className="empty-msg">正在生成推荐景点...</p>
                )}
                <div className="attraction-grid">
                    {attractions.map((a, i) => {
                        const id = a.attraction_id || a.id || String(i);
                        const opt: AttractionOption = {
                            id: id,
                            name: a.name,
                            english_name: a.english_name || "",
                            recommended_duration: a.suggested_duration_hours,
                            categories: a.attraction_tags,
                            description: a.notes
                        };
                        return (
                           <AttractionCard 
                               key={id} 
                               option={opt} 
                               selected={selectedIds.has(id)}
                               onToggle={() => toggleSelect(id)}
                               disabled={isConfirmed}
                           />
                        )
                    })}
                </div>
            </div>
            {attractions.length > 0 && (
                <div className="attraction-summary">
                    已选: <strong>{selectedIds.size}</strong> 个景点
                </div>
            )}
        </StepCard>
    );
};

export default AttractionSelection;
