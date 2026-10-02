import React, { useState, useEffect } from "react";
import { QueryInput } from "./components/QueryInput";
import { AnswerDisplay } from "./components/AnswerDisplay";
import { EvidenceCard } from "./components/EvidenceCard";
import { Timeline } from "./components/Timeline";
import { Filters } from "./components/Filters";
import { healthCheck, queryStream } from "./services/api";
import { Answer, Evidence, StreamEvent } from "./types";
import "./styles/globals.css";

function App() {
  const [status, setStatus] = useState<string>("Checking system...");
  const [systemReady, setSystemReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [statusMessages, setStatusMessages] = useState<string[]>([]);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await healthCheck();
        setStatus("System Ready");
        setSystemReady(true);
      } catch (err) {
        setStatus("System Unavailable");
        setSystemReady(false);
      }
    };

    checkHealth();
  }, []);

  const handleQuery = async (query: string) => {
    setLoading(true);
    setAnswer(null);
    setEvidence([]);
    setStatusMessages([]);

    try {
      await queryStream(query, 8, (event: StreamEvent) => {
        if (event.type === "status" && event.message) {
          setStatusMessages((prev) => [...prev, event.message!]);
        } else if (event.type === "evidence") {
          // Mock evidence object
          setEvidence((prev) => [
            ...prev,
            {
              evidence_id: event.evidence_id || "",
              source: (event.source as any) || "SEC",
              text: `Evidence from ${event.source}`,
              ticker: event.ticker,
              date: event.date,
            },
          ]);
        } else if (event.type === "answer" && event.text) {
          setAnswer({
            text: event.text,
            claims: [],
            citations: [],
            limitations: [],
          });
        } else if (event.type === "complete") {
          setLoading(false);
        } else if (event.type === "error") {
          setStatusMessages((prev) => [
            ...prev,
            `Error: ${event.error_message}`,
          ]);
          setLoading(false);
        }
      });
    } catch (err) {
      setStatusMessages((prev) => [
        ...prev,
        `Failed to query: ${err instanceof Error ? err.message : "Unknown error"}`,
      ]);
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>FounderOS</h1>
        <div className="system-status">
          <span className={`status-indicator ${systemReady ? "ready" : "error"}`}>
            ●
          </span>
          {status}
        </div>
      </header>

      <main className="app-main">
        <div className="query-section">
          <h2>Ask a strategic question...</h2>
          <div className="query-bar">
            <QueryInput onSubmit={handleQuery} disabled={loading} />
            <Filters />
          </div>
        </div>

        <div className="results-section">
          <div className="answer-panel">
            <h3>Answer</h3>
            <AnswerDisplay answer={answer} loading={loading} />
          </div>

          <div className="evidence-panel">
            <h3>Evidence</h3>
            <div className="evidence-list">
              {evidence.length > 0 ? (
                evidence.map((e) => (
                  <EvidenceCard key={e.evidence_id} evidence={e} />
                ))
              ) : (
                <p className="placeholder">Evidence will appear here</p>
              )}
            </div>
          </div>
        </div>

        <Timeline />

        {statusMessages.length > 0 && (
          <div className="status-footer">
            <strong>Status:</strong> {statusMessages[statusMessages.length - 1]}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
