import React, { useState } from 'react';
import { usePlanningStore } from '../../../store/planningStore';
import { StepCard } from '../../../components/common/StepCard';
import IntentForm from './IntentForm';
import './intent.css';
import { Send, Sparkles } from 'lucide-react';

const IntentInput: React.FC = () => {
  const [text, setText] = useState('');
  const { intent, parseIntent, confirmIntent, stepStatus } = usePlanningStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      parseIntent(text);
    }
  };

  const handleRegenerate = () => {
    if (text.trim() || intent.rawInput) {
        parseIntent(text.trim() || intent.rawInput);
    }
  };

  const handleConfirm = () => {
    confirmIntent();
  };

  // 状态适配
  // 如果没有任何解析结果且未在解析中，那是初始态，不需要显示卡片外壳，只需显示输入框即可
  const showCardMode = intent.result || stepStatus.intent === 'isGenerating';

  if (!showCardMode) {
     return (
        <div className="initial-intent-container">
            <h2 className="initial-intent-title"><Sparkles size={28} /> 开启您的 AI 旅程</h2>
            <form onSubmit={handleSubmit} className="initial-intent-form">
                <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="例如：我想五一去北京玩5天，预算1万，喜欢古建筑..."
                className="intent-search-input"
                />
                <button
                type="submit"
                disabled={!text.trim()}
                className="intent-search-btn"
                >
                <Send size={18} /> 发送
                </button>
            </form>
        </div>
     );
  }

  return (
    <StepCard 
       title="出行意图确认" 
       status={stepStatus.intent}
       dataSourceLabel="知识库大语言模型"
       dataSourceType="model"
       onRegenerate={intent.result && stepStatus.intent !== 'confirmed' ? handleRegenerate : undefined}
       onConfirm={intent.result && stepStatus.intent !== 'confirmed' ? handleConfirm : undefined}
    >
      {/* Search Input Area */}
      {stepStatus.intent !== 'confirmed' && (
          <form onSubmit={handleSubmit} className="intent-search-bar">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="修改自然语言意图并重新解析..."
              className="intent-search-input-small"
              disabled={stepStatus.intent === 'isGenerating'}
            />
            <button
              type="submit"
              disabled={stepStatus.intent === 'isGenerating' || !text.trim()}
              className="intent-search-btn-small"
            >
              {stepStatus.intent === 'isGenerating' ? '解析中...' : '重新解析'}
            </button>
          </form>
      )}

      {/* Result Display as Form */}
      {intent.result && (
        <div className="intent-result-form">
          {intent.result.clarification_message && intent.result.clarification_message !== 'null' && (
            <div className="clarification-msg">
              💡 {intent.result.clarification_message}
            </div>
          )}
          <IntentForm />
        </div>
      )}
    </StepCard>
  );
};

export default IntentInput;
