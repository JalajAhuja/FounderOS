# FounderOS Architecture

FounderOS answers questions across filings, earnings calls, XBRL facts, graph relationships, news metadata, and multiple reporting periods. Qdrant handles semantic text retrieval, Neo4j handles relationships and provenance, and XBRL remains the source for numerical facts. LangGraph coordinates the tools; the generation layer receives an explicit evidence package.

The response path is: query analysis, retrieval planning, source retrieval, evidence normalization, sufficiency/correction, temporal reasoning, contradiction detection, synthesis, citation, and tracing. FastAPI exposes the backend and the frontend renders the answer, evidence, timeline, and safe execution statuses.