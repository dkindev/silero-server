from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.deps import add_engine, get_engine
from src.handlers import add_cors, add_global_exception_handler
from src.routers import setup_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""

    add_engine(app)

    yield

    engine = get_engine(app.state)
    if engine:
        await engine.shutdown()


app = FastAPI(
    title="Silero TTS Server",
    description="A simple, robust, and performant REST API that wraps the Silero TTS engine",
    version="0.1.0",
    lifespan=lifespan,
)

add_cors(app)
add_global_exception_handler(app)
setup_routers(app)
