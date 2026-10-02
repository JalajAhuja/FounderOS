"""PostgreSQL repository layer (mock for now)."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from founder.storage.models import (
    Session,
    QueryRecord,
    AgentRun,
    Answer,
    Feedback,
)


class SessionRepository:
    """Session persistence."""

    def __init__(self):
        self._sessions: dict[UUID, Session] = {}

    def create_session(
        self, user_id: Optional[str] = None
    ) -> Session:
        """Create a new session."""

        now = datetime.utcnow()

        session = Session(
            session_id=uuid4(),
            created_at=now,
            updated_at=now,
            user_id=user_id,
            status="active",
        )

        self._sessions[session.session_id] = session

        return session

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieve session by ID."""

        return self._sessions.get(session_id)

    def close_session(self, session_id: UUID) -> None:
        """Close a session."""

        if session_id in self._sessions:

            session = self._sessions[session_id]

            session.status = "closed"
            session.updated_at = datetime.utcnow()


class QueryRepository:
    """Query history persistence."""

    def __init__(self):
        self._queries: dict[UUID, QueryRecord] = {}

    def log_query(self, session_id: UUID, query_text: str) -> QueryRecord:
        """Log a query."""

        record = QueryRecord(
            query_id=uuid4(),
            session_id=session_id,
            query_text=query_text,
            created_at=datetime.utcnow(),
        )

        self._queries[record.query_id] = record

        return record

    def get_query(self, query_id: UUID) -> Optional[QueryRecord]:
        """Retrieve query by ID."""

        return self._queries.get(query_id)


class AgentRunRepository:
    """Agent run checkpointing."""

    def __init__(self):
        self._runs: dict[UUID, AgentRun] = {}

    def create_run(self, query_id: UUID) -> AgentRun:
        """Create a new agent run."""

        run = AgentRun(
            run_id=uuid4(),
            query_id=query_id,
            status="pending",
            started_at=datetime.utcnow(),
        )

        self._runs[run.run_id] = run

        return run

    def save_checkpoint(
        self, run_id: UUID, checkpoint_data: dict
    ) -> None:
        """Save checkpoint for agent run."""

        if run_id in self._runs:

            self._runs[run_id].checkpoint_data = checkpoint_data

    def complete_run(
        self, run_id: UUID, latency_ms: int
    ) -> None:
        """Mark run as complete."""

        if run_id in self._runs:

            run = self._runs[run_id]

            run.status = "complete"
            run.completed_at = datetime.utcnow()
            run.latency_ms = latency_ms

    def error_run(self, run_id: UUID, error: str) -> None:
        """Mark run as errored."""

        if run_id in self._runs:

            run = self._runs[run_id]

            run.status = "error"
            run.error = error
            run.completed_at = datetime.utcnow()

    def get_run(self, run_id: UUID) -> Optional[AgentRun]:
        """Retrieve run by ID."""

        return self._runs.get(run_id)


class AnswerRepository:
    """Answer persistence."""

    def __init__(self):
        self._answers: dict[UUID, Answer] = {}

    def save_answer(
        self,
        run_id: UUID,
        answer_text: str,
        claims: list,
        citations: list,
        evidence: list,
    ) -> Answer:
        """Save generated answer."""

        answer = Answer(
            answer_id=uuid4(),
            run_id=run_id,
            answer_text=answer_text,
            claims=claims,
            citations=citations,
            evidence=evidence,
        )

        self._answers[answer.answer_id] = answer

        return answer

    def get_answer(self, answer_id: UUID) -> Optional[Answer]:
        """Retrieve answer by ID."""

        return self._answers.get(answer_id)


class FeedbackRepository:
    """Feedback persistence."""

    def __init__(self):
        self._feedback: dict[UUID, Feedback] = {}

    def save_feedback(
        self,
        run_id: UUID,
        rating: int,
        comment: Optional[str] = None,
    ) -> Feedback:
        """Save user feedback."""

        feedback = Feedback(
            feedback_id=uuid4(),
            run_id=run_id,
            rating=min(5, max(1, rating)),  # Clamp to 1-5
            comment=comment,
            created_at=datetime.utcnow(),
        )

        self._feedback[feedback.feedback_id] = feedback

        return feedback

    def get_feedback(self, run_id: UUID) -> Optional[Feedback]:
        """Retrieve feedback for run."""

        for feedback in self._feedback.values():

            if feedback.run_id == run_id:
                return feedback

        return None


# Global singleton instances (in-memory for now)
_sessions = SessionRepository()
_queries = QueryRepository()
_runs = AgentRunRepository()
_answers = AnswerRepository()
_feedback = FeedbackRepository()


def get_session_repo() -> SessionRepository:
    return _sessions


def get_query_repo() -> QueryRepository:
    return _queries


def get_run_repo() -> AgentRunRepository:
    return _runs


def get_answer_repo() -> AnswerRepository:
    return _answers


def get_feedback_repo() -> FeedbackRepository:
    return _feedback
