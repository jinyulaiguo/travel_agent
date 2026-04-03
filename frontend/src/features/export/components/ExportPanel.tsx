import React, { useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { Download, Share2, FileText, CheckCircle } from 'lucide-react';
import './ExportPanel.css';

const ExportPanel: React.FC = () => {
  const { sessionId } = usePlanningStore();
  const [isExporting, setIsExporting] = useState(false);
  const [showDialog, setShowDialog] = useState(false);

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      alert("行程计划PDF已准备就绪，开始下载！");
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = () => {
    setShowDialog(true);
  };

  return (
    <div className="export-panel">
      <div className="export-header">
        <div className="success-icon"><CheckCircle size={40} /></div>
        <h2>完美！您的专属行程已生成完毕</h2>
        <p className="export-desc">我们已经为您打包好了所有交通、住宿和景点细节，赶快开始您的旅程吧！</p>
      </div>
      
      <div className="export-actions">
        <button 
          className="export-btn primary"
          onClick={handleExportPDF}
          disabled={isExporting}
        >
          <Download size={18} />
          {isExporting ? '生成PDF中...' : '下载PDF行程单'}
        </button>
        
        <button 
          className="export-btn secondary"
          onClick={handleShare}
        >
          <Share2 size={18} />
          分享给旅伴
        </button>
        
        <button className="export-btn outline">
          <FileText size={18} />
          导出到日历
        </button>
      </div>

      {showDialog && (
        <div className="share-dialog-overlay" onClick={() => setShowDialog(false)}>
          <div className="share-dialog" onClick={e => e.stopPropagation()}>
            <h3>🔗 分享行程</h3>
            <p className="dialog-desc">复制以下链接发送给您的旅伴，他们可以直接在浏览器中查看此行程。</p>
            <div className="share-link-box">
              <code>https://travel.antigravity.com/plan/{sessionId || 'demo123'}</code>
            </div>
            <button className="copy-btn" onClick={() => {
                navigator.clipboard.writeText(`https://travel.antigravity.com/plan/${sessionId || 'demo123'}`);
                alert("链接已复制！");
                setShowDialog(false);
            }}>复制链接</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportPanel;
