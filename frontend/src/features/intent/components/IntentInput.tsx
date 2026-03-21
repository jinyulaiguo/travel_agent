import React, { useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';

const IntentInput: React.FC = () => {
  const [text, setText] = useState('');
  const { intent, parseIntent, confirmIntent, triggerPlanning } = usePlanningStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      parseIntent(text);
      setText('');
    }
  };

  const handleConfirm = () => {
    confirmIntent();
  };

  const handleGenerate = () => {
    triggerPlanning();
  };

  return (
    <div className="intent-container" style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '2rem',
      background: 'var(--accent-bg)',
      borderRadius: '16px',
      border: '1px solid var(--accent-border)',
      boxShadow: 'var(--shadow)',
      textAlign: 'left'
    }}>
      <h2 style={{ color: 'var(--accent)', marginBottom: '1.5rem' }}>🌟 开启您的 AI 旅程</h2>
      
      {/* Search Input Area */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', marginBottom: '1.5rem' }}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="例如：我想五一去北京玩5天，预算1万，喜欢古建筑..."
          style={{
            flex: 1,
            padding: '12px 20px',
            borderRadius: '30px',
            border: '2px solid var(--border)',
            fontSize: '16px',
            outline: 'none',
            transition: 'border-color 0.3s',
            background: 'var(--bg)',
            color: 'var(--text-h)'
          }}
          disabled={intent.parsing}
        />
        <button
          type="submit"
          disabled={intent.parsing || !text.trim()}
          style={{
            padding: '12px 24px',
            borderRadius: '30px',
            border: 'none',
            background: 'var(--accent)',
            color: 'white',
            fontWeight: 'bold',
            cursor: 'pointer',
            opacity: (intent.parsing || !text.trim()) ? 0.6 : 1
          }}
        >
          {intent.parsing ? '解析中...' : '发送'}
        </button>
      </form>

      {/* Result Display */}
      {intent.result && (
        <div className="intent-result" style={{
          padding: '1.5rem',
          background: 'var(--bg)',
          borderRadius: '12px',
          border: '1px solid var(--border)'
        }}>
          {intent.result.clarification_message && (
            <div style={{ marginBottom: '1rem', color: 'var(--accent)', fontWeight: '500' }}>
              💡 {intent.result.clarification_message}
            </div>
          )}

          <div style={{ fontSize: '14px', color: 'var(--text)' }}>
            <strong>当前识别意图:</strong>
            <ul style={{ marginTop: '0.5rem', listStyle: 'none', padding: 0 }}>
              <li>📍 目的地: {intent.result.updated_intent.destinations?.map((d: any) => d.city).join(', ') || '未定'}</li>
              <li>📅 日期: {intent.result.updated_intent.departure_date || '未定'} 至 {intent.result.updated_intent.return_date || '未定'}</li>
              <li>👥 人数: {intent.result.updated_intent.travelers?.total || 1} 人</li>
              <li>💰 预算档次: {intent.result.updated_intent.preferences?.accommodation_tier || '未定'}</li>
            </ul>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '1.5rem' }}>
            {!intent.confirmed ? (
              <button
                onClick={handleConfirm}
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  background: '#10b981',
                  color: 'white',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                ✅ 确认意图
              </button>
            ) : (
              <button
                onClick={handleGenerate}
                style={{
                  padding: '12px 30px',
                  borderRadius: '30px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #aa3bff 0%, #6366f1 100%)',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '16px',
                  cursor: 'pointer',
                  boxShadow: '0 4px 15px rgba(170, 59, 255, 0.4)'
                }}
              >
                🚀 一键生成完整行程
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default IntentInput;
