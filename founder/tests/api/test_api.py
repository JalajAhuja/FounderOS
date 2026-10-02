"""API tests."""

import pytest

from fastapi.testclient import TestClient

from founder.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint(client):

    response = client.get("/")

    assert response.status_code == 200
    assert "FounderOS API" in response.json()["message"]


def test_stream_query_empty(client):

    response = client.post("/api/v1/query/stream?query=&top_k=8")

    assert response.status_code == 400


def test_stream_query_valid(client):

    response = client.post(
        "/api/v1/query/stream?query=What+is+Microsoft+revenue&top_k=5"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
