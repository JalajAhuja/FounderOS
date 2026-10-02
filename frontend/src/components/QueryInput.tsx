import React, { useState } from "react";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  disabled?: boolean;
}

export const QueryInput: React.FC<QueryInputProps> = ({
  onSubmit,
  disabled = false,
}) => {
  const [query, setQuery] = useState("");

  const handleSubmit = () => {
    if (query.trim()) {
      onSubmit(query);
      setQuery("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      handleSubmit();
    }
  };

  return (
    <div className="query-input-container">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask a strategic question about companies..."
        disabled={disabled}
        className="query-input"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !query.trim()}
        className="submit-button"
      >
        Ask
      </button>
    </div>
  );
};
