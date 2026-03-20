import React from "react";
import { ShieldAlert } from "lucide-react";

export const DisclaimerBanner: React.FC = () => {
  return (
    <div
      style={{
        position: "sticky",
        bottom: 0,
        width: "100%",
        padding: "16px 24px",
        backgroundColor: "#fff7ed",
        borderTop: "1px solid #fed7aa",
        color: "#ea580c",
        fontSize: "14px",
        lineHeight: "1.6",
        zIndex: 2000,
        display: "flex",
        alignItems: "flex-start",
        gap: "12px",
        boxSizing: "border-box",
      }}
    >
      <ShieldAlert size={20} style={{ flexShrink: 0, marginTop: "2px" }} />
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, fontWeight: 500 }}>
          价格信息为查询时快照，实际以平台下单价格为准。景点开放时间以景点官方公告为准。
          签证及入境政策请前往官方渠道核实，本系统不提供签证建议。
        </p>
      </div>
    </div>
  );
};
