import io
from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    name: str
    language: str
    enabled: bool = True
    warmup: bool = False
    hash_prefix: str | None = None


@dataclass(frozen=True)
class Voice:
    name: str
    speaker: str
    model: str
    gender: str
    locale: str


@dataclass(frozen=True)
class Locale:
    name: str


@dataclass(frozen=True)
class TTSConfigModel:
    models: list[Model]
    locales: list[Locale]
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


@dataclass(frozen=True)
class TTSResult:
    audio: io.BytesIO
    sample_rate: int
    model: str
