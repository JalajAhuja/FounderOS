# ============================================================
# NODE TYPES
# ============================================================

# Entity types extracted by the LLM (see SYSTEM_PROMPT below).
NODE_TYPES = [
    "Company",
    "Person",
    "Product",
    "Technology",
    "Event",
    "Market",
    "Metric",
]

# Structural nodes written directly by the ingestion pipeline
# (never produced by the LLM extraction step).
STRUCTURAL_NODE_TYPES = [
    "Chunk",
    "Document",
]


# ============================================================
# RELATIONSHIP TYPES
# ============================================================

# Relationship types the LLM is allowed to extract.
RELATIONSHIP_TYPES = [
    "EXECUTIVE_OF",
    "FOUNDED",
    "ACQUIRED",
    "COMPETES_WITH",
    "PARTNERS_WITH",
    "INVESTS_IN",
    "USES",
    "BUILDS",
    "OFFERS",
    "LAUNCHED",
    "ANNOUNCED",
    "AFFECTS",
    "DRIVES",
    "MENTIONS",
    "GUIDANCE_CHANGE",
]

# Provenance/structural relationship types written directly by the
# ingestion pipeline (never produced by the LLM extraction step).
STRUCTURAL_RELATIONSHIP_TYPES = [
    "MENTIONED_IN",
    "SUPPORTED_BY",
    "PART_OF",
]


# ============================================================
# EXTRACTION PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a financial and strategic intelligence
knowledge-graph extraction system.

Your job is to extract ONLY facts explicitly
supported by the supplied text.

Do NOT infer relationships that are not stated.

Do NOT use outside knowledge.

Return JSON with:

{
  "entities": [
    {
      "name": "...",
      "type": "Company|Person|Product|Technology|Event|Market|Metric"
    }
  ],
  "relationships": [
    {
      "source": "...",
      "source_type": "...",
      "relationship": "...",
      "target": "...",
      "target_type": "...",
      "evidence": "...",
      "confidence": 0.0
    }
  ]
}

Rules:

1. Only extract entities explicitly mentioned.
2. Only create relationships supported by the text.
3. Use canonical company names when clearly stated.
4. Do not invent entities.
5. Do not infer ownership merely because two entities
   appear in the same sentence.
6. Keep relationship types within the supplied schema.
7. Evidence must be a short exact quote from the input.
8. Confidence must reflect extraction certainty,
   not whether the underlying business claim is true.
9. A relationship without evidence is invalid.
10. If there are no relationships, return an empty list.
"""
