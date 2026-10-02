"""Unit tests for the write_graph provenance hardening (Step 13),
using a fake client that just records executed Cypher/params.
"""

from founder.graph import write_graph


class FakeClient:

    def __init__(self):
        self.calls = []

    def execute(self, query, parameters=None):
        self.calls.append((query, parameters or {}))


def _extraction(**overrides):

    base = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "source": "earnings",
        "ticker": "MSFT",
        "published_at": "2025-06-01",
    }

    base.update(overrides)

    return base


def test_create_chunk_also_creates_document_and_part_of():

    client = FakeClient()

    write_graph.create_chunk(client, _extraction())

    queries = [call[0] for call in client.calls]

    assert any("MERGE (c:Chunk" in q for q in queries)
    assert any("MERGE (d:Document" in q for q in queries)
    assert any("PART_OF" in q for q in queries)


def test_create_document_skips_when_no_document_id():

    client = FakeClient()

    write_graph.create_document(
        client, _extraction(document_id=None)
    )

    assert client.calls == []


def test_create_relationship_scopes_identity_by_chunk_and_sets_temporal_fields():

    client = FakeClient()

    relationship = {
        "source": "Microsoft",
        "source_type": "Company",
        "relationship": "INVESTS_IN",
        "target": "OpenAI",
        "target_type": "Company",
        "evidence": "Microsoft invested in OpenAI.",
        "confidence": 0.95,
    }

    created = write_graph.create_relationship(
        client, _extraction(), relationship
    )

    assert created is True

    relationship_query, relationship_params = client.calls[0]

    assert "chunk_id: $chunk_id" in relationship_query
    assert "r.valid_from = $published_at" in relationship_query
    assert relationship_params["chunk_id"] == "chunk-1"
    assert relationship_params["published_at"] == "2025-06-01"

    # SUPPORTED_BY edges created for both source and target entities.
    supported_by_queries = [
        query for query, _ in client.calls if "SUPPORTED_BY" in query
    ]

    assert len(supported_by_queries) == 2


def test_create_relationship_rejects_unknown_type():

    client = FakeClient()

    relationship = {
        "source": "Microsoft",
        "source_type": "Company",
        "relationship": "NOT_A_REAL_TYPE",
        "target": "OpenAI",
        "target_type": "Company",
        "evidence": "...",
        "confidence": 0.5,
    }

    created = write_graph.create_relationship(
        client, _extraction(), relationship
    )

    assert created is False
    assert client.calls == []
