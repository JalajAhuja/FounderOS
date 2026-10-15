"""Deduplication and deterministic event ordering."""

from collections import OrderedDict
from collections.abc import Iterable

from founder.news.events import Event


def resolve_events(events: Iterable[Event]) -> list[Event]:
    """Keep the strongest record for each document/category pair."""
    resolved: OrderedDict[tuple[str | None, str], Event] = OrderedDict()
    for event in events:
        key = (event.document_id, event.category)
        current = resolved.get(key)
        if current is None or event.confidence > current.confidence:
            resolved[key] = event
    return sorted(resolved.values(), key=lambda event: event.published_at or "")
