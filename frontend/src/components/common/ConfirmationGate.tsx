import React from 'react';
import { usePlanningStore } from '../../store/planningStore';
import { Lock, Unlock, Check, RefreshCw, AlertTriangle } from 'lucide-react';
import './Interaction.css';

interface ConfirmationGateProps {
    nodeKey: string;
    title: string;
    children: React.ReactNode;
}

const ConfirmationGate: React.FC<ConfirmationGateProps> = ({ nodeKey, title, children }) => {
    const { nodes, confirmNode, lockNode, unlockNode, rollback } = usePlanningStore();
    const node = nodes[nodeKey];

    if (!node) return <div>Loading node {nodeKey}...</div>;

    const isHighlight = node.status === 'generated' || node.status === 'stale';
    const isLocked = node.locked;
    const isGenerating = node.status === 'generating';

    return (
        <div className={`confirmation-gate ${isHighlight ? 'highlight' : ''} ${isLocked ? 'locked' : ''} ${isGenerating ? 'generating' : ''}`}>
            <div className="gate-header">
                <span className="gate-title">{title}</span>
                <div className="gate-status-pill" data-status={node.status}>
                    {node.status.toUpperCase()}
                </div>
                {!isGenerating && (
                    <button 
                        className={`lock-button ${isLocked ? 'active' : ''}`}
                        onClick={() => isLocked ? unlockNode(nodeKey) : lockNode(nodeKey)}
                        title={isLocked ? "解锁节点" : "锁定节点"}
                    >
                        {isLocked ? <Lock size={16} /> : <Unlock size={16} />}
                    </button>
                )}
            </div>

            {node.compatibilityWarning && (
                <div className="compatibility-warning">
                    <AlertTriangle size={16} />
                    <span>{node.compatibilityWarning}</span>
                </div>
            )}

            <div className="gate-content">
                {isGenerating ? (
                    <div className="gate-skeleton">
                        <div className="skeleton-line full"></div>
                        <div className="skeleton-line half"></div>
                        <div className="skeleton-line last"></div>
                        <div className="skeleton-label">正在为您智能规划 {title}...</div>
                    </div>
                ) : children}
            </div>

            {isHighlight && (
                <div className="gate-footer">
                    <button className="gate-btn confirm" onClick={() => confirmNode(nodeKey, node.data)}>
                        <Check size={16} /> 确认建议
                    </button>
                    <button className="gate-btn modify" onClick={() => {/* Entry for manual edit */}}>
                        修改
                    </button>
                    <button className="gate-btn recalculate" onClick={() => rollback(nodeKey)}>
                        <RefreshCw size={16} /> 重新生成
                    </button>
                </div>
            )}
        </div>
    );
};

export default ConfirmationGate;
