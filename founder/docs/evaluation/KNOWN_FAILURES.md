# Known Failures

- Live graph and vector tests require the optional `neo4j` and `qdrant-client` dependencies and running services.
- News categories use deterministic keywords and may need human review.
- Empty or unlabeled evaluation sets cannot produce meaningful quality metrics.
- The demo stream route is a compatibility surface; production deployments should connect it to the real agent runner.