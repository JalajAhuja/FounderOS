"""Manual verification script for tracing (Step 19)."""

import uuid
import time
from founder.observability.tracer import Trace, set_current_trace, trace_node
from founder.agent.runner import run_query


def main():

    print("\n== FounderOS Tracing Test ==\n")

    trace_id = str(uuid.uuid4())[:8]

    trace = Trace(
        trace_id=trace_id,
        query="What did Microsoft say about AI monetization?",
        model_config={"model": "gpt-4o", "temperature": 0.7},
        prompt_version="v1",
    )

    set_current_trace(trace)

    start = time.perf_counter()

    try:

        result = run_query(trace.query)

        trace.total_latency_ms = (time.perf_counter() - start) * 1000

    except Exception as error:

        trace.total_latency_ms = (time.perf_counter() - start) * 1000
        trace.error = str(error)

    finally:

        set_current_trace(None)

    print(f"Trace ID: {trace_id}")
    print(f"Total Latency: {trace.total_latency_ms:.0f}ms")
    print(f"Events: {len(trace.events)}")

    for event in trace.events[:10]:

        print(
            f"  {event.node_name:25s} | "
            f"{event.event_type:5s} | "
            f"{event.latency_ms if event.latency_ms else 0:6.0f}ms"
        )

    if len(trace.events) > 10:
        print(f"  ... and {len(trace.events) - 10} more events")

    print(f"\nJSON size: {len(trace.to_json())} bytes")

    print(f"\nTrace is reproducible via:")
    print(f"  trace_id={trace_id}")
    print(f"  query={trace.query}")
    print(f"  model={trace.model_config}")


if __name__ == "__main__":
    main()
