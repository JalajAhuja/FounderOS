import json

from founder.graph.config import (
    EXTRACTIONS_FILE,
)
from founder.graph.neo4j_client import (
    Neo4jClient,
)
from founder.graph.schema import (
    RELATIONSHIP_TYPES,
)

ALLOWED_RELATIONSHIPS = set(RELATIONSHIP_TYPES)


def safe_label(value):

    allowed = {
        "Company",
        "Person",
        "Product",
        "Technology",
        "Event",
        "Market",
        "Metric",
    }

    if value in allowed:
        return value

    return None


def normalize_name(name):

    return " ".join(
        str(name)
        .strip()
        .split()
    )


def create_chunk(
    client,
    extraction,
):

    query = """
    MERGE (c:Chunk {
        chunk_id: $chunk_id
    })

    SET
        c.document_id = $document_id,
        c.source = $source,
        c.ticker = $ticker,
        c.published_at = $published_at

    RETURN c
    """

    client.execute(
        query,
        {
            "chunk_id": extraction[
                "chunk_id"
            ],

            "document_id": extraction.get(
                "document_id"
            ),

            "source": extraction.get(
                "source"
            ),

            "ticker": extraction.get(
                "ticker"
            ),

            "published_at": extraction.get(
                "published_at"
            ),
        },
    )

    create_document(
        client,
        extraction,
    )


def create_document(
    client,
    extraction,
):
    """Create the Document node this chunk belongs to and link it via
    `PART_OF`, giving explicit chunk -> document provenance instead of
    relying solely on the `document_id` property.
    """

    document_id = extraction.get(
        "document_id"
    )

    if not document_id:
        return

    query = """
    MERGE (d:Document {
        document_id: $document_id
    })

    SET
        d.source = $source,
        d.ticker = $ticker,
        d.published_at = $published_at

    WITH d

    MATCH (c:Chunk {
        chunk_id: $chunk_id
    })

    MERGE (c)-[:PART_OF]->(d)

    RETURN d
    """

    client.execute(
        query,
        {
            "document_id": document_id,

            "chunk_id": extraction[
                "chunk_id"
            ],

            "source": extraction.get(
                "source"
            ),

            "ticker": extraction.get(
                "ticker"
            ),

            "published_at": extraction.get(
                "published_at"
            ),
        },
    )


def create_entity(
    client,
    entity,
):

    label = safe_label(
        entity.get("type")
    )

    if not label:
        return False

    name = normalize_name(
        entity.get("name")
    )

    if not name:
        return False

    query = f"""
    MERGE (n:{label} {{
        name: $name
    }})

    RETURN n
    """

    client.execute(
        query,
        {
            "name": name
        },
    )

    return True


def create_mention(
    client,
    extraction,
    entity,
):

    label = safe_label(
        entity.get("type")
    )

    if not label:
        return

    name = normalize_name(
        entity.get("name")
    )

    if not name:
        return

    query = f"""
    MATCH (c:Chunk {{
        chunk_id: $chunk_id
    }})

    MATCH (n:{label} {{
        name: $name
    }})

    MERGE (n)-[r:MENTIONED_IN]->(c)

    SET
        r.source = $source,
        r.published_at = $published_at

    RETURN r
    """

    client.execute(
        query,
        {
            "chunk_id": extraction[
                "chunk_id"
            ],

            "name": name,

            "source": extraction.get(
                "source"
            ),

            "published_at": extraction.get(
                "published_at"
            ),
        },
    )


def create_relationship(
    client,
    extraction,
    relationship,
):

    relationship_type = relationship.get(
        "relationship"
    )

    if (
        relationship_type
        not in ALLOWED_RELATIONSHIPS
    ):
        return False

    source_label = safe_label(
        relationship.get(
            "source_type"
        )
    )

    target_label = safe_label(
        relationship.get(
            "target_type"
        )
    )

    if not source_label or not target_label:
        return False

    source_name = normalize_name(
        relationship.get(
            "source"
        )
    )

    target_name = normalize_name(
        relationship.get(
            "target"
        )
    )

    if not source_name or not target_name:
        return False

    # The relationship identity includes chunk_id so the same
    # (source, type, target) triple extracted from different chunks over
    # time creates separate, independently timestamped edges instead of
    # overwriting prior evidence -- this is what makes the graph
    # provenance-preserving and temporal rather than a mutable snapshot.
    query = f"""
    MATCH (s:{source_label} {{
        name: $source_name
    }})

    MATCH (t:{target_label} {{
        name: $target_name
    }})

    MERGE (s)-[r:{relationship_type} {{
        chunk_id: $chunk_id
    }}]->(t)

    SET
        r.evidence = $evidence,
        r.confidence = $confidence,
        r.document_id = $document_id,
        r.source = $source,
        r.ticker = $ticker,
        r.published_at = $published_at,
        r.valid_from = $published_at,
        r.valid_to = coalesce(r.valid_to, null)

    RETURN r
    """

    client.execute(
        query,
        {
            "source_name": source_name,

            "target_name": target_name,

            "evidence": relationship.get(
                "evidence"
            ),

            "confidence": relationship.get(
                "confidence",
                0.0,
            ),

            "chunk_id": extraction[
                "chunk_id"
            ],

            "document_id": extraction.get(
                "document_id"
            ),

            "source": extraction.get(
                "source"
            ),

            "ticker": extraction.get(
                "ticker"
            ),

            "published_at": extraction.get(
                "published_at"
            ),
        },
    )

    create_supported_by(
        client,
        extraction,
        source_label,
        source_name,
    )

    create_supported_by(
        client,
        extraction,
        target_label,
        target_name,
    )

    return True


def create_supported_by(
    client,
    extraction,
    label,
    name,
):
    """Explicit entity -> Chunk provenance edge for entities that
    participate in an extracted relationship, distinct from the generic
    `MENTIONED_IN` edge created for every mentioned entity. This lets a
    relationship be traced graph-natively: entity -> relationship ->
    (SUPPORTED_BY) -> Chunk -> (PART_OF) -> Document.
    """

    query = f"""
    MATCH (c:Chunk {{
        chunk_id: $chunk_id
    }})

    MATCH (n:{label} {{
        name: $name
    }})

    MERGE (n)-[r:SUPPORTED_BY]->(c)

    SET
        r.published_at = $published_at

    RETURN r
    """

    client.execute(
        query,
        {
            "chunk_id": extraction[
                "chunk_id"
            ],

            "name": name,

            "published_at": extraction.get(
                "published_at"
            ),
        },
    )


def main():

    print(
        "\nFounderOS - Neo4j Graph Writer"
    )

    client = Neo4jClient()

    total_chunks = 0
    total_entities = 0
    total_relationships = 0

    with open(
        EXTRACTIONS_FILE,
        encoding="utf-8",
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            extraction = json.loads(
                line
            )

            create_chunk(
                client,
                extraction,
            )

            total_chunks += 1

            # ------------------------------------------------
            # Entities
            # ------------------------------------------------

            for entity in extraction.get(
                "entities",
                [],
            ):

                if create_entity(
                    client,
                    entity,
                ):

                    total_entities += 1

                    create_mention(
                        client,
                        extraction,
                        entity,
                    )

            # ------------------------------------------------
            # Relationships
            # ------------------------------------------------

            for relationship in extraction.get(
                "relationships",
                [],
            ):

                if create_relationship(
                    client,
                    extraction,
                    relationship,
                ):

                    total_relationships += 1

    client.close()

    print(
        "\n" + "=" * 70
    )

    print(
        "GRAPH BUILD COMPLETE"
    )

    print(
        f"Chunks processed: "
        f"{total_chunks:,}"
    )

    print(
        f"Entities processed: "
        f"{total_entities:,}"
    )

    print(
        f"Relationships processed: "
        f"{total_relationships:,}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()
