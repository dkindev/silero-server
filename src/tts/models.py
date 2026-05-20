from dataclasses import dataclass

import yaml


def load_config_model(config_path: str) -> "TTSConfigModel":
    """Load TTS configuration from YAML file."""
    with open(config_path) as f:
        data = yaml.safe_load(f)

    models = {}
    for name, m in data.get("models", {}).items():
        models[name] = Model(
            language=m["language"],
        )

    locales = {}
    for name, loc in data.get("locales", {}).items():
        voices = {}
        for voice_name, v in loc.get("voices", {}).items():
            voices[voice_name] = VoiceConfig(
                speaker=v["speaker"],
                model=v["model"],
                gender=v["gender"],
            )
        locales[name] = Locale(voices=voices)

    return TTSConfigModel(models=models, locales=locales)


@dataclass(frozen=True)
class Model:
    language: str


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
