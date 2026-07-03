from dataclasses import dataclass
from enum import Enum, unique
from typing import Any


@dataclass(frozen=True)
class Model:
    name: str
    language: str
    enabled: bool = True
    warmup: bool = False
    hash_prefix: str | None = None


@dataclass(frozen=True)
class Voice:
    id: str
    name: str
    speaker: str
    model: str
    locale: str


@unique
class TextFormat(Enum):
    TEXT = "text"
    SSML = "ssml"


@unique
class NormalizationType(Enum):
    SIMPLE = "simple"
    LLM = "llm"


@dataclass(frozen=True)
class TTSConfigModel:
    models: list[Model]
    voices: list[Voice]


@dataclass(frozen=True)
class TTSConfig:
    device: str
    sample_rate: int
    max_models: int
    max_concurrent_per_model: int
    max_chunk_chars: int
    models_dir: str
    models_yml_url: str
    models_yml_hash: str | None = None
    normalization_type: NormalizationType | None = None


@dataclass(frozen=True)
class NormalizationOptions:
    voice: Voice
    model: Model
    silero_model: Any


@dataclass(frozen=True)
class OpenAiNormalizationConfig:
    timeout: float
    max_concurrent_chunks_per_request: int
    default_model: str
    default_promt: str


@dataclass(frozen=True)
class TTSResult:
    audio: bytes
    sample_rate: int
    model: str
    bytes_per_sample: int
    channels: int
