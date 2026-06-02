from abc import ABC, abstractmethod

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
    def get_voices(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def get_voice_config(self, locale: str, voice_name: str) -> VoiceConfig:
        ...

    @abstractmethod
    def get_model_info(self, model_name: str) -> Model:
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
        import yaml

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        models = {}
        for name, m in data.get("models", {}).items():
            models[name] = Model(language=m["language"], enabled=m.get("enabled", True))

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

    def _build_voices(self) -> tuple[str, ...]:
        voices = []
        for locale, locale_data in self._config_model.locales.items():
            for voice_name, voice_config in locale_data.voices.items():
                voices.append(f"{voice_name} {locale} {voice_config.gender}")
        return tuple(voices)

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

    def get_voices(self) -> tuple[str, ...]:
        return self._voices

    def get_voice_config(self, locale: str, voice_name: str) -> VoiceConfig:
        return self._config_model.locales[locale].voices[voice_name]

    def get_model_info(self, model_name: str) -> Model:
        return self._config_model.models[model_name]
