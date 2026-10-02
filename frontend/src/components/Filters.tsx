import React, { useState } from "react";

interface FiltersProps {
  onTicker?: (ticker: string) => void;
  onSource?: (source: string) => void;
}

export const Filters: React.FC<FiltersProps> = ({ onTicker, onSource }) => {
  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="filters-container">
      <button
        onClick={() => setShowFilters(!showFilters)}
        className="filters-toggle"
      >
        Filters ▼
      </button>
      {showFilters && (
        <div className="filters-panel">
          <div className="filter-group">
            <label>Ticker</label>
            <input
              type="text"
              placeholder="e.g., MSFT"
              onChange={(e) => onTicker?.(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label>Source</label>
            <select onChange={(e) => onSource?.(e.target.value)}>
              <option value="">All sources</option>
              <option value="SEC">SEC Filings</option>
              <option value="earnings_call">Earnings Calls</option>
              <option value="news">News</option>
              <option value="graph">Knowledge Graph</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};
