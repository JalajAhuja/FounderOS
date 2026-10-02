from founder.graph.neo4j_client import (
    Neo4jClient,
)


def main():

    client = Neo4jClient()

    print(
        "\nInitializing FounderOS Neo4j graph..."
    )

    queries = [

        # ----------------------------------------------------
        # Entity uniqueness
        # ----------------------------------------------------

        """
        CREATE CONSTRAINT company_name_unique
        IF NOT EXISTS
        FOR (n:Company)
        REQUIRE n.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT person_name_unique
        IF NOT EXISTS
        FOR (n:Person)
        REQUIRE n.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT product_name_unique
        IF NOT EXISTS
        FOR (n:Product)
        REQUIRE n.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT technology_name_unique
        IF NOT EXISTS
        FOR (n:Technology)
        REQUIRE n.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT event_name_unique
        IF NOT EXISTS
        FOR (n:Event)
        REQUIRE n.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT market_name_unique
        IF NOT EXISTS
        FOR (n:Market)
        REQUIRE n.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT metric_name_unique
        IF NOT EXISTS
        FOR (n:Metric)
        REQUIRE n.name IS UNIQUE
        """,

        # ----------------------------------------------------
        # Chunk uniqueness
        # ----------------------------------------------------

        """
        CREATE CONSTRAINT chunk_id_unique
        IF NOT EXISTS
        FOR (n:Chunk)
        REQUIRE n.chunk_id IS UNIQUE
        """,

        # ----------------------------------------------------
        # Document uniqueness
        # ----------------------------------------------------

        """
        CREATE CONSTRAINT document_id_unique
        IF NOT EXISTS
        FOR (n:Document)
        REQUIRE n.document_id IS UNIQUE
        """,

        # ----------------------------------------------------
        # Temporal query performance
        # ----------------------------------------------------

        """
        CREATE INDEX chunk_published_at
        IF NOT EXISTS
        FOR (n:Chunk)
        ON (n.published_at)
        """,

        """
        CREATE INDEX document_published_at
        IF NOT EXISTS
        FOR (n:Document)
        ON (n.published_at)
        """,
    ]

    for query in queries:

        client.execute(query)

    client.close()

    print(
        "Neo4j schema initialized."
    )


if __name__ == "__main__":
    main()