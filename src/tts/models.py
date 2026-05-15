from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    language: str
    sample_rates: list[int]


@dataclass(frozen=True)
class VoiceConfig:
    speaker: str
    model: str
    gender: str


@dataclass(frozen=True)
class Locale:
    voices: dict[str, "VoiceConfig"]


@dataclass(frozen=True)
class TTSConfigModel:
    models: dict[str, Model]
    locales: dict[str, Locale]


@dataclass(frozen=True)
class TTSConfig:
    device: str
    sample_rate: int
    max_concurrent_per_locale: int
