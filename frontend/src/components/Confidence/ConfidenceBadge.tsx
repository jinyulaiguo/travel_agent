import React, { useState } from "react";
import { Info, AlertCircle, CheckCircle, Database, HelpCircle } from "lucide-react";
import { ConfidenceLevel } from "../../types/confidence";
import type { ConfidenceLevelType } from "../../types/confidence";

interface ConfidenceBadgeProps {
  level: ConfidenceLevelType;
  timestamp?: string;
  note?: string;
}

const CONFIDENCE_CONFIG: Record<ConfidenceLevelType, { label: string; color: string; icon: any; description: string }> = {
  [ConfidenceLevel.L1]: {
    label: "实时数据",
    color: "#52C41A",
    icon: CheckCircle,
    description: "数据来自实时接口查询（30分钟内）。",
  },
  [ConfidenceLevel.L2]: {
    label: "快照过期",
    color: "#FAAD14",
    icon: AlertCircle,
    description: "接口查询已超时效，可能与当前实际情况有偏差。",
  },
  [ConfidenceLevel.L3]: {
    label: "统计数据",
    color: "#8C8C8C",
    icon: Info,
    description: "基于历史统计数据（如延误率、平均价格等）。",
  },
  [ConfidenceLevel.L4]: {
    label: "知识库",
    color: "#1890FF",
    icon: Database,
    description: "来自经过验证的结构化知识库。",
  },
  [ConfidenceLevel.L5]: {
    label: "仅供参考",
    color: "#FA8C16",
    icon: HelpCircle,
    description: "基于模型估算或大模型内置知识，建议核实。",
  },
};

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ level, timestamp, note }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const config = CONFIDENCE_CONFIG[level];
  
  if (!config) {
    return null; // Don't crash if level is invalid
  }

  const Icon = config.icon;

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        position: "relative",
        cursor: "help",
      }}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "4px",
          padding: "2px 8px",
          borderRadius: "12px",
          backgroundColor: `${config.color}15`,
          border: `1px solid ${config.color}`,
          color: config.color,
          fontSize: "12px",
          fontWeight: 500,
          whiteSpace: "nowrap",
        }}
      >
        <Icon size={12} />
        {config.label}
      </div>

      {showTooltip && (
        <div
          style={{
            position: "absolute",
            bottom: "calc(100% + 8px)",
            left: "50%",
            transform: "translateX(-50%)",
            width: "220px",
            padding: "12px",
            backgroundColor: "#fff",
            border: "1px solid #e5e4e7",
            borderRadius: "8px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            zIndex: 1000,
            fontSize: "13px",
            color: "#6b6375",
            pointerEvents: "none",
          }}
        >
          <div style={{ fontWeight: 600, color: config.color, marginBottom: "4px" }}>
            {config.label}
          </div>
          <p style={{ margin: 0, lineHeight: "1.4" }}>{config.description}</p>
          {timestamp && (
            <div style={{ marginTop: "8px", fontSize: "11px", color: "#9ca3af" }}>
              查询时间: {timestamp}
            </div>
          )}
          {note && (
            <div style={{ marginTop: "4px", fontSize: "11px", color: "#9ca3af" }}>
              说明: {note}
            </div>
          )}
          {level === ConfidenceLevel.L5 && (
            <div
              style={{
                marginTop: "8px",
                padding: "4px 8px",
                backgroundColor: "#fff7ed",
                border: "1px solid #fed7aa",
                borderRadius: "4px",
                color: "#ea580c",
                fontWeight: 600,
                textAlign: "center",
              }}
            >
              仅供参考，建议核实
            </div>
          )}
          {/* Tooltip arrow */}
          <div
            style={{
              position: "absolute",
              top: "100%",
              left: "50%",
              transform: "translateX(-50%)",
              borderWidth: "8px",
              borderStyle: "solid",
              borderColor: "#fff transparent transparent transparent",
            }}
          />
        </div>
      )}
    </div>
  );
};
