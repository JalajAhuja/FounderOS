"""Tests for storage repositories."""

import uuid

from founder.storage.repositories import (
    get_answer_repo,
    get_feedback_repo,
    get_query_repo,
    get_run_repo,
    get_session_repo,
)


def test_create_and_retrieve_session():

    repo = get_session_repo()

    session = repo.create_session(user_id="user123")

    assert session.session_id is not None
    assert session.user_id == "user123"
    assert session.status == "active"

    retrieved = repo.get_session(session.session_id)

    assert retrieved.session_id == session.session_id


def test_close_session():

    repo = get_session_repo()

    session = repo.create_session()

    repo.close_session(session.session_id)

    retrieved = repo.get_session(session.session_id)

    assert retrieved.status == "closed"


def test_log_and_retrieve_query():

    session_repo = get_session_repo()
    query_repo = get_query_repo()

    session = session_repo.create_session()

    query_record = query_repo.log_query(
        session.session_id, "What is Microsoft's revenue?"
    )

    assert query_record.query_id is not None
    assert query_record.query_text == "What is Microsoft's revenue?"

    retrieved = query_repo.get_query(query_record.query_id)

    assert retrieved.query_text == "What is Microsoft's revenue?"


def test_agent_run_lifecycle():

    query_repo = get_query_repo()
    run_repo = get_run_repo()
    session_repo = get_session_repo()

    session = session_repo.create_session()
    query_record = query_repo.log_query(session.session_id, "test query")
    run = run_repo.create_run(query_record.query_id)

    assert run.status == "pending"

    run_repo.save_checkpoint(run.run_id, {"data": "checkpoint"})

    retrieved = run_repo.get_run(run.run_id)

    assert retrieved.checkpoint_data == {"data": "checkpoint"}

    run_repo.complete_run(run.run_id, 1234)

    completed = run_repo.get_run(run.run_id)

    assert completed.status == "complete"
    assert completed.latency_ms == 1234


def test_save_and_retrieve_answer():

    answer_repo = get_answer_repo()

    run_id = uuid.uuid4()

    answer = answer_repo.save_answer(
        run_id=run_id,
        answer_text="The answer is...",
        claims=[{"text": "Claim 1"}],
        citations=[{"id": 1, "text": "[1]"}],
        evidence=[{"id": "e1"}],
    )

    assert answer.answer_id is not None

    retrieved = answer_repo.get_answer(answer.answer_id)

    assert retrieved.answer_text == "The answer is..."


def test_save_and_retrieve_feedback():

    feedback_repo = get_feedback_repo()

    run_id = uuid.uuid4()

    feedback = feedback_repo.save_feedback(
        run_id=run_id,
        rating=4,
        comment="Good answer",
    )

    assert feedback.feedback_id is not None
    assert feedback.rating == 4

    retrieved = feedback_repo.get_feedback(run_id)

    assert retrieved.comment == "Good answer"
