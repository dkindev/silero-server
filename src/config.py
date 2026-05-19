from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    TTS_DEVICE: str = "cpu"
    """Device to run TTS model on: 'cpu', 'cuda', or 'xpu'. Falls back to 'cpu' at runtime if unavailable."""

    @field_validator("TTS_DEVICE")
    @classmethod
    def device_must_be_valid(cls, v: str) -> str:
        valid = {"cpu", "cuda", "xpu"}
        if v.lower() not in valid:
            raise ValueError(
                f"Invalid TTS_DEVICE '{v}', must be one of: {', '.join(sorted(valid))}"
            )
        return v.lower()

    TTS_SAMPLE_RATE: Literal[8000, 16000, 22050, 24000, 48000] = 48000
    """Audio sample rate in Hz for TTS output."""

    TTS_MAX_TEXT_LENGTH: int = Field(1000, ge=1, le=10000)
    """Maximum length of text input for TTS synthesis."""

    TTS_ALLOWED_ORIGINS: str = "*"
    """Allowed CORS origins, or '*' for all origins."""

    TTS_SHUTDOWN_TIMEOUT: int = Field(10, ge=1)
    """Timeout in seconds for graceful shutdown."""

    TTS_CONFIG_PATH: str = "silero-to-mary-config.yml"
    """Path to voice/locale mapping config file."""

    TTS_MAX_CONCURRENT_PER_MODEL: int = Field(2, ge=1, le=10)
    """Maximum concurrent TTS requests per model."""

    @field_validator("TTS_CONFIG_PATH")
    @classmethod
    def config_path_must_exist(cls, v: str) -> str:
        if not Path(v).exists():
            raise ValueError(f"Config file not found: {v}")
        return v


settings = Settings()
