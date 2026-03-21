import React, { useState } from 'react';
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
import './DailySchedule.css';

interface SortableItemProps {
  item: DailyItineraryItem;
}

const SortableItem: React.FC<SortableItemProps> = ({ item }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getIcon = () => {
    switch (item.type) {
      case 'attraction': return <MapPin size={18} />;
      case 'fixed_slot': return <Clock size={18} />;
      case 'buffer': return <Menu size={18} />;
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="timeline-item"
    >
      <div {...attributes} {...listeners} className="drag-handle">
        <GripVertical size={20} />
      </div>
      
      <div className="item-time">
        {item.planned_start_time}
      </div>
      
      <div className="item-content">
        <div className={`item-icon ${item.type}`}>
          {getIcon()}
        </div>
        <div style={{ flex: 1 }}>
          <div className="flex items-center" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span className="item-name">{item.name}</span>
            {item.confidence_level && <ConfidenceBadge level={item.confidence_level} />}
            {item.notes && (
              <span className="item-notes" style={{ display: 'flex', alignItems: 'center' }}>
                <AlertCircle size={10} style={{marginRight: '4px'}} />
                {item.notes}
              </span>
            )}
          </div>
          <div className="item-duration">
            预计时长: {item.duration_hours}小时
          </div>
        </div>
      </div>
      
      <div className="item-end-time">
        {item.planned_end_time}
      </div>
    </div>
  );
};

interface DailyScheduleProps {
  initialData?: DailyItinerary;
}

const DailySchedule: React.FC<DailyScheduleProps> = ({ initialData }) => {
  const [itinerary, setItinerary] = useState<DailyItinerary>(initialData || { days: [] });
  const [selectedDay, setSelectedDay] = useState(0);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setItinerary((prev) => {
        const newDays = [...prev.days];
        const day = { ...newDays[selectedDay] };
        const items = [...day.items];
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        
        day.items = arrayMove(items, oldIndex, newIndex);
        
        // Simulating auto-recalculation
        newDays[selectedDay] = day;
        return { ...prev, days: newDays };
      });
      
      console.log('行程调整已保存，触发 STALE 标记...');
    }
  };

  const currentDay = itinerary.days[selectedDay];

  if (!currentDay) return <div className="p-10 text-center text-gray-400">暂无行程数据</div>;

  return (
    <div className="schedule-container">
      <div className="schedule-header">
        <div className="schedule-title">
          <h2>每日行程编排</h2>
          <div className="schedule-subtitle" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            L5 自动填充生成 | 支持手动微调
            <ConfidenceBadge level="L5" note="由大模型规划生成，建议核实具体时长" />
          </div>
        </div>
        
        <div className="day-selector">
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
      </div>

      <div className="itinerary-card">
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

        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={currentDay.items.map(i => i.id)}
            strategy={verticalListSortingStrategy}
          >
            <div className="timeline">
              {currentDay.items.map((item) => (
                <SortableItem key={item.id} item={item} />
              ))}
            </div>
          </SortableContext>
        </DndContext>
        
        <div className="impact-alert">
          <div className="alert-icon">
            <AlertCircle size={24} />
          </div>
          <div>
            <div className="alert-title">行程调整已保存</div>
            <div className="alert-desc">
              注意：手动调整景点顺序后，原有的城市内交通（L6）和行程费用（L8）规划将自动进入失效状态，需重新触发计算。
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailySchedule;
