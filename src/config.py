import argparse
from functools import lru_cache
from typing import Any, Literal, get_args, get_origin

from pydantic import AliasChoices, BaseModel, Field, HttpUrl, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class TorchSettings(BaseModel):
    device: str = Field(
        default="cpu",
        validation_alias=AliasChoices("device", "TTS_TORCH_DEVICE"),
        description="Device to run TTS model on: 'cpu', 'cuda', etc. Falls back to 'cpu' at runtime if unavailable.",
    )
    """Device to run TTS model on: 'cpu', 'cuda', etc. Falls back to 'cpu' at runtime if unavailable."""

    num_threads: int = Field(
        default=4,
        ge=1,
        validation_alias=AliasChoices("num_threads", "TTS_TORCH_NUM_THREADS"),
        description="Number of PyTorch intra-op threads (torch.set_num_threads).",
    )
    """Number of PyTorch intra-op threads (torch.set_num_threads)."""

    num_interop_threads: int = Field(
        default=1,
        ge=1,
        validation_alias=AliasChoices("num_interop_threads", "TTS_TORCH_NUM_INTEROP_THREADS"),
        description="Number of PyTorch inter-op threads (torch.set_num_interop_threads).",
    )
    """Number of PyTorch inter-op threads (torch.set_num_interop_threads)."""

    flush_denormal: bool = Field(
        default=True,
        validation_alias=AliasChoices("flush_denormal", "TTS_TORCH_FLUSH_DENORMAL"),
        description="Flush denormal floats for performance (torch.set_flush_denormal).",
    )
    """Flush denormal floats for performance (torch.set_flush_denormal)."""


class TtsSettings(BaseModel):
    sample_rate: Literal[8000, 16000, 24000, 48000] = Field(
        default=48000,
        validation_alias=AliasChoices("sample_rate", "TTS_SAMPLE_RATE"),
        description="Audio sample rate in Hz for TTS output.",
    )
    """Audio sample rate in Hz for TTS output."""

    @field_validator("sample_rate", mode="before")
    @classmethod
    def coerce_sample_rate(cls, v: object) -> object:
        if isinstance(v, str):
            return int(v)
        return v

    max_models: int = Field(
        default=2,
        ge=1,
        validation_alias=AliasChoices("max_models", "TTS_MAX_MODELS"),
        description="Maximum number of models to cache in memory. Oldest evicted when limit reached.",
    )
    """Maximum number of models to cache in memory. Oldest evicted when limit reached."""

    max_concurrent_per_model: int = Field(
        default=2,
        ge=1,
        validation_alias=AliasChoices("max_concurrent_per_model", "TTS_MAX_CONCURRENT_PER_MODEL"),
        description="Maximum concurrent TTS requests per model.",
    )
    """Maximum concurrent TTS requests per model."""

    max_chunk_chars: int = Field(
        default=140,
        ge=1,
        validation_alias=AliasChoices("max_chunk_chars", "TTS_MAX_CHUNK_CHARS"),
        description="Maximum character count per text chunk for TTS processing.",
    )
    """Maximum character count per text chunk for TTS processing."""

    models_config_path: str = Field(
        default="data/models.yml",
        validation_alias=AliasChoices("models_config_path", "TTS_MODELS_CONFIG_PATH"),
    )
    """Local path to the models configuration file models.yml"""

    models_dir: str = Field(
        default="models/silero",
        validation_alias=AliasChoices("models_dir", "TTS_MODELS_DIR"),
        description="Directory for downloaded Silero .pt model files.",
    )
    """Directory for downloaded Silero .pt model files."""

    models_yml_url: HttpUrl = Field(
        default="https://raw.githubusercontent.com/snakers4/silero-models/refs/heads/master/models.yml",
        validation_alias=AliasChoices("models_yml_url", "TTS_MODELS_YML_URL"),
        description="URL to the Silero models.yml registry file.",
    )
    """URL to the Silero models.yml registry file."""

    models_yml_hash: str = Field(
        default="",
        validation_alias=AliasChoices("models_yml_hash", "TTS_MODELS_YML_HASH"),
        description="SHA-256 hash of the Silero models.yml file for integrity verification. Set empty to skip validation.",
    )
    """SHA-256 hash of the Silero models.yml file for integrity verification. Set empty to skip validation."""

    @field_validator("models_yml_hash")
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


class Settings(BaseSettings):
    env_type: Literal["development", "production"] = Field(
        default="development",
        description="Application environment type. Controls error detail level and other environment-specific behavior.",
    )
    """Application environment type. Controls error detail level and other environment-specific behavior."""

    uri: str = Field(
        default="tcp://127.0.0.1:10200",
        description="URI for the Wyoming server.",
    )
    """URI for the Wyoming server."""

    zeroconf: str = Field(
        default="silero-tts",
        description="Zeroconf discovery name. Empty string means disabled. Set to a name (e.g. 'silero-tts') to enable.",
    )
    """Zeroconf discovery name. Empty string means disabled. Set to a name (e.g. 'silero-tts') to enable."""

    torch: TorchSettings = Field(default_factory=TorchSettings)
    tts: TtsSettings = Field(default_factory=TtsSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        yaml_file="config.yml",
        yaml_file_encoding="utf-8",
        env_prefix="TTS_",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # CLI > ENV OS > config.yaml > Defaults
        return (
            CliArgsSource(settings_cls),
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            init_settings,
        )


class CliArgsSource(PydanticBaseSettingsSource):
    def get_field_value(self, field, field_name):
        return None

    def __call__(self) -> dict[str, Any]:
        return self._parse_cli_args()

    def _add_fields_to_parser(
        self, parser: argparse.ArgumentParser, model_cls: type[BaseModel], prefix: str = ""
    ):
        for field_name, field_info in model_cls.model_fields.items():
            cli_name = f"{prefix}{field_name}"
            help_text = field_info.description or ""
            annotation = field_info.annotation

            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                self._add_fields_to_parser(parser, annotation, prefix=f"{cli_name}_")
                continue

            kwargs: dict[str, Any] = {"default": None, "help": help_text}

            if get_origin(annotation) is Literal:
                allowed_values = get_args(annotation)
                kwargs["choices"] = allowed_values
                kwargs["type"] = type(allowed_values[0]) if allowed_values else str
            elif annotation is bool:
                kwargs["action"] = "store_true"
            else:
                kwargs["type"] = str
                if annotation is int:
                    kwargs["metavar"] = "INT"
                else:
                    kwargs["metavar"] = "STR"

            parser.add_argument(f"--{cli_name}", **kwargs)

    def _parse_cli_args(self) -> dict[str, Any]:
        parser = argparse.ArgumentParser(
            description="A simple, robust, and performant Wyoming protocol TTS server that wraps the Silero TTS engine.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        self._add_fields_to_parser(parser, Settings)

        args, _ = parser.parse_known_args()
        raw_args = {k: v for k, v in vars(args).items() if v is not None}

        structured_data: dict[str, Any] = {}
        for key, value in raw_args.items():
            if key.startswith("torch_"):
                if "torch" not in structured_data:
                    structured_data["torch"] = {}
                structured_data["torch"][key[6:]] = value
            elif key.startswith("tts_"):
                if "tts" not in structured_data:
                    structured_data["tts"] = {}
                structured_data["tts"][key[4:]] = value
            else:
                structured_data[key] = value

        return structured_data


@lru_cache
def get_settings() -> Settings:
    return Settings()
