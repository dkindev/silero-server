import os
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from loguru import logger

from src.tts.models import Model, TTSConfigModel, Voice


class SileroTTSConfigStorage(ABC):
    @abstractmethod
    def get_voices(self) -> list[Voice]:
        ...

    @abstractmethod
    def get_voice(self, voice_id: str) -> Voice | None:
        ...

    @abstractmethod
    def get_model(self, model_name: str) -> Model | None:
        ...

    @abstractmethod
    def get_models(self) -> list[Model]:
        ...


class SileroTTSYamlConfigStorage(SileroTTSConfigStorage):
    def __init__(self, config_path_or_model: str | Path | TTSConfigModel):
        if isinstance(config_path_or_model, str | Path):
            config_model = self._load_config_model(config_path_or_model)
        else:
            config_model = config_path_or_model

        config_model = self._filter_enabled(config_model)

        self._models: dict[str, Model] = {m.name: m for m in config_model.models}
        self._voices_by_id: dict[str, Voice] = {v.id: v for v in config_model.voices}

    def _load_config_model(self, config_path: str | Path) -> TTSConfigModel:
        config_path = config_path.strip()
        if not config_path:
            raise ValueError("Path to the model configuration file is empty or whitespace")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Models configuration file not found at path: '{config_path}'")

        logger.debug("Loading models configuration from '{path}'", path=config_path)

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        models_list: list[Model] = []
        voices_list: list[Voice] = []

        for model_name, model_data in data.get("models", {}).items():
            models_list.append(
                Model(
                    name=model_name,
                    language=model_data["language"],
                    enabled=model_data.get("enabled", True),
                    warmup=model_data.get("warmup", False),
                    hash_prefix=model_data.get("hash_prefix") or None,
                )
            )

            for locale_name, locale_data in model_data.get("locales", {}).items():
                for voice_entry in locale_data.get("voices", []):
                    voice_name = voice_entry["name"]
                    speaker = voice_entry.get("speaker", "").strip() or voice_name
                    voices_list.append(
                        Voice(
                            id=f"{locale_name}-{model_name}-{voice_name}",
                            name=voice_name,
                            speaker=speaker,
                            model=model_name,
                            locale=locale_name,
                        )
                    )

        logger.debug("Configuration loaded.")
        return TTSConfigModel(models=models_list, voices=voices_list)

    @staticmethod
    def _filter_enabled(config: TTSConfigModel) -> TTSConfigModel:
        enabled_models = [m for m in config.models if m.enabled]
        enabled_model_names = {m.name for m in enabled_models}

        filtered_voices = [v for v in config.voices if v.model in enabled_model_names]

        return TTSConfigModel(models=enabled_models, voices=filtered_voices)

    def get_voices(self) -> list[Voice]:
        return list(self._voices_by_id.values())

    def get_voice(self, voice_id: str) -> Voice | None:
        return self._voices_by_id.get(voice_id)

    def get_model(self, model_name: str) -> Model | None:
        return self._models.get(model_name)

    def get_models(self) -> list[Model]:
        return list(self._models.values())
