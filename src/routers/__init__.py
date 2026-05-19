from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.tts.exceptions import TTSEngineError
from src.tts.silero_tts_engine import SileroTTSEngine


def get_engine(request: Request) -> SileroTTSEngine:
    """Dependency to get the TTS engine from app state."""
    engine = request.app.state.engine
    if engine is None:
        raise RuntimeError("TTS engine not initialized")
    return engine


EngineDep = Annotated[SileroTTSEngine, Depends(get_engine)]


async def tts_exception_handler(request: Request, exc: TTSEngineError) -> JSONResponse:
    """Global exception handler for TTS engine errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def setup_routers(app: FastAPI, engine: SileroTTSEngine, allowed_origins: str) -> None:
    """Configure routers and middleware for the application."""
    app.state.engine = engine

    origins = ["*"] if allowed_origins == "*" else allowed_origins.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(TTSEngineError, tts_exception_handler)

    from src.routers import locales, process, voices

    app.include_router(locales.router)
    app.include_router(voices.router)
    app.include_router(process.router)
