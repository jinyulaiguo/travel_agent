import React, { useState } from 'react';
import { usePlanningStore } from '../../store/planningStore';
import { Zap, AlertCircle } from 'lucide-react';
import './Interaction.css';

const QuickModeButton: React.FC = () => {
    const { batchConfirm } = usePlanningStore();
    const [showConfirm, setShowConfirm] = useState(false);

    const handleConfirm = async () => {
        await batchConfirm();
        setShowConfirm(false);
        // Maybe toast notification
        alert("已自动确认所有建议并生成完整行程！");
    };

    return (
        <>
            <button className="quick-mode-btn" onClick={() => setShowConfirm(true)}>
                <Zap size={20} fill="currentColor" />
                <span>一键生成完整行程</span>
            </button>

            {showConfirm && (
                <div className="quick-mode-modal-overlay">
                    <div className="quick-mode-modal">
                        <AlertCircle size={40} color="#f59e0b" />
                        <h3>进入快速模式？</h3>
                        <p>系统将自动确认所有推荐方案，跳过逐步确认。您生成后仍可对细节进行修改。</p>
                        <div className="modal-actions">
                            <button className="modal-btn cancel" onClick={() => setShowConfirm(false)}>
                                取消
                            </button>
                            <button className="modal-btn proceed" onClick={handleConfirm}>
                                立即生成
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default QuickModeButton;
