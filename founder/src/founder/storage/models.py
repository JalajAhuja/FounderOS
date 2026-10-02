"""PostgreSQL models for persistence."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Session:
    """User session."""

    session_id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    status: str = "active"  # active | closed


@dataclass
class QueryRecord:
    """Query history record."""

    query_id: UUID
    session_id: UUID
    query_text: str
    created_at: datetime


@dataclass
class AgentRun:
    """Agent execution run."""

    run_id: UUID
    query_id: UUID
    status: str  # pending | complete | error
    started_at: datetime
    completed_at: Optional[datetime] = None
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    checkpoint_data: Optional[dict] = None


@dataclass
class Answer:
    """Generated answer record."""

    answer_id: UUID
    run_id: UUID
    answer_text: str
    claims: list
    citations: list
    evidence: list


@dataclass
class Feedback:
    """User feedback."""

    feedback_id: UUID
    run_id: UUID
    rating: int  # 1-5
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
