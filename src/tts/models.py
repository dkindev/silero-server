from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    language: str
    enabled: bool = True
    warmup: bool = False


@dataclass(frozen=True)
class VoiceConfig:
    voice_name: str
    speaker: str
    model: str
    gender: str
    locale: str


@dataclass(frozen=True)
class Locale:
    name: str


@dataclass(frozen=True)
class TTSConfigModel:
    models: dict[str, Model]
    locales: list[Locale]
    voices: list[VoiceConfig]


@dataclass(frozen=True)
class TTSConfig:
    device: str
    sample_rate: int
    max_models: int
    max_concurrent_per_model: int
    max_chunk_chars: int
    models_dir: str
