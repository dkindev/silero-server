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
    max_concurrent_per_model: int


def select_sample_rate(config_rate: int, supported_rates: list[int]) -> int:
    if not supported_rates:
        return config_rate
    if supported_rates is None:
        return config_rate

    unique_rates = sorted(set(supported_rates))

    if len(unique_rates) == 1:
        return unique_rates[0]

    max_rate = unique_rates[-1]
    if config_rate > max_rate:
        return max_rate
    min_rate = unique_rates[0]
    if config_rate < min_rate:
        return min_rate

    if config_rate in unique_rates:
        return config_rate

    candidates = [r for r in unique_rates if r < config_rate]
    if candidates:
        return candidates[-1]

    return max_rate
