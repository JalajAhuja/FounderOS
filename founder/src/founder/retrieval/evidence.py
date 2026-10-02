from dataclasses import dataclass, field
from typing import Any


@dataclass
class Evidence:

    evidence_id: str

    source: str

    text: str

    score: float = 0.0

    ticker: str | None = None

    document_id: str | None = None

    chunk_id: str | None = None

    document_type: str | None = None

    section: str | None = None

    published_at: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


def qdrant_to_evidence(point):

    payload = (
        point.payload
        or {}
    )

    return Evidence(

        evidence_id=(
            f"qdrant:"
            f"{payload.get('chunk_id')}"
        ),

        source=(
            payload.get("source")
            or "Qdrant"
        ),

        text=payload.get(
            "text",
            "",
        ),

        score=float(
            point.score
            or 0.0
        ),

        ticker=payload.get(
            "ticker"
        ),

        document_id=payload.get(
            "document_id"
        ),

        chunk_id=payload.get(
            "chunk_id"
        ),

        document_type=payload.get(
            "document_type"
        ),

        section=payload.get(
            "section"
        ),

        published_at=payload.get(
            "published_at"
        ),

        metadata=payload,
    )


def fact_to_evidence(
    fact,
    index,
):

    ticker = fact.get(
        "ticker"
    )

    concept = fact.get(
        "concept"
    )

    value = fact.get(
        "value"
    )

    unit = fact.get(
        "unit"
    )

    start = fact.get(
        "start"
    )

    end = fact.get(
        "end"
    )

    text = (
        f"{ticker} | "
        f"{concept} | "
        f"value={value} "
        f"{unit or ''} | "
        f"period={start or ''}"
        f" to {end or ''} | "
        f"FY={fact.get('fiscal_year')} | "
        f"FP={fact.get('fiscal_period')}"
    )

    return Evidence(

        evidence_id=(
            f"fact:{ticker}:"
            f"{concept}:"
            f"{end}:"
            f"{index}"
        ),

        source="XBRL",

        text=text,

        score=1.0,

        ticker=ticker,

        document_id=None,

        chunk_id=None,

        document_type="financial_fact",

        section=concept,

        published_at=fact.get(
            "filed"
        ),

        metadata={
            "concept": concept,
            "value": value,
            "unit": unit,
            "start": start,
            "end": end,
            "fiscal_year": fact.get(
                "fiscal_year"
            ),
            "fiscal_period": fact.get(
                "fiscal_period"
            ),
            "form": fact.get(
                "form"
            ),
            "frame": fact.get(
                "frame"
            ),
            "accession": fact.get(
                "accn"
            ),
        },
    )


def news_to_evidence(
    article,
    index,
):

    metadata = (
        article.get("metadata") or {}
    )

    return Evidence(

        evidence_id=(
            f"news:"
            f"{article.get('document_id')}:"
            f"{index}"
        ),

        source="News",

        text=article.get("title", ""),

        score=1.0,

        ticker=article.get("ticker"),

        document_id=article.get("document_id"),

        chunk_id=None,

        document_type="news",

        section=None,

        published_at=article.get("published_at"),

        metadata={
            "url": metadata.get("url"),
            "domain": metadata.get("domain"),
            "year": metadata.get("year"),
        },
    )


def graph_to_evidence(
    item,
    index,
):

    text = (
        f"{item.get('source')} "
        f"--{item.get('relationship')}--> "
        f"{item.get('target')}. "
        f"Evidence: "
        f"{item.get('evidence') or ''}"
    )

    return Evidence(

        evidence_id=(
            f"graph:"
            f"{item.get('chunk_id')}:"
            f"{index}"
        ),

        source="Neo4j",

        text=text,

        score=float(
            item.get(
                "confidence"
            )
            or 0.0
        ),

        document_id=item.get(
            "document_id"
        ),

        chunk_id=item.get(
            "chunk_id"
        ),

        document_type="graph_relationship",

        section=item.get(
            "relationship"
        ),

        published_at=item.get(
            "published_at"
        ),

        metadata={
            "source_entity": item.get(
                "source"
            ),
            "target_entity": item.get(
                "target"
            ),
            "relationship": item.get(
                "relationship"
            ),
            "graph_source": item.get(
                "source_type"
            ),
        },
    )