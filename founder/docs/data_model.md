# FounderOS Data Model

Primary records are source-aware documents, facts, earnings calls, and news metadata. Chunks carry `chunk_id`, `document_id`, `ticker`, source, document type, and publication date. Evidence records add a stable `evidence_id`; claims refer only to those IDs.

Graph relationships retain source, publication/validity dates, chunk and document IDs, evidence, confidence, and ticker. Event records retain URL and domain without requiring article-text redistribution.