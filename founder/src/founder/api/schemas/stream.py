"""Streaming response models and events."""

import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StatusEvent:
    """Status update event."""

    type: str = "status"
    message: str = ""
    timestamp: datetime | None = None

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "message": self.message,
            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),
        })


@dataclass
class EvidenceEvent:
    """Evidence discovered event."""

    type: str = "evidence"
    evidence_id: str = ""
    source: str = ""  # SEC, earnings_call, news, graph
    ticker: str | None = None
    date: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "evidence_id": self.evidence_id,
            "source": self.source,
            "ticker": self.ticker,
            "date": self.date,
        })


@dataclass
class AnswerEvent:
    """Partial or complete answer event."""

    type: str = "answer"
    text: str = ""
    complete: bool = False

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "text": self.text,
            "complete": self.complete,
        })


@dataclass
class CompleteEvent:
    """Query completion event."""

    type: str = "complete"
    trace_id: str = ""
    latency_ms: int = 0
    answer: str = ""
    evidence_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "trace_id": self.trace_id,
            "latency_ms": self.latency_ms,
            "answer": self.answer,
            "evidence_count": self.evidence_count,
        })


@dataclass
class ErrorEvent:
    """Error event."""

    type: str = "error"
    error_message: str = ""
    trace_id: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "error_message": self.error_message,
            "trace_id": self.trace_id,
        })


# Event stream: ordered sequence of any event
EventTypes = (
    StatusEvent
    | EvidenceEvent
    | AnswerEvent
    | CompleteEvent
    | ErrorEvent
)
