"""Unit tests for the tracing module."""

import json
from founder.observability.tracer import (
    Trace,
    TraceEvent,
    get_current_trace,
    set_current_trace,
    trace_node,
)


def test_trace_event_creation():

    event = TraceEvent(
        timestamp=1.0,
        node_name="test_node",
        event_type="start",
        latency_ms=None,
    )

    assert event.node_name == "test_node"
    assert event.event_type == "start"


def test_trace_creation_and_serialization():

    trace = Trace(
        trace_id="trace-123",
        query="What is Microsoft's AI strategy?",
        total_latency_ms=1500.0,
    )

    trace.events.append(
        TraceEvent(
            timestamp=1.0,
            node_name="analyze_query",
            event_type="end",
            latency_ms=50.0,
        )
    )

    trace_dict = trace.to_dict()

    assert trace_dict["trace_id"] == "trace-123"
    assert len(trace_dict["events"]) == 1
    assert trace_dict["events"][0]["node_name"] == "analyze_query"


def test_trace_json_serialization():

    trace = Trace(
        trace_id="t1",
        query="test",
        total_latency_ms=100.0,
    )

    json_str = trace.to_json()

    assert isinstance(json_str, str)

    parsed = json.loads(json_str)

    assert parsed["trace_id"] == "t1"


def test_get_and_set_current_trace():

    trace1 = Trace(trace_id="t1", query="q1")

    set_current_trace(trace1)

    assert get_current_trace() == trace1

    set_current_trace(None)

    assert get_current_trace() is None


def test_trace_node_decorator_records_events():

    trace = Trace(trace_id="t1", query="test")

    set_current_trace(trace)

    @trace_node("test_node")
    def my_function(x):
        return x + 1

    result = my_function(5)

    assert result == 6
    assert len(trace.events) >= 2
    assert trace.events[0].event_type == "start"
    assert trace.events[1].event_type == "end"

    set_current_trace(None)


def test_trace_node_records_error():

    trace = Trace(trace_id="t1", query="test")

    set_current_trace(trace)

    @trace_node("error_node")
    def my_function():
        raise ValueError("test error")

    try:
        my_function()
    except ValueError:
        pass

    assert any(e.event_type == "error" for e in trace.events)

    set_current_trace(None)
