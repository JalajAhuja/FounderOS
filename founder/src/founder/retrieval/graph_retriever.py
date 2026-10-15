from founder.graph.neo4j_client import (
    Neo4jClient,
)


class GraphRetriever:

    def __init__(self):

        self.client = Neo4jClient()

    # ========================================================
    # ENTITY / RELATIONSHIP SEARCH
    # ========================================================

    def search(
        self,
        query,
        ticker=None,
        top_k=10,
    ):

        # ----------------------------------------------------
        # If ticker exists, anchor the graph around it.
        # ----------------------------------------------------

        if ticker:

            cypher = """
            MATCH (company:Company)
            WHERE
                toLower(company.name)
                CONTAINS toLower($ticker)

            MATCH (company)-[r]-(target)

            RETURN
                company.name AS source,
                type(r) AS relationship,
                target.name AS target,
                labels(target) AS target_types,
                r.evidence AS evidence,
                r.confidence AS confidence,
                r.source AS source_type,
                r.published_at AS published_at,
                r.chunk_id AS chunk_id

            ORDER BY r.published_at DESC

            LIMIT $top_k
            """

            records = self.client.driver.execute_query(
                cypher,
                ticker=ticker,
                top_k=top_k,
                database_=self.client.database,
            )

            return [
                dict(record)
                for record in records.records
            ]

        # ----------------------------------------------------
        # General graph search.
        #
        # We search entity names against words in query.
        # This is intentionally simple; LangGraph will later
        # provide a more intelligent graph-query tool.
        # ----------------------------------------------------

        words = [
            word.strip(
                ".,?!:;()[]{}"
            )

            for word in query.split()

            if len(word) >= 3
        ]

        if not words:
            return []

        cypher = """
        UNWIND $terms AS term

        MATCH (entity)

        WHERE
            entity.name IS NOT NULL
            AND toLower(entity.name)
                CONTAINS toLower(term)

        MATCH (entity)-[r]-(target)

        RETURN
            entity.name AS source,
            type(r) AS relationship,
            target.name AS target,
            labels(target) AS target_types,
            r.evidence AS evidence,
            r.confidence AS confidence,
            r.source AS source_type,
            r.published_at AS published_at,
            r.chunk_id AS chunk_id

        ORDER BY r.published_at DESC

        LIMIT $top_k
        """

        records = self.client.driver.execute_query(
            cypher,
            terms=words,
            top_k=top_k,
            database_=self.client.database,
        )

        return [
            dict(record)
            for record in records.records
        ]

    def close(self):

        self.client.close()
