"""Answer synthesis (Step 18): calls the LLM with a structured-output
schema, then validates and deterministically re-derives citations so
nothing in the final answer can cite evidence that wasn't retrieved.
"""

import json

from openai import OpenAI

from founder.agent.config import AGENT_MODEL, OPENAI_API_KEY
from founder.generation.citations import build_citations
from founder.generation.prompts import (
    ANSWER_SCHEMA,
    SYSTEM_PROMPT,
    format_evidence_block,
)
from founder.generation.schemas import Claim, GeneratedAnswer
from founder.retrieval.evidence import Evidence


def generate_answer(
    query: str,
    evidence: list[Evidence],
    sufficiency: dict | None = None,
) -> GeneratedAnswer:

    if not evidence:

        return GeneratedAnswer(
            answer=(
                "I don't have enough evidence to answer this question."
            ),
            limitations=["No evidence retrieved."],
        )

    evidence_by_id = {item.evidence_id: item for item in evidence}

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question: {query}\n\n"
                    f"Evidence:\n{format_evidence_block(evidence)}"
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "founderos_answer",
                "strict": True,
                "schema": ANSWER_SCHEMA,
            },
        },
    )

    payload = json.loads(response.choices[0].message.content)

    valid_claims = []

    for raw_claim in payload.get("claims", []):

        # Drop any evidence_id the model referenced that wasn't actually
        # retrieved -- never cite evidence not actually retrieved.
        evidence_ids = [
            evidence_id
            for evidence_id in raw_claim.get("evidence_ids", [])
            if evidence_id in evidence_by_id
        ]

        if not evidence_ids:
            continue

        valid_claims.append(
            Claim(
                text=raw_claim["text"],
                evidence_ids=evidence_ids,
                claim_type=raw_claim.get(
                    "claim_type", "source_claim"
                ),
                confidence=float(
                    raw_claim.get("confidence", 0.5)
                ),
            )
        )

    referenced_ids = [
        evidence_id
        for claim in valid_claims
        for evidence_id in claim.evidence_ids
    ]

    citations = build_citations(evidence_by_id, referenced_ids)

    limitations = list(payload.get("limitations", []))

    if sufficiency and not sufficiency.get("sufficient", True):

        limitations.append(
            "Evidence coverage may be incomplete: "
            + "; ".join(sufficiency.get("reason", []))
        )

    return GeneratedAnswer(
        answer=payload.get("answer", ""),
        claims=valid_claims,
        citations=citations,
        limitations=limitations,
    )
