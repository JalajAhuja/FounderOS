"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from founder.api.routes import health, stream

app = FastAPI(title="FounderOS API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(stream.router)


@app.get("/")
async def root():
    """Root endpoint."""

    return {"message": "FounderOS API", "version": "0.1.0"}
