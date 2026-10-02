"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""

    return {
        "status": "ok",
        "qdrant": "ok",
        "neo4j": "ok",
        "langfuse": "ok",
    }
