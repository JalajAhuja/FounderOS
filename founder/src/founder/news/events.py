"""Conservative event extraction from licensed news metadata."""

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

EVENT_KEYWORDS = {
    "product_launch": ("launch", "introduced", "unveiled", "released"),
    "acquisition": ("acquire", "acquisition", "bought", "merger"),
    "regulation": ("regulator", "regulation", "antitrust", "law"),
    "pricing_change": ("price", "pricing", "subscription", "fee"),
    "leadership_change": ("ceo", "executive", "resign", "appointed"),
    "partnership": ("partner", "partnership", "collaboration"),
    "security_incident": ("breach", "outage", "security", "cyberattack"),
    "guidance_change": ("guidance", "forecast", "outlook"),
    "market_event": ("shares", "stock", "market", "investor"),
    "macro_event": ("inflation", "rates", "economy", "recession"),
}


@dataclass(frozen=True)
class Event:
    event_id: str
    category: str
    title: str
    ticker: str | None
    published_at: str | None
    source_url: str | None
    domain: str | None
    document_id: str | None
    evidence_id: str | None
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _category(title: str) -> tuple[str, float]:
    lowered = title.casefold()
    matches = [(category, sum(word in lowered for word in words)) for category, words in EVENT_KEYWORDS.items()]
    category, score = max(matches, key=lambda item: item[1])
    return (category, min(1.0, 0.55 + score * 0.12)) if score else ("market_event", 0.25)


def extract_events(articles: Iterable[dict[str, Any]]) -> list[Event]:
    """Extract typed events while retaining the article as the evidence source."""
    events: list[Event] = []
    for index, article in enumerate(articles):
        title = str(article.get("title") or article.get("text") or "").strip()
        if not title:
            continue
        category, confidence = _category(title)
        document_id = article.get("document_id")
        metadata = article.get("metadata") or {}
        events.append(Event(
            event_id=f"event:{document_id or index}", category=category, title=title,
            ticker=article.get("ticker"), published_at=article.get("published_at"),
            source_url=metadata.get("url"), domain=metadata.get("domain"),
            document_id=document_id, evidence_id=f"news:{document_id}:{index}" if document_id else None,
            confidence=confidence,
        ))
    return events
