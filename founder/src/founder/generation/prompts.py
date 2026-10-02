"""Synthesis prompt + structured-output schema for the `synthesize` node.

Every claim must reference `evidence_ids` chosen from the IDs shown in the
evidence block -- the model is never allowed to invent an evidence_id, a
date, a source, or a URL. Citations themselves are built deterministically
in `citations.py` from the referenced evidence, not from model output.
"""

from founder.retrieval.evidence import Evidence


SYSTEM_PROMPT = """
You are FounderOS, a research assistant that answers strategic questions
about public companies using only the evidence provided to you.

Rules:

- Only use the evidence given below. Never use outside knowledge.
- Never invent dates, numbers, evidence IDs, or sources.
- Every claim must list the exact evidence_id(s) (shown as `id=...` next
  to each evidence item) that support it. Do not reference an id that was
  not shown to you.
- Distinguish claim types:
    "fact"          -> a precise financial/structured fact (XBRL)
    "source_claim"  -> a management/company statement (earnings, SEC, news)
    "inference"     -> your own inference, not stated directly in evidence
    "uncertainty"   -> evidence is ambiguous, conflicting, or insufficient
- If the evidence is insufficient or conflicting, say so explicitly in
  `limitations` instead of guessing.
""".strip()


ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "evidence_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "claim_type": {
                        "type": "string",
                        "enum": [
                            "fact",
                            "source_claim",
                            "inference",
                            "uncertainty",
                        ],
                    },
                    "confidence": {"type": "number"},
                },
                "required": [
                    "text",
                    "evidence_ids",
                    "claim_type",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
        "limitations": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["answer", "claims", "limitations"],
    "additionalProperties": False,
}


def format_evidence_block(
    evidence: list[Evidence],
) -> str:

    lines = []

    for item in evidence:

        lines.append(
            f"id={item.evidence_id} source={item.source} "
            f"ticker={item.ticker} date={item.published_at}\n"
            f"{item.text}"
        )

    return "\n\n".join(lines)
