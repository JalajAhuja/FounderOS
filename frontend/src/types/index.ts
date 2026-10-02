export type Evidence = {
  evidence_id: string;
  source: "SEC" | "earnings_call" | "news" | "graph";
  text: string;
  score?: number;
  ticker?: string;
  date?: string;
};

export type Claim = {
  text: string;
  evidence_ids: string[];
  claim_type: "fact" | "source_claim" | "inference";
  confidence: number;
};

export type Citation = {
  citation_id: number;
  evidence_id: string;
  source: string;
  date: string;
};

export type Answer = {
  text: string;
  claims: Claim[];
  citations: Citation[];
  limitations: string[];
};

export type QueryResponse = {
  trace_id: string;
  query: string;
  answer: Answer;
  evidence: Evidence[];
  latency_ms: number;
};

export type StreamEvent = {
  type: "status" | "evidence" | "answer" | "complete" | "error";
  message?: string;
  error_message?: string;
  evidence_id?: string;
  source?: string;
  ticker?: string;
  date?: string;
  text?: string;
  trace_id?: string;
  answer?: string;
  evidence_count?: number;
};
