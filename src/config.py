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

from src import __metadata__
from src.tts.models import NormalizationType


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
        validation_alias=AliasChoices("num_threads", "TTS_TORCH_NUM_THREADS", "OMP_NUM_THREADS"),
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


class NormalizationPromt(BaseModel):
    text: str = Field(default="", description="System prompt for normalization")
    """System prompt for normalization"""

    model: str = Field(
        default="",
        description="System LLM model name for normalization",
    )
    """System LLM model name for normalization"""


class BaseNormalizationSettings(BaseModel):
    type: NormalizationType = Field(
        default=NormalizationType.SIMPLE, description="Normalizer type (simple, llm)"
    )
    """Normalizer type (simple, llm)"""

    promts: dict[str, NormalizationPromt] | None = Field(
        default_factory=dict, description="A dictionary of prompts indexed by locale"
    )
    """A dictionary of prompts indexed by locale"""

    # model_config = {"use_enum_values": True}


class TextNormalizationSettings(BaseNormalizationSettings):
    enabled: bool = Field(
        default=True,
        validation_alias=AliasChoices("enabled", "TTS_NORM_TEXT_ENABLED"),
        description="Enable plain text normalization",
    )
    """Enable plain text normalization"""


class SsmlNormalizationSettings(BaseNormalizationSettings):
    enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("enabled", "TTS_NORM_SSML_ENABLED"),
        description="Enable SSML markup normalization",
    )
    """Enable SSML markup normalization"""


class NormalizationSettings(BaseModel):
    timeout: float = Field(
        default=5,
        ge=1,
        validation_alias=AliasChoices("timeout", "TTS_NORM_TIMEOUT"),
        description="Timeout for input text normalization",
    )
    """Timeout for input text normalization"""

    max_concurrent_chunks_per_request: int = Field(
        default=2,
        ge=1,
        validation_alias=AliasChoices(
            "max_concurrent_chunks_per_request", "TTS_NORM_MAX_CONCURRENT_PER_REQUEST"
        ),
        description="Maximum concurrent chunks per request for normalization.",
    )
    """Maximum concurrent chunks per request for normalization."""

    text: TextNormalizationSettings = Field(default_factory=TextNormalizationSettings)
    ssml: SsmlNormalizationSettings = Field(default_factory=SsmlNormalizationSettings)


class OpenAiSettings(BaseModel):
    base_url: str = Field(
        default="",
        validation_alias=AliasChoices("base_url", "TTS_OPENAI_BASE_URL", "OPENAI_BASE_URL"),
        description="Base URL for OpenAI-compatible API",
    )
    """Base URL for OpenAI-compatible API"""

    api_key: str = Field(
        default="",
        validation_alias=AliasChoices("api_key", "TTS_OPENAI_API_KEY", "OPENAI_API_KEY"),
        description="API key for OpenAI-compatible API",
    )
    """API key for OpenAI-compatible API"""


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
        ge=10,
        validation_alias=AliasChoices("max_chunk_chars", "TTS_MAX_CHUNK_CHARS"),
        description="Maximum character count per text chunk for TTS processing.",
    )
    """Maximum character count per text chunk for TTS processing."""

    data_yml_path: str = Field(
        default="data/data.yml",
        validation_alias=AliasChoices("data_yml_path", "TTS_DATA_YML_PATH"),
    )
    """Local path to the voice/model mapping configuration file data.yml"""

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

    normalization: NormalizationSettings = Field(default_factory=NormalizationSettings)

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

    streaming: bool = Field(
        default=True,
        description="Enable audio streaming.",
    )
    """Enable audio streaming."""

    torch: TorchSettings = Field(default_factory=TorchSettings)
    open_ai: OpenAiSettings = Field(default_factory=OpenAiSettings)
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
            if field_name == "normalization":
                continue

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
                kwargs["action"] = argparse.BooleanOptionalAction
            else:
                kwargs["type"] = str
                if annotation is int:
                    kwargs["metavar"] = "INT"
                else:
                    kwargs["metavar"] = "STR"

            parser.add_argument(f"--{cli_name}", **kwargs)

    def _parse_cli_args(self) -> dict[str, Any]:
        parser = argparse.ArgumentParser(
            description=__metadata__["summary"],
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
