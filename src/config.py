from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    TTS_TORCH_DEVICE: str = "cpu"
    """Device to run TTS model on: 'cpu', 'cuda', or 'xpu'. Falls back to 'cpu' at runtime if unavailable."""

    TTS_TORCH_NUM_THREADS: int = Field(4, ge=1)
    """Number of PyTorch intra-op threads (torch.set_num_threads)."""

    TTS_TORCH_NUM_INTEROP_THREADS: int = Field(1, ge=1)
    """Number of PyTorch inter-op threads (torch.set_num_interop_threads)."""

    TTS_TORCH_FLUSH_DENORMAL: bool = True
    """Flush denormal floats for performance (torch.set_flush_denormal)."""

    @field_validator("TTS_TORCH_DEVICE")
    @classmethod
    def device_must_be_valid(cls, v: str) -> str:
        valid = {"cpu", "cuda", "xpu"}
        if v.lower() not in valid:
            raise ValueError(
                f"Invalid TTS_TORCH_DEVICE '{v}', must be one of: {', '.join(sorted(valid))}"
            )
        return v.lower()

    TTS_SAMPLE_RATE: Literal[8000, 16000, 22050, 24000, 48000] = 48000
    """Audio sample rate in Hz for TTS output."""

    TTS_MAX_TEXT_LENGTH: int = Field(1000, ge=1, le=10000)
    """Maximum length of text input for TTS synthesis."""

    TTS_ALLOWED_ORIGINS: str = "*"
    """Allowed CORS origins, or '*' for all origins."""

    TTS_CONFIG_PATH: str = "silero-to-mary-config.yml"
    """Path to voice/locale mapping config file."""

    TTS_MAX_MODELS: int = Field(2, ge=1)
    """Maximum number of models to cache in memory. Oldest evicted when limit reached."""

    TTS_MAX_CONCURRENT_PER_MODEL: int = Field(2, ge=1, le=10)
    """Maximum concurrent TTS requests per model."""

    TTS_MAX_CHUNK_CHARS: int = Field(140, ge=1)
    """Maximum character count per text chunk for TTS processing."""

    TTS_MODELS_DIR: str = ".models/silero"
    """Directory for downloaded Silero .pt model files."""

    TTS_MODELS_YML_URL: str = "https://raw.githubusercontent.com/snakers4/silero-models/88959d6c73168cab4f1487f63754c7c7c96b78a8/models.yml"
    """URL to the Silero models.yml registry file."""

    TTS_MODELS_YML_HASH: str = "c981f239ed79b3924f952eb3a4dee3a03221d9867330c2b4054c767df77a86d8"
    """SHA-256 hash of the models.yml file for integrity verification. Set empty to skip validation."""

    TTS_ENV_TYPE: Literal["development", "production"] = "development"
    """Application environment type. Controls error detail level and other environment-specific behavior."""

    @field_validator("TTS_MODELS_YML_HASH")
    @classmethod
    def models_yml_hash_must_be_valid(cls, v: str) -> str:
        if v and not v.strip():
            return ""
        if v:
            import re

            if not re.fullmatch(r"[a-f0-9]{64}", v.lower()):
                raise ValueError(
                    "TTS_MODELS_YML_HASH must be a 64-character hex string or empty to skip validation"
                )
        return v

    @field_validator("TTS_CONFIG_PATH")
    @classmethod
    def config_path_must_exist(cls, v: str) -> str:
        if not Path(v).exists():
            raise ValueError(f"Config file not found: {v}")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
