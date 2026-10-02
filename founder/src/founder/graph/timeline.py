"""Temporal knowledge-graph query helpers (Step 13).

Each function accepts an optional `client`. When omitted, a fresh
`Neo4jClient` is created and closed internally; callers that want to reuse
a single connection across several calls (e.g. `runner.py` /
`timeline_test.py`) can pass their own client and manage its lifecycle
instead.

These helpers read the relationship provenance fields written by
`founder.graph.write_graph` (`chunk_id`, `document_id`, `evidence`,
`confidence`, `source`, `ticker`, `published_at`, `valid_from`,
`valid_to`). They do not themselves write to the graph.
"""

from founder.graph.neo4j_client import Neo4jClient


def _with_client(client):

    if client is not None:
        return client, False

    return Neo4jClient(), True


def _run(client, cypher, **params):

    result = client.driver.execute_query(
        cypher,
        **params,
        database_=client.database,
    )

    return [dict(record) for record in result.records]


TIMELINE_FIELDS = """
        s.name AS source,
        type(r) AS relationship,
        t.name AS target,
        r.evidence AS evidence,
        r.confidence AS confidence,
        r.chunk_id AS chunk_id,
        r.document_id AS document_id,
        r.source AS source_type,
        r.ticker AS ticker,
        r.published_at AS published_at,
        r.valid_from AS valid_from,
        r.valid_to AS valid_to
"""


def get_company_timeline(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 200,
    client=None,
) -> list[dict]:
    """All relationship events involving entities tagged with `ticker`,
    ordered chronologically, optionally bounded to [start_date, end_date]
    (inclusive, ISO-ish string comparison consistent with how
    `published_at` is already stored)."""

    client, owns_client = _with_client(client)

    try:

        cypher = f"""
        MATCH (s)-[r]->(t)
        WHERE r.ticker = $ticker
          AND ($start_date IS NULL OR r.published_at >= $start_date)
          AND ($end_date IS NULL OR r.published_at <= $end_date)
        RETURN {TIMELINE_FIELDS}
        ORDER BY r.published_at
        LIMIT $limit
        """

        return _run(
            client,
            cypher,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    finally:

        if owns_client:
            client.close()


def get_relationship_timeline(
    entity_name: str,
    relationship_type: str | None = None,
    limit: int = 200,
    client=None,
) -> list[dict]:
    """All relationship events where `entity_name` is either the source or
    the target, optionally filtered to a single relationship type."""

    client, owns_client = _with_client(client)

    try:

        cypher = f"""
        MATCH (s)-[r]->(t)
        WHERE (
            toLower(s.name) = toLower($entity_name)
            OR toLower(t.name) = toLower($entity_name)
        )
        AND ($relationship_type IS NULL OR type(r) = $relationship_type)
        RETURN {TIMELINE_FIELDS}
        ORDER BY r.published_at
        LIMIT $limit
        """

        return _run(
            client,
            cypher,
            entity_name=entity_name,
            relationship_type=relationship_type,
            limit=limit,
        )

    finally:

        if owns_client:
            client.close()


def _distinct_triples(
    ticker: str,
    start_date: str,
    end_date: str,
    client,
) -> set[tuple[str, str, str]]:

    cypher = """
    MATCH (s)-[r]->(t)
    WHERE r.ticker = $ticker
      AND r.published_at >= $start_date
      AND r.published_at <= $end_date
    RETURN DISTINCT s.name AS source, type(r) AS relationship, t.name AS target
    """

    rows = _run(
        client,
        cypher,
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        (row["source"], row["relationship"], row["target"])
        for row in rows
    }


def compare_periods(
    ticker: str,
    period_a_start: str,
    period_a_end: str,
    period_b_start: str,
    period_b_end: str,
    client=None,
) -> dict:
    """Diff the distinct (source, relationship, target) triples observed
    for `ticker` between two non-overlapping (or overlapping) date
    windows. Does not claim causality -- only reports set differences."""

    client, owns_client = _with_client(client)

    try:

        triples_a = _distinct_triples(
            ticker, period_a_start, period_a_end, client
        )

        triples_b = _distinct_triples(
            ticker, period_b_start, period_b_end, client
        )

        return {
            "period_a": {
                "start": period_a_start,
                "end": period_a_end,
                "relationships": sorted(triples_a),
            },
            "period_b": {
                "start": period_b_start,
                "end": period_b_end,
                "relationships": sorted(triples_b),
            },
            "added": sorted(triples_b - triples_a),
            "removed": sorted(triples_a - triples_b),
            "unchanged": sorted(triples_a & triples_b),
        }

    finally:

        if owns_client:
            client.close()


def _triples_with_bounds(
    ticker: str,
    client,
) -> list[dict]:

    cypher = """
    MATCH (s)-[r]->(t)
    WHERE r.ticker = $ticker
    WITH
        s.name AS source,
        type(r) AS relationship,
        t.name AS target,
        min(r.published_at) AS first_seen,
        max(r.published_at) AS last_seen
    RETURN source, relationship, target, first_seen, last_seen
    ORDER BY first_seen
    """

    return _run(client, cypher, ticker=ticker)


def find_new_relationships(
    ticker: str,
    since_date: str,
    client=None,
) -> list[dict]:
    """Relationship triples whose earliest observed evidence is at or
    after `since_date` -- i.e. they were not part of the graph before that
    date."""

    client, owns_client = _with_client(client)

    try:

        rows = _triples_with_bounds(ticker, client)

        return [
            row
            for row in rows
            if row["first_seen"] and row["first_seen"] >= since_date
        ]

    finally:

        if owns_client:
            client.close()


def find_removed_relationships(
    ticker: str,
    before_date: str,
    after_date: str,
    client=None,
) -> list[dict]:
    """Relationship triples last seen at or before `before_date` that do
    not reappear in any evidence at or after `after_date` -- i.e. they
    appear to have dropped out of the narrative."""

    client, owns_client = _with_client(client)

    try:

        rows = _triples_with_bounds(ticker, client)

        # last_seen is already the max published_at across every instance
        # of this triple, so "last_seen <= before_date" already implies no
        # instance exists at/after after_date whenever after_date >=
        # before_date.
        return [
            row
            for row in rows
            if row["last_seen"]
            and row["last_seen"] <= before_date
            and before_date <= after_date
        ]

    finally:

        if owns_client:
            client.close()
