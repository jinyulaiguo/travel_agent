import React from 'react';
import { Clock, Tag } from 'lucide-react';
import './attractions.css';

export interface AttractionOption {
  id: string;
  name: string;
  english_name?: string;
  recommended_duration?: number;
  categories?: string[];
  description?: string;
}

interface AttractionCardProps {
  option: AttractionOption;
  selected: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export const AttractionCard: React.FC<AttractionCardProps> = ({ option, selected, onToggle, disabled }) => {
  return (
    <div 
      className={`attraction-card ${selected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={disabled ? undefined : onToggle}
    >
      <div className="ac-checkbox">
         <div className={`checkbox-outer ${selected ? 'active' : ''}`}>
           {selected && <div className="checkbox-inner"></div>}
         </div>
      </div>
      <div className="ac-content">
         <div className="ac-title">
           <span className="name">{option.name}</span>
           {option.english_name && <span className="en-name">{option.english_name}</span>}
         </div>
         <div className="ac-meta">
           {option.recommended_duration && (
             <span className="ac-duration">
               <Clock size={14} /> 建议游玩 {option.recommended_duration} 小时
             </span>
           )}
           {option.categories && option.categories.length > 0 && (
             <div className="ac-tags">
               <Tag size={12} />
               {option.categories.map((c, i) => (
                 <span key={i} className="ac-tag">{c}</span>
               ))}
             </div>
           )}
         </div>
         {option.description && <p className="ac-desc">{option.description}</p>}
      </div>
    </div>
  );
};
