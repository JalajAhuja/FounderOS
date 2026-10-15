from founder.graph.neo4j_client import (
    Neo4jClient,
)


def company_timeline(
    ticker: str,
):

    client = Neo4jClient()

    query = """
    MATCH (c:Company)
    WHERE
        c.name CONTAINS $ticker
        OR c.name = $ticker

    MATCH (c)-[r]->(target)

    RETURN
        c.name AS company,
        type(r) AS relationship,
        target.name AS target,
        r.evidence AS evidence,
        r.source AS source,
        r.published_at AS published_at,
        r.chunk_id AS chunk_id

    ORDER BY r.published_at
    """

    result = client.driver.execute_query(
        query,
        ticker=ticker,
        database_=client.database,
    )

    client.close()

    return result.records


def main():

    ticker = input(
        "Company name/ticker: "
    ).strip()

    records = company_timeline(
        ticker
    )

    print(
        f"\nFound {len(records)} graph events.\n"
    )

    for record in records:

        print(
            f"{record['published_at']} | "
            f"{record['company']} "
            f"--{record['relationship']}--> "
            f"{record['target']}"
        )

        print(
            f"  Source: {record['source']}"
        )

        print(
            f"  Evidence: {record['evidence']}"
        )

        print()


if __name__ == "__main__":
    main()
