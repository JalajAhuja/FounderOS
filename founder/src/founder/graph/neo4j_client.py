from neo4j import GraphDatabase

from founder.graph.config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    NEO4J_DATABASE,
)


class Neo4jClient:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USERNAME,
                NEO4J_PASSWORD,
            ),
        )

        self.database = NEO4J_DATABASE

    def close(self):

        self.driver.close()

    def execute(
        self,
        query,
        parameters=None,
    ):

        with self.driver.session(
            database=self.database
        ) as session:

            return session.run(
                query,
                parameters or {},
            ).consume()