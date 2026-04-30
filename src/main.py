from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Silero TTS Server",
    description="A simple, robust, and performant REST API that wraps the Silero TTS engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
