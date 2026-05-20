from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import Settings, get_settings
from src.routers import setup_routers
from src.tts.exceptions import TTSEngineError
from src.tts.models import TTSConfig, load_config_model
from src.tts.silero_tts_engine import SileroTTSEngine, create_silero_engine


def get_engine(request: Request) -> SileroTTSEngine:
    """Dependency to get the TTS engine from app state."""
    engine = request.app.state.engine
    if engine is None:
        raise RuntimeError("TTS engine not initialized")
    return engine


EngineDep = Annotated[SileroTTSEngine, Depends(get_engine)]


SettingsDep = Annotated[Settings, Depends(get_settings)]


async def tts_exception_handler(request: Request, exc: TTSEngineError) -> JSONResponse:
    """Global exception handler for TTS engine errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""

    app_settings = get_settings()
    config_model = load_config_model(app_settings.TTS_CONFIG_PATH)
    config = TTSConfig(
        device=app_settings.TTS_DEVICE,
        sample_rate=app_settings.TTS_SAMPLE_RATE,
        max_concurrent_per_model=app_settings.TTS_MAX_CONCURRENT_PER_MODEL,
    )
    app.state.engine = create_silero_engine(config, config_model)

    yield


app = FastAPI(
    title="Silero TTS Server",
    description="A simple, robust, and performant REST API that wraps the Silero TTS engine",
    version="0.1.0",
    lifespan=lifespan,
)

app_settings = get_settings()
allowed_origins = app_settings.TTS_ALLOWED_ORIGINS
origins = ["*"] if allowed_origins == "*" else allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(TTSEngineError, tts_exception_handler)

setup_routers(app)
