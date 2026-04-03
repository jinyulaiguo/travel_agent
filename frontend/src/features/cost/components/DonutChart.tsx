import React from 'react';

export interface DataPoint {
  label: string;
  value: number;
  color: string;
}

interface DonutChartProps {
  data: DataPoint[];
  size?: number;
  strokeWidth?: number;
}

export const DonutChart: React.FC<DonutChartProps> = ({ 
  data, 
  size = 200, 
  strokeWidth = 24 
}) => {
  const center = size / 2;
  const radius = center - strokeWidth / 2;
  const circumference = 2 * Math.PI * radius;

  let currentOffset = 0;
  
  const total = data.reduce((acc, d) => acc + d.value, 0);

  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="transparent"
          stroke="#f1f5f9"
          strokeWidth={strokeWidth}
        />
        
        {data.map((d, i) => {
          const percentage = total > 0 ? d.value / total : 0;
          if (percentage === 0) return null;
          
          const dashArray = `${percentage * circumference} ${circumference}`;
          const dashOffset = -currentOffset * circumference;
          
          currentOffset += percentage;

          return (
            <circle
              key={i}
              cx={center}
              cy={center}
              r={radius}
              fill="transparent"
              stroke={d.color}
              strokeWidth={strokeWidth}
              strokeDasharray={dashArray}
              strokeDashoffset={dashOffset}
              transform={`rotate(-90 ${center} ${center})`}
              style={{ transition: 'all 0.5s ease', strokeLinecap: 'round' }}
            />
          );
        })}
      </svg>
    </div>
  );
};
