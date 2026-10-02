import React from "react";
import { Citation } from "../types";

interface CitationsProps {
  citations: Citation[];
}

export const Citations: React.FC<CitationsProps> = ({ citations }) => {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="citations">
      <span className="citations-label">Citations:</span>
      {citations.map((citation) => (
        <span key={citation.citation_id} className="citation-link">
          [{citation.citation_id}]
        </span>
      ))}
    </div>
  );
};
