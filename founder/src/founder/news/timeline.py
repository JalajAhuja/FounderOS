"""Date-aware event queries."""

from datetime import date, datetime, timedelta
from typing import Iterable
from founder.news.events import Event


def _parse(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


def events_near_date(events: Iterable[Event], target: str, window_days: int = 30) -> list[Event]:
    target_date = _parse(target)
    if target_date is None:
        return []
    window = timedelta(days=window_days)
    return [event for event in events if (published := _parse(event.published_at)) is not None and abs(published - target_date) <= window]