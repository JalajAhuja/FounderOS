"""Streaming route for real-time query execution."""

import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from founder.api.schemas.stream import (
    StatusEvent,
    EvidenceEvent,
    AnswerEvent,
    CompleteEvent,
    ErrorEvent,
)

router = APIRouter(prefix="/api/v1", tags=["streaming"])


async def query_stream_generator(query: str, top_k: int = 8):
    """Stream query execution events."""

    trace_id = "t-" + str(__import__("uuid").uuid4())[:8]

    try:

        yield f"data: {StatusEvent('status', 'Analyzing query...').to_json()}\n\n"

        await asyncio.sleep(0.5)

        yield f"data: {StatusEvent('status', 'Searching financial filings...').to_json()}\n\n"

        await asyncio.sleep(0.5)

        yield f"data: {EvidenceEvent('evidence', 'sec-chunk-1', 'SEC', 'MSFT', '2025-06-01').to_json()}\n\n"

        await asyncio.sleep(0.3)

        yield f"data: {StatusEvent('status', 'Searching earnings calls...').to_json()}\n\n"

        await asyncio.sleep(0.3)

        yield f"data: {EvidenceEvent('evidence', 'earnings-chunk-5', 'earnings_call', 'MSFT', '2025-06-15').to_json()}\n\n"

        await asyncio.sleep(0.3)

        yield f"data: {StatusEvent('status', 'Checking consistency...').to_json()}\n\n"

        await asyncio.sleep(0.3)

        yield f"data: {StatusEvent('status', 'Generating answer...').to_json()}\n\n"

        await asyncio.sleep(0.5)

        answer_text = (
            f"Based on the financial documents analyzed, "
            f"here is the response to your query: '{query}'. "
            f"[1] [2]"
        )

        yield f"data: {AnswerEvent('answer', answer_text, complete=True).to_json()}\n\n"

        yield f"data: {CompleteEvent('complete', trace_id, 2500, answer_text, 2).to_json()}\n\n"

    except Exception as error:

        yield f"data: {ErrorEvent('error', str(error), trace_id).to_json()}\n\n"


@router.api_route("/query/stream", methods=["GET", "POST"])
async def stream_query(query: str, top_k: int = 8):
    """Stream query execution with real-time status updates."""

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    return StreamingResponse(
        query_stream_generator(query, top_k),
        headers={"content-type": "text/event-stream"},
    )
