import React, { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Clock, MapPin, AlertCircle, Menu, GripVertical } from 'lucide-react';
import type { DailyItinerary, DailyItineraryItem } from '../../../types/daily_itinerary';
import { ConfidenceBadge } from '../../../components/Confidence';
import { TransitSegment } from './TransitSegment';
import { StepCard } from '../../../components/common/StepCard';
import MapRoute from './MapRoute';
import { usePlanningStore } from '../../../store/planningStore';
import './DailySchedule.css';

interface SortableItemProps {
  item: DailyItineraryItem;
  disabled?: boolean;
}

const SortableItem: React.FC<SortableItemProps> = ({ item, disabled }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: item.id || item.name, disabled });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getIcon = () => {
    switch (item.type) {
      case 'attraction': return <MapPin size={18} />;
      case 'fixed_slot': return <Clock size={18} />;
      case 'buffer': return <Menu size={18} />;
      default: return <MapPin size={18} />;
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`timeline-item ${disabled ? 'disabled' : ''}`}
    >
      <div {...attributes} {...listeners} className="drag-handle" style={{ cursor: disabled ? 'default' : 'grab' }}>
        {!disabled && <GripVertical size={20} />}
      </div>
      
      <div className="item-time">
        {item.planned_start_time}
      </div>
      
      <div className="item-content">
        <div className={`item-icon ${item.type}`}>
          {getIcon()}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span className="item-name">{item.name}</span>
            {item.confidence_level && <ConfidenceBadge level={item.confidence_level as any} />}
            {item.notes && (
              <span className="item-notes" style={{ display: 'flex', alignItems: 'center' }}>
                <AlertCircle size={10} style={{marginRight: '4px'}} />
                {item.notes}
              </span>
            )}
          </div>
          <div className="item-duration">
            预计游玩: {item.duration_hours}小时
          </div>
        </div>
      </div>
      
      <div className="item-end-time">
        {item.planned_end_time}
      </div>
    </div>
  );
};

const DailySchedule: React.FC = () => {
  const { 
      sessionId,
      nodes,
      intent,
      stepStatus, 
      generateStep, 
      confirmStep, 
      setStepStatus,
  } = usePlanningStore();

  const [itinerary, setItinerary] = useState<DailyItinerary | null>(null);
  const [selectedDay, setSelectedDay] = useState(0);
  const [isModified, setIsModified] = useState(false);

  const isConfirmed = stepStatus.schedule === 'confirmed';

  const fetchSchedule = async () => {
      if (!sessionId) return;
      try {
          const dests = intent.result?.updated_intent?.destinations?.map((d:any)=>d.city) || ['北京'];
          const body = {
             plan_id: sessionId,
             destination_cities: dests,
             start_date: intent.result?.updated_intent?.departure_date || new Date().toISOString().split('T')[0],
             end_date: intent.result?.updated_intent?.return_date || new Date().toISOString().split('T')[0]
          };
          const data = await generateStep("schedule", "/schedules/generate", "POST", body);
          setItinerary(data);
          setIsModified(false);
      } catch (e) {
          console.error("Schedule generation failed", e);
      }
  };

  useEffect(() => {
    if (stepStatus.schedule === 'pending' && !nodes['L5_itinerary']?.data) {
        fetchSchedule();
    } else if (nodes['L5_itinerary']?.data) {
        setItinerary(nodes['L5_itinerary'].data);
        if (nodes['L5_itinerary'].status === 'confirmed') {
            setStepStatus('schedule', 'confirmed');
        }
    }
    // eslint-disable-next-line
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id && itinerary) {
      setItinerary((prev) => {
        if (!prev) return prev;
        const newDays = [...prev.days];
        const day = { ...newDays[selectedDay] };
        const items = [...day.items];
        const oldIndex = items.findIndex((i) => (i.id || i.name) === active.id);
        const newIndex = items.findIndex((i) => (i.id || i.name) === over.id);
        
        day.items = arrayMove(items, oldIndex, newIndex);
        newDays[selectedDay] = day;
        return { ...prev, days: newDays };
      });
      setIsModified(true);
    }
  };

  const currentDay = itinerary?.days[selectedDay];

  const handleConfirm = async () => {
      if (!itinerary) return;
      const body = {
          plan_id: sessionId,
          itinerary: itinerary
      };
      await confirmStep("schedule", `/schedules/adjust`, body);
  };

  return (
    <StepCard
       title="每日行程编排"
       status={stepStatus.schedule}
       dataSourceLabel="知识库大语言模型 (L5)"
       dataSourceType="model"
       onRegenerate={!isConfirmed ? fetchSchedule : undefined}
       onConfirm={!isConfirmed && itinerary ? handleConfirm : undefined}
    >
      <div className="schedule-container" style={{ margin: 0, border: 'none', boxShadow: 'none', padding: 0 }}>
        {!itinerary ? (
            <div className="empty-msg" style={{ padding: '20px 0' }}>{stepStatus.schedule === 'isGenerating' ? '正在智能分配您的路线...' : '暂无数据'}</div>
        ) : (
            <>
                <div className="day-selector" style={{ marginBottom: '24px', display: 'inline-flex' }}>
                {itinerary.days.map((day, idx) => (
                    <button
                        key={day.day}
                        onClick={() => setSelectedDay(idx)}
                        className={`day-btn ${selectedDay === idx ? 'active' : ''}`}
                    >
                    Day {day.day}
                    </button>
                ))}
                </div>

                {currentDay && (
                <div className="itinerary-card" style={{ padding: '20px' }}>
                    <div className="itinerary-info">
                        <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                            <span className="date-badge">
                            {currentDay.date}
                            </span>
                            <span className="stats">
                            累计活动时长: <b>{currentDay.total_active_hours}h</b>
                            {currentDay.total_active_hours > 10 && (
                                <span style={{marginLeft: '12px', color: '#f43f5e', fontWeight: 'bold'}}>
                                ⚠️ 超出建议强度
                                </span>
                            )}
                            </span>
                        </div>
                    </div>

                    <MapRoute items={currentDay.items} />

                    <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={isConfirmed ? undefined : handleDragEnd}
                    >
                        <SortableContext
                            items={currentDay.items.map(i => i.id || i.name)}
                            strategy={verticalListSortingStrategy}
                        >
                            <div className="timeline">
                                {currentDay.items.map((item, idx) => (
                                    <React.Fragment key={item.id || item.name}>
                                        <SortableItem item={item} disabled={isConfirmed} />
                                        {idx < currentDay.items.length - 1 && (
                                            <TransitSegment mode="驾车" duration="30分钟" distance="5公里" />
                                        )}
                                    </React.Fragment>
                                ))}
                            </div>
                        </SortableContext>
                    </DndContext>
                    
                    {isModified && !isConfirmed && (
                        <div className="impact-alert">
                            <div className="alert-icon">
                                <AlertCircle size={24} />
                            </div>
                            <div>
                                <div className="alert-title">行程已调整</div>
                                <div className="alert-desc">
                                    注意：手动调整景点顺序后，原有的城市内交通（L6）规划将自动更新以匹配新的接驳路线。
                                </div>
                            </div>
                        </div>
                    )}
                </div>
                )}
            </>
        )}
      </div>
    </StepCard>
  );
};

export default DailySchedule;
