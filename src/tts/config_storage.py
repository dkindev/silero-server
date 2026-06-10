from abc import ABC, abstractmethod

import yaml
from loguru import logger

from src.tts.models import Locale, Model, TTSConfigModel, VoiceConfig


class SileroTTSConfigStorage(ABC):
    @abstractmethod
    def has_locale(self, locale: str) -> bool:
        ...

    @abstractmethod
    def has_voice(self, locale: str, voice_name: str) -> bool:
        ...

    @abstractmethod
    def get_locales(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def get_voices(self) -> dict[str, list[VoiceConfig]]:
        ...

    @abstractmethod
    def get_voice_config(self, locale: str, voice_name: str) -> VoiceConfig:
        ...

    @abstractmethod
    def get_model_info(self, model_name: str) -> Model:
        ...

    @abstractmethod
    def get_models(self) -> dict[str, Model]:
        ...


class SileroTTSYamlConfigStorage(SileroTTSConfigStorage):
    def __init__(self, config_path_or_model: str | TTSConfigModel):
        if isinstance(config_path_or_model, str):
            self._config_model: TTSConfigModel = self._load_config_model(config_path_or_model)
        else:
            self._config_model = config_path_or_model
        self._config_model = self._filter_enabled(self._config_model)
        self._locales = tuple(self._config_model.locales.keys())
        self._voices = self._build_voices()

    def _load_config_model(self, config_path: str) -> TTSConfigModel:
        logger.debug("Loading Silero-To-Mary configuration from '{path}'.", path=config_path)

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        models = {}
        for name, m in data.get("models", {}).items():
            models[name] = Model(
                language=m["language"],
                enabled=m.get("enabled", True),
                warmup=m.get("warmup", False),
            )

        locales = {}
        for name, loc in data.get("locales", {}).items():
            voices = {}
            for voice_name, v in loc.get("voices", {}).items():
                speaker_raw = v.get("speaker")
                speaker = speaker_raw if speaker_raw and speaker_raw.strip() else voice_name
                voices[voice_name] = VoiceConfig(
                    voice_name=voice_name,
                    speaker=speaker,
                    model=v["model"],
                    gender=v["gender"],
                )
            locales[name] = Locale(voices=voices)

        logger.debug("Silero-To-Mary configuration loaded.")

        return TTSConfigModel(models=models, locales=locales)

    def _build_voices(self) -> dict[str, list[VoiceConfig]]:
        result: dict[str, list[VoiceConfig]] = {}
        for locale, locale_data in self._config_model.locales.items():
            seen: set[str] = set()
            voices: list[VoiceConfig] = []
            for voice_name, vc in locale_data.voices.items():
                if voice_name not in seen:
                    seen.add(voice_name)
                    voices.append(vc)
            if voices:
                result[locale] = voices
        return result

    @staticmethod
    def _filter_enabled(config: TTSConfigModel) -> TTSConfigModel:
        enabled_models = {name: m for name, m in config.models.items() if m.enabled}
        enabled_model_names = set(enabled_models)

        filtered_locales = {}
        for locale_name, locale_data in config.locales.items():
            filtered_voices = {
                vn: vc for vn, vc in locale_data.voices.items() if vc.model in enabled_model_names
            }
            if filtered_voices or not locale_data.voices:
                filtered_locales[locale_name] = Locale(voices=filtered_voices)

        return TTSConfigModel(models=enabled_models, locales=filtered_locales)

    def has_locale(self, locale: str) -> bool:
        return locale in self._locales

    def has_voice(self, locale: str, voice_name: str) -> bool:
        return (
            locale in self._config_model.locales
            and voice_name in self._config_model.locales[locale].voices
        )

    def get_locales(self) -> tuple[str, ...]:
        return self._locales

    def get_voices(self) -> dict[str, list[VoiceConfig]]:
        return self._voices

    def get_voice_config(self, locale: str, voice_name: str) -> VoiceConfig:
        return self._config_model.locales[locale].voices[voice_name]

    def get_model_info(self, model_name: str) -> Model:
        return self._config_model.models[model_name]

    def get_models(self) -> dict[str, Model]:
        return dict(self._config_model.models)
