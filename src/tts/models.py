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
