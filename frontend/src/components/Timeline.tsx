import React from "react";

export const Timeline: React.FC = () => {
  return (
    <div className="timeline-container">
      <div className="timeline">
        <div className="timeline-marker">
          <span className="timeline-date">2025 Q2</span>
          <span className="timeline-label">Initial statement</span>
        </div>
        <div className="timeline-line"></div>
        <div className="timeline-marker">
          <span className="timeline-date">2025 Q4</span>
          <span className="timeline-label">Change detected</span>
        </div>
        <div className="timeline-line"></div>
        <div className="timeline-marker">
          <span className="timeline-date">2026 Q1</span>
          <span className="timeline-label">Latest statement</span>
        </div>
      </div>
    </div>
  );
};
