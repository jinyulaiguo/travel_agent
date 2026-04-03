import React from 'react';
import { Plane, Train } from 'lucide-react';
import './transport.css';

export interface TransportOption {
  flight_id: string;
  flight_no: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  price: number;
  airline: string;
  transport_type?: string;
  ota_source?: string;
}

interface TransportCardProps {
  option: TransportOption;
  selected: boolean;
  onSelect: () => void;
  disabled?: boolean;
}

const formatTime = (isoString: string) => {
  if (!isoString) return '--:--';
  const d = new Date(isoString);
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const formatDuration = (mins: number) => {
  if (!mins) return '--';
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return `${h > 0 ? h + 'h' : ''}${m}m`;
};

export const TransportCard: React.FC<TransportCardProps> = ({ option, selected, onSelect, disabled }) => {
  const isTrain = option.transport_type === 'train';

  return (
    <div 
      className={`transport-card ${selected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`} 
      onClick={disabled ? undefined : onSelect}
    >
      <div className="tc-radio">
         <div className={`radio-outer ${selected ? 'active' : ''}`}>
           {selected && <div className="radio-inner" />}
         </div>
      </div>
      <div className="tc-content">
         <div className="tc-time-row">
            <div className="time-block">
               <span className="time">{formatTime(option.departure_time)}</span>
            </div>
            <div className="duration-block">
               <span className="duration-text">{formatDuration(option.duration_minutes)}</span>
               <div className="duration-line">
                 <div className="line-bar"></div>
                 {isTrain ? <Train size={14} className="icon-train" /> : <Plane size={14} className="icon-plane" />}
               </div>
               <span className="airline">{option.airline} {option.flight_no}</span>
            </div>
            <div className="time-block right">
               <span className="time">{formatTime(option.arrival_time)}</span>
            </div>
         </div>
      </div>
      <div className="tc-price">
         <span className="price-val">¥{option.price}</span>
         {option.ota_source && <span className="ota-source">{option.ota_source}</span>}
      </div>
    </div>
  );
};
