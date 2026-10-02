"""Optional Langfuse integration for FounderOS traces."""

import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from founder.observability.tracer import Trace


LANGFUSE_ENABLED = (
    os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
)

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")


def push_trace_to_langfuse(trace: "Trace") -> Optional[str]:
    """Push a trace to Langfuse. Returns trace ID if successful, None otherwise.
    
    This is a no-op stub if Langfuse is disabled or credentials are missing.
    """

    if not LANGFUSE_ENABLED or not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        return None

    try:

        from langfuse import Langfuse

        client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
        )

        # Create a trace in Langfuse from the Trace object.
        trace_dict = trace.to_dict()

        # For now, just log the trace data as an event.
        # Full Langfuse integration (hierarchy, generations, scores) is
        # Step 25's job.

        client.trace(
            name="founder_query",
            trace_id=trace.trace_id,
            metadata={
                "query": trace.query,
                "total_latency_ms": trace.total_latency_ms,
                "event_count": len(trace.events),
            },
        )

        return trace.trace_id

    except Exception as error:

        print(f"WARNING: Langfuse push failed: {error}")

        return None
