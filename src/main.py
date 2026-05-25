from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.handlers import global_exception_handler
from src.routers import setup_routers
from src.tts.models import TTSConfig
from src.tts.silero_tts_engine import create_silero_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""

    app_settings = get_settings()

    import torch

    torch.set_num_threads(2)

    config = TTSConfig(
        device=app_settings.TTS_DEVICE,
        sample_rate=app_settings.TTS_SAMPLE_RATE,
        max_models=2,
        max_concurrent_per_model=app_settings.TTS_MAX_CONCURRENT_PER_MODEL,
    )
    app.state.engine = create_silero_engine(config, app_settings.TTS_CONFIG_PATH)

    yield

    engine = app.state.engine
    if engine:
        await engine.shutdown()


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

app.add_exception_handler(Exception, global_exception_handler)

setup_routers(app)
