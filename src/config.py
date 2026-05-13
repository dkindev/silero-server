from typing import Literal

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    TTS_DEVICE: str = "cpu"
    """Device to run TTS model on: 'cpu' or 'cuda'."""

    TTS_SAMPLE_RATE: Literal[8000, 16000, 22050, 24000, 48000] = 48000
    """Audio sample rate in Hz for TTS output."""

    TTS_MAX_TEXT_LENGTH: int = Field(1000, ge=1, le=10000)
    """Maximum length of text input for TTS synthesis."""

    TTS_ALLOWED_ORIGINS: str = "*"
    """Allowed CORS origins, or '*' for all origins."""

    TTS_SHUTDOWN_TIMEOUT: int = Field(10, ge=1)
    """Timeout in seconds for graceful shutdown."""


settings = Settings()
