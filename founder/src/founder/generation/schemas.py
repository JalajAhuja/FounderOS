from dataclasses import dataclass, field


@dataclass
class Claim:

    text: str

    evidence_ids: list[str]

    claim_type: str

    confidence: float


@dataclass
class Citation:

    citation_id: int

    evidence_id: str

    citation_text: str

    source: str

    date: str | None


@dataclass
class GeneratedAnswer:

    answer: str

    claims: list[Claim] = field(default_factory=list)

    citations: list[Citation] = field(default_factory=list)

    limitations: list[str] = field(default_factory=list)
