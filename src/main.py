from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.routers import health, setup_routers
from src.tts.models import TTSConfig, load_config_model
from src.tts.silero_tts_engine import SileroTTSEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    config_model = load_config_model(settings.TTS_CONFIG_PATH)
    config = TTSConfig(
        device=settings.TTS_DEVICE,
        sample_rate=settings.TTS_SAMPLE_RATE,
        max_concurrent_per_model=settings.TTS_MAX_CONCURRENT_PER_MODEL,
    )
    engine = SileroTTSEngine(config, config_model)
    setup_routers(app, engine, settings.TTS_ALLOWED_ORIGINS)
    yield


app = FastAPI(
    title="Silero TTS Server",
    description="A simple, robust, and performant REST API that wraps the Silero TTS engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
