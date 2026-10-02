import React from "react";
import { Evidence } from "../types";

interface EvidenceCardProps {
  evidence: Evidence;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence }) => {
  const sourceColors: Record<string, string> = {
    SEC: "#003DA5",
    earnings_call: "#0066CC",
    news: "#FF6B35",
    graph: "#6B35FF",
  };

  return (
    <div className="evidence-card">
      <div
        className="evidence-badge"
        style={{ backgroundColor: sourceColors[evidence.source] || "#999" }}
      >
        {evidence.source}
      </div>
      <div className="evidence-details">
        {evidence.ticker && (
          <span className="evidence-ticker">{evidence.ticker}</span>
        )}
        {evidence.date && <span className="evidence-date">{evidence.date}</span>}
      </div>
      <p className="evidence-text">{evidence.text.substring(0, 150)}...</p>
      {evidence.score && (
        <div className="evidence-score">Score: {evidence.score.toFixed(2)}</div>
      )}
    </div>
  );
};
