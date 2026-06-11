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
    def get_locales(self) -> list[Locale]:
        ...

    @abstractmethod
    def get_voices(self) -> list[VoiceConfig]:
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
        self._locales: dict[str, tuple[Locale, dict[str, VoiceConfig]]] = {}
        for locale in self._config_model.locales:
            self._locales[locale.name] = (locale, {})
        for vc in self._config_model.voices:
            if vc.locale in self._locales:
                self._locales[vc.locale][1][vc.voice_name] = vc

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

        locales_list: list[Locale] = []
        voices_list: list[VoiceConfig] = []
        for locale_name, loc in data.get("locales", {}).items():
            locales_list.append(Locale(name=locale_name))
            for voice_name, v in loc.get("voices", {}).items():
                speaker_raw = v.get("speaker")
                speaker = speaker_raw if speaker_raw and speaker_raw.strip() else voice_name
                voices_list.append(
                    VoiceConfig(
                        voice_name=voice_name,
                        speaker=speaker,
                        model=v["model"],
                        gender=v["gender"],
                        locale=locale_name,
                    )
                )

        logger.debug("Silero-To-Mary configuration loaded.")

        return TTSConfigModel(models=models, locales=locales_list, voices=voices_list)

    @staticmethod
    def _filter_enabled(config: TTSConfigModel) -> TTSConfigModel:
        enabled_models = {name: m for name, m in config.models.items() if m.enabled}
        enabled_model_names = set(enabled_models)

        filtered_voices = [vc for vc in config.voices if vc.model in enabled_model_names]
        locales_with_enabled_voices = {vc.locale for vc in filtered_voices}

        filtered_locales = [
            locale for locale in config.locales if locale.name in locales_with_enabled_voices
        ]

        return TTSConfigModel(
            models=enabled_models, locales=filtered_locales, voices=filtered_voices
        )

    def has_locale(self, locale: str) -> bool:
        return locale in self._locales

    def has_voice(self, locale: str, voice_name: str) -> bool:
        try:
            self.get_voice_config(locale, voice_name)
            return True
        except KeyError:
            return False

    def get_locales(self) -> list[Locale]:
        return [locale for locale, _ in self._locales.values()]

    def get_voices(self) -> list[VoiceConfig]:
        result: list[VoiceConfig] = []
        for _, voices in self._locales.values():
            result.extend(voices.values())
        return result

    def get_voice_config(self, locale: str, voice_name: str) -> VoiceConfig:
        _, voices = self._locales[locale]
        return voices[voice_name]

    def get_model_info(self, model_name: str) -> Model:
        return self._config_model.models[model_name]

    def get_models(self) -> dict[str, Model]:
        return dict(self._config_model.models)
