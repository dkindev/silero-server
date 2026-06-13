from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from loguru import logger

from src.tts.models import Locale, Model, TTSConfigModel, Voice


class SileroTTSConfigStorage(ABC):
    @abstractmethod
    def has_locale_in_voices(self, locale_name: str) -> bool:
        ...

    @abstractmethod
    def has_voice(self, locale_name: str, voice_name: str) -> bool:
        ...

    @abstractmethod
    def get_locales_in_voices(self) -> list[Locale]:
        ...

    @abstractmethod
    def get_voices(self) -> list[Voice]:
        ...

    @abstractmethod
    def get_voice(self, locale_name: str, voice_name: str) -> Voice:
        ...

    @abstractmethod
    def get_model_info(self, model_name: str) -> Model:
        ...

    @abstractmethod
    def get_models(self) -> dict[str, Model]:
        ...


class SileroTTSYamlConfigStorage(SileroTTSConfigStorage):
    def __init__(self, config_path_or_model: str | Path | TTSConfigModel):
        if isinstance(config_path_or_model, str | Path):
            config_model = self._load_config_model(config_path_or_model)
        else:
            config_model = config_path_or_model

        config_model = self._filter_enabled(config_model)

        self._models: dict[str, Model] = {m.name: m for m in config_model.models}

        self._locales: dict[str, tuple[Locale, dict[str, Voice]]] = {
            locale.name: (locale, {}) for locale in config_model.locales
        }
        for voice in config_model.voices:
            if voice.locale in self._locales:
                self._locales[voice.locale][1][voice.name] = voice

    def _load_config_model(self, config_path: str | Path) -> TTSConfigModel:
        logger.debug("Loading Silero-To-Mary configuration from '{path}'.", path=config_path)

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        models = [
            Model(
                name=name,
                language=m["language"],
                enabled=m.get("enabled", True),
                warmup=m.get("warmup", False),
                hash_prefix=m.get("hash_prefix") or None,
            )
            for name, m in data.get("models", {}).items()
        ]

        locales_list: list[Locale] = []
        voices_list: list[Voice] = []

        for locale_name, loc in data.get("locales", {}).items():
            locales_list.append(Locale(name=locale_name))
            for voice_name, voice_data in loc.get("voices", {}).items():
                speaker = voice_data.get("speaker", "").strip() or voice_name
                voices_list.append(
                    Voice(
                        name=voice_name,
                        speaker=speaker,
                        model=voice_data["model"],
                        gender=voice_data["gender"],
                        locale=locale_name,
                    )
                )

        logger.debug("Silero-To-Mary configuration loaded.")
        return TTSConfigModel(models=models, locales=locales_list, voices=voices_list)

    @staticmethod
    def _filter_enabled(config: TTSConfigModel) -> TTSConfigModel:
        enabled_models = [m for m in config.models if m.enabled]
        enabled_model_names = {m.name for m in enabled_models}

        filtered_voices = [voice for voice in config.voices if voice.model in enabled_model_names]
        locales_with_enabled_voices = {voice.locale for voice in filtered_voices}

        filtered_locales = [
            locale for locale in config.locales if locale.name in locales_with_enabled_voices
        ]

        return TTSConfigModel(
            models=enabled_models, locales=filtered_locales, voices=filtered_voices
        )

    def has_locale_in_voices(self, locale_name: str) -> bool:
        return locale_name in self._locales

    def has_voice(self, locale_name: str, voice_name: str) -> bool:
        return locale_name in self._locales and voice_name in self._locales[locale_name][1]

    def get_locales_in_voices(self) -> list[Locale]:
        return [locale for locale, _ in self._locales.values()]

    def get_voices(self) -> list[Voice]:
        return [voice for _, voices in self._locales.values() for voice in voices.values()]

    def get_voice(self, locale_name: str, voice_name: str) -> Voice:
        return self._locales[locale_name][1][voice_name]

    def get_model_info(self, model_name: str) -> Model:
        return self._models[model_name]

    def get_models(self) -> dict[str, Model]:
        return self._models.copy()
