import React from "react";
import { Answer } from "../types";
import { Citations } from "./Citations";

interface AnswerDisplayProps {
  answer: Answer | null;
  loading?: boolean;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({
  answer,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="answer-container">
        <div className="loading">Generating answer...</div>
      </div>
    );
  }

  if (!answer) {
    return (
      <div className="answer-container">
        <p className="placeholder">Answer will appear here</p>
      </div>
    );
  }

  return (
    <div className="answer-container">
      <div className="answer-text">
        {answer.text}
        <Citations citations={answer.citations} />
      </div>
      {answer.limitations.length > 0 && (
        <div className="answer-limitations">
          <strong>Limitations:</strong>
          <ul>
            {answer.limitations.map((limitation, idx) => (
              <li key={idx}>{limitation}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
