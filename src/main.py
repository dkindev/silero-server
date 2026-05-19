from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.routers import get_settings, setup_routers
from src.tts.models import TTSConfig, load_config_model
from src.tts.silero_tts_engine import SileroTTSEngine


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
    engine = SileroTTSEngine(config, config_model)
    setup_routers(app, engine, app_settings.TTS_ALLOWED_ORIGINS)
    yield


app = FastAPI(
    title="Silero TTS Server",
    description="A simple, robust, and performant REST API that wraps the Silero TTS engine",
    version="0.1.0",
    lifespan=lifespan,
)
