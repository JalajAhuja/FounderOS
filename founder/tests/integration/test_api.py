"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from founder.api.main import app


@pytest.mark.integration
class TestHealthEndpoint:

    def test_health_check_returns_ok(self):

        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_includes_services(self):

        client = TestClient(app)

        response = client.get("/health")

        data = response.json()

        assert "qdrant" in data
        assert "neo4j" in data
        assert "langfuse" in data


@pytest.mark.integration
class TestStreamingEndpoint:

    def test_stream_endpoint_returns_event_stream(self):

        client = TestClient(app)

        response = client.post("/api/v1/query/stream?query=test&top_k=5")

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

    def test_stream_endpoint_rejects_empty_query(self):

        client = TestClient(app)

        response = client.post("/api/v1/query/stream?query=&top_k=5")

        assert response.status_code == 400
