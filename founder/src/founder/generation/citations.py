from founder.generation.schemas import Citation
from founder.retrieval.evidence import Evidence


def build_citations(
    evidence_by_id: dict[str, Evidence],
    referenced_ids: list[str],
) -> list[Citation]:
    """Deterministically build citations from evidence already retrieved.

    Citation text/source/date always come from the Evidence object, never
    from the LLM response, so a citation can never carry an invented date
    or source.
    """

    assigned: dict[str, int] = {}

    citations = []

    for evidence_id in referenced_ids:

        if evidence_id in assigned:
            continue

        item = evidence_by_id.get(evidence_id)

        if item is None:
            continue

        citation_id = len(assigned) + 1

        assigned[evidence_id] = citation_id

        citations.append(
            Citation(
                citation_id=citation_id,
                evidence_id=evidence_id,
                citation_text=f"[{citation_id}]",
                source=item.source,
                date=item.published_at,
            )
        )

    return citations
