from typing import Annotated

from fastapi import Depends, Request

from src.config import Settings, get_settings
from src.tts.silero_tts_engine import SileroTTSEngine


def get_engine(request: Request) -> SileroTTSEngine:
    """Dependency to get the TTS engine from app state."""
    engine = request.app.state.engine
    if engine is None:
        raise RuntimeError("TTS engine not initialized")
    return engine


EngineDep = Annotated[SileroTTSEngine, Depends(get_engine)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
