from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.datastructures import State

from src.config import Settings, get_settings
from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.models import TTSConfig
from src.tts.provider import SileroTTSModelProvider
from src.tts.silero_tts_engine import SileroTTSEngine


def add_engine(app: FastAPI):
    """Create and store a SileroTTSEngine on app.state."""
    settings = get_settings()
    config = TTSConfig(
        device=settings.TTS_TORCH_DEVICE,
        sample_rate=settings.TTS_SAMPLE_RATE,
        max_models=settings.TTS_MAX_MODELS,
        max_concurrent_per_model=settings.TTS_MAX_CONCURRENT_PER_MODEL,
    )
    storage = SileroTTSYamlConfigStorage(settings.TTS_CONFIG_PATH)
    provider = SileroTTSModelProvider()
    app.state.engine = SileroTTSEngine(config=config, storage=storage, provider=provider)


def get_engine_from_request(request: Request) -> SileroTTSEngine:
    """Dependency to get the TTS engine from request."""
    engine = get_engine(request.app.state)
    if engine is None:
        raise RuntimeError("TTS engine not initialized")
    return engine


def get_engine(state: State) -> SileroTTSEngine:
    """Dependency to get the TTS engine from app state."""
    return state.engine


def setup_torch():
    """Setting up PyTorch."""
    app_settings = get_settings()

    import torch

    torch.set_num_threads(app_settings.TTS_TORCH_NUM_THREADS)
    torch.set_num_interop_threads(app_settings.TTS_TORCH_NUM_INTEROP_THREADS)
    if app_settings.TTS_TORCH_FLUSH_DENORMAL and hasattr(torch, "set_flush_denormal"):
        torch.set_flush_denormal(True)


EngineDep = Annotated[SileroTTSEngine, Depends(get_engine_from_request)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
