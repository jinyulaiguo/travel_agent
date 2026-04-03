import React, { ReactNode } from 'react';
import { RefreshCw, CheckCircle } from 'lucide-react';
import './StepCard.css';

export interface StepCardProps {
  title: string;
  status: 'pending' | 'isGenerating' | 'confirmed';
  dataSourceLabel?: string;
  dataSourceType?: 'realtime' | 'knowledge' | 'model';
  onRegenerate?: () => void;
  onConfirm?: () => void;
  children: ReactNode;
}

export const StepCard: React.FC<StepCardProps> = ({
  title,
  status,
  dataSourceLabel,
  dataSourceType,
  onRegenerate,
  onConfirm,
  children
}) => {
  return (
    <div className={`step-card ${status}`}>
      <div className="step-card-header">
        <div className="step-card-title-area">
          <h2>{title}</h2>
          {status === 'pending' && <span className="status-badge pending">【需确认】</span>}
          {status === 'isGenerating' && <span className="status-badge generating">生成中...</span>}
          {status === 'confirmed' && <span className="status-badge confirmed">【已确认】</span>}
        </div>
        {dataSourceLabel && (
          <div className={`data-source-badge ${dataSourceType || 'default'}`}>
            {dataSourceType === 'realtime' && '⊙ '}
            {dataSourceType === 'knowledge' && '📋 '}
            {dataSourceType === 'model' && '✨ '}
            {dataSourceLabel}
          </div>
        )}
      </div>

      <div className="step-card-content">
        {children}
      </div>

      {status !== 'confirmed' && (
        <div className="step-card-footer">
          {onRegenerate && (
             <button 
               className="btn-regenerate" 
               onClick={onRegenerate} 
               disabled={status === 'isGenerating'}
             >
               <RefreshCw size={16} /> 重新生成
             </button>
          )}
          {onConfirm && (
             <button 
               className="btn-confirm" 
               onClick={onConfirm}
               disabled={status === 'isGenerating'}
             >
               <CheckCircle size={16} /> 确认此方案
             </button>
          )}
        </div>
      )}
    </div>
  );
};
