"""Unit tests for the temporal graph helpers, using a fake Neo4j driver
so no live database is required.
"""

from founder.graph import timeline


class FakeResult:

    def __init__(self, records):
        self.records = records


class FakeDriver:
    """Records every Cypher query issued and returns canned rows based on
    simple substring matching, mimicking the shape of
    `neo4j.Driver.execute_query`.
    """

    def __init__(self, responses):
        # responses: list of (marker, rows) checked in order.
        self.responses = responses
        self.calls = []

    def execute_query(self, cypher, **params):

        self.calls.append((cypher, params))

        for marker, rows in self.responses:

            if marker in cypher:
                return FakeResult(rows)

        return FakeResult([])


class FakeClient:

    def __init__(self, driver):
        self.driver = driver
        self.database = "neo4j"

    def close(self):
        pass


def _row(source, relationship, target, published_at, **extra):

    base = {
        "source": source,
        "relationship": relationship,
        "target": target,
        "evidence": "quote",
        "confidence": 0.9,
        "chunk_id": f"chunk-{published_at}",
        "document_id": "doc-1",
        "source_type": "earnings",
        "ticker": "MSFT",
        "published_at": published_at,
        "valid_from": published_at,
        "valid_to": None,
    }

    base.update(extra)

    return base


def test_get_company_timeline_orders_and_filters_by_ticker():

    rows = [
        _row("Microsoft", "INVESTS_IN", "OpenAI", "2025-06-01"),
    ]

    driver = FakeDriver([("ORDER BY r.published_at", rows)])

    client = FakeClient(driver)

    result = timeline.get_company_timeline("MSFT", client=client)

    assert result == rows

    _, params = driver.calls[0]

    assert params["ticker"] == "MSFT"


def test_get_relationship_timeline_passes_entity_name():

    rows = [
        _row("Microsoft", "COMPETES_WITH", "Google", "2025-03-01"),
    ]

    driver = FakeDriver([("toLower(s.name)", rows)])

    client = FakeClient(driver)

    result = timeline.get_relationship_timeline(
        "Microsoft", client=client
    )

    assert result == rows

    _, params = driver.calls[0]

    assert params["entity_name"] == "Microsoft"


def test_compare_periods_computes_added_removed_unchanged():

    period_a_rows = [
        {"source": "Microsoft", "relationship": "PARTNERS_WITH", "target": "OpenAI"},
        {"source": "Microsoft", "relationship": "COMPETES_WITH", "target": "Google"},
    ]

    period_b_rows = [
        {"source": "Microsoft", "relationship": "COMPETES_WITH", "target": "Google"},
        {"source": "Microsoft", "relationship": "ACQUIRED", "target": "Activision"},
    ]

    calls = {"count": 0}

    class SequencedDriver:

        def __init__(self):
            self.calls = []

        def execute_query(self, cypher, **params):

            self.calls.append((cypher, params))

            calls["count"] += 1

            if calls["count"] == 1:
                return FakeResult(period_a_rows)

            return FakeResult(period_b_rows)

    client = FakeClient(SequencedDriver())

    result = timeline.compare_periods(
        "MSFT",
        "2025-01-01",
        "2025-06-30",
        "2025-07-01",
        "2025-12-31",
        client=client,
    )

    assert result["added"] == [
        ("Microsoft", "ACQUIRED", "Activision"),
    ]

    assert result["removed"] == [
        ("Microsoft", "PARTNERS_WITH", "OpenAI"),
    ]

    assert result["unchanged"] == [
        ("Microsoft", "COMPETES_WITH", "Google"),
    ]


def test_find_new_relationships_filters_by_first_seen():

    rows = [
        {
            "source": "Microsoft",
            "relationship": "INVESTS_IN",
            "target": "OpenAI",
            "first_seen": "2025-03-01",
            "last_seen": "2025-09-01",
        },
        {
            "source": "Microsoft",
            "relationship": "FOUNDED",
            "target": "Microsoft",
            "first_seen": "1975-04-04",
            "last_seen": "1975-04-04",
        },
    ]

    driver = FakeDriver([("min(r.published_at)", rows)])

    client = FakeClient(driver)

    result = timeline.find_new_relationships(
        "MSFT", "2025-01-01", client=client
    )

    assert len(result) == 1
    assert result[0]["target"] == "OpenAI"


def test_find_removed_relationships_filters_by_last_seen():

    rows = [
        {
            "source": "Microsoft",
            "relationship": "PARTNERS_WITH",
            "target": "Nokia",
            "first_seen": "2013-01-01",
            "last_seen": "2014-01-01",
        },
        {
            "source": "Microsoft",
            "relationship": "COMPETES_WITH",
            "target": "Google",
            "first_seen": "2020-01-01",
            "last_seen": "2026-01-01",
        },
    ]

    driver = FakeDriver([("min(r.published_at)", rows)])

    client = FakeClient(driver)

    result = timeline.find_removed_relationships(
        "MSFT", "2015-01-01", "2020-01-01", client=client
    )

    assert len(result) == 1
    assert result[0]["target"] == "Nokia"
