"""Structured execution tracing for reproducibility and observability."""

import json
import time
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Optional
from functools import wraps
import os


TRACING_ENABLED = (
    os.getenv("TRACING_ENABLED", "true").lower() == "true"
)


@dataclass
class TraceEvent:
    """A single event in the execution trace."""

    timestamp: float
    node_name: str
    event_type: str  # "start", "end", "error"
    latency_ms: float | None = None
    input_sample: dict | None = None
    output_sample: dict | None = None
    error: str | None = None


@dataclass
class Trace:
    """Complete execution trace for a single query."""

    trace_id: str
    query: str
    model_config: dict = field(default_factory=dict)
    prompt_version: str = "v1"
    events: list[TraceEvent] = field(default_factory=list)
    total_latency_ms: float = 0.0
    final_answer_tokens: int | None = None
    error: str | None = None
    langfuse_trace_id: str | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "model_config": self.model_config,
            "prompt_version": self.prompt_version,
            "events": [asdict(e) for e in self.events],
            "total_latency_ms": self.total_latency_ms,
            "final_answer_tokens": self.final_answer_tokens,
            "error": self.error,
            "langfuse_trace_id": self.langfuse_trace_id,
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), default=str)


_current_trace: Trace | None = None


def get_current_trace() -> Trace | None:
    """Retrieve the active trace (thread-unsafe for now)."""
    return _current_trace


def set_current_trace(trace: Trace | None) -> None:
    """Set the active trace (thread-unsafe for now)."""
    global _current_trace
    _current_trace = trace


def trace_node(node_name: str):
    """Decorator to trace a node's execution."""

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:

            if not TRACING_ENABLED:
                return func(*args, **kwargs)

            trace = get_current_trace()

            if not trace:
                return func(*args, **kwargs)

            start_time = time.perf_counter()

            try:

                # Record start event.
                trace.events.append(
                    TraceEvent(
                        timestamp=start_time,
                        node_name=node_name,
                        event_type="start",
                        input_sample=_sample_input(*args, **kwargs),
                    )
                )

                result = func(*args, **kwargs)

                # Record end event.
                latency_ms = (time.perf_counter() - start_time) * 1000

                trace.events.append(
                    TraceEvent(
                        timestamp=time.perf_counter(),
                        node_name=node_name,
                        event_type="end",
                        latency_ms=latency_ms,
                        output_sample=_sample_output(result),
                    )
                )

                return result

            except Exception as error:

                latency_ms = (time.perf_counter() - start_time) * 1000

                trace.events.append(
                    TraceEvent(
                        timestamp=time.perf_counter(),
                        node_name=node_name,
                        event_type="error",
                        latency_ms=latency_ms,
                        error=str(error),
                    )
                )

                raise

        return wrapper

    return decorator


def _sample_input(*args, **kwargs) -> dict | None:
    """Extract a small sample from input arguments."""

    if not args and not kwargs:
        return None

    sample = {}

    if args and hasattr(args[0], "__dict__"):
        arg_dict = vars(args[0])
        if "query" in arg_dict:
            sample["query"] = arg_dict["query"][:100]

    for key in ["query", "ticker", "top_k"]:
        if key in kwargs:
            val = kwargs[key]
            if isinstance(val, str):
                sample[key] = val[:100]
            else:
                sample[key] = val

    return sample if sample else None


def _sample_output(output: Any) -> dict | None:
    """Extract a small sample from output."""

    if isinstance(output, dict):

        sample = {}

        if "evidence" in output:
            sample["evidence_count"] = len(output.get("evidence", []))

        if "answer" in output:
            answer = output.get("answer", "")
            sample["answer_length"] = len(answer)

        if "error" in output:
            sample["has_error"] = bool(output["error"])

        return sample if sample else None

    return None
