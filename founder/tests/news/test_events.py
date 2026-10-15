from founder.news.event_resolution import resolve_events
from founder.news.events import extract_events
from founder.news.timeline import events_near_date


def test_event_preserves_source_provenance():
    events = extract_events([{
        "document_id": "news_MSFT_0001",
        "ticker": "MSFT",
        "title": "Microsoft launches a new AI product",
        "published_at": "2025-06-15T10:00:00Z",
        "metadata": {"url": "https://example.test/story", "domain": "example.test"},
    }])
    assert events[0].category == "product_launch"
    assert events[0].source_url == "https://example.test/story"
    assert events[0].evidence_id == "news:news_MSFT_0001:0"


def test_events_are_resolved_and_date_filtered():
    articles = [
        {"document_id": "a", "title": "Company announces partnership", "published_at": "2025-01-02", "ticker": "MSFT"},
        {"document_id": "a", "title": "Company announces partnership", "published_at": "2025-01-02", "ticker": "MSFT"},
    ]
    events = resolve_events(extract_events(articles))
    assert len(events) == 1
    assert events_near_date(events, "2025-01-10", window_days=10) == events
