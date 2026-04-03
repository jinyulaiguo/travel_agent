import React from 'react';
import { Car } from 'lucide-react';

interface TransitSegmentProps {
  mode?: string;
  duration?: string;
  distance?: string;
}

export const TransitSegment: React.FC<TransitSegmentProps> = ({ 
  mode = "驾车", 
  duration = "30分钟", 
  distance = "5公里" 
}) => {
  return (
    <div className="transit-segment">
      <div className="transit-line-wrap">
        <div className="transit-line"></div>
      </div>
      <div className="transit-content">
        <div className="transit-badge">
           <Car size={12} />
           {mode} {duration} ({distance})
        </div>
      </div>
    </div>
  );
};
