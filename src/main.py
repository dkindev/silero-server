from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.deps import add_engine, get_engine
from src.handlers import add_cors, add_global_exception_handler
from src.logger import setup_logging
from src.routers import setup_routers

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""

    add_engine(app.state)

    engine = get_engine(app.state)
    if engine:
        await engine.warmup()

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

add_global_exception_handler(app)
add_cors(app)
setup_routers(app)
