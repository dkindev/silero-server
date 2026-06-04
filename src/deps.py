from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.datastructures import State

from src.config import Settings, get_settings
from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.engine import SileroTTSEngine
from src.tts.models import TTSConfig


def add_engine(app: FastAPI):
    """Create and store a SileroTTSEngine on app.state."""
    settings = get_settings()

    import torch

    torch.set_num_threads(settings.TTS_TORCH_NUM_THREADS)
    torch.set_num_interop_threads(settings.TTS_TORCH_NUM_INTEROP_THREADS)
    if settings.TTS_TORCH_FLUSH_DENORMAL and hasattr(torch, "set_flush_denormal"):
        torch.set_flush_denormal(True)

    config = TTSConfig(
        device=settings.TTS_TORCH_DEVICE,
        sample_rate=settings.TTS_SAMPLE_RATE,
        max_models=settings.TTS_MAX_MODELS,
        max_concurrent_per_model=settings.TTS_MAX_CONCURRENT_PER_MODEL,
        models_dir=settings.TTS_MODELS_DIR,
    )
    storage = SileroTTSYamlConfigStorage(settings.TTS_CONFIG_PATH)
    app.state.engine = SileroTTSEngine(config=config, storage=storage)


def get_engine_from_request(request: Request) -> SileroTTSEngine:
    """Dependency to get the TTS engine from request."""
    engine = get_engine(request.app.state)
    if engine is None:
        raise RuntimeError("TTS engine not initialized")
    return engine


def get_engine(state: State) -> SileroTTSEngine:
    """Dependency to get the TTS engine from app state."""
    return state.engine


EngineDep = Annotated[SileroTTSEngine, Depends(get_engine_from_request)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
