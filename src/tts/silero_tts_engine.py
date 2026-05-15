import asyncio
from typing import Any

import torch

from src.tts.exceptions import (
    InvalidInputTypeError,
    InvalidLocaleError,
    InvalidOutputTypeError,
    InvalidVoiceError,
)
from src.tts.models import TTSConfig, TTSConfigModel
from src.tts.result import TTSResult


class SileroTTSEngine:
    """TTS engine wrapping Silero TTS library."""

    def __init__(self, config: TTSConfig, config_model: TTSConfigModel):
        self._config = config
        self._config_model = config_model
        self._locales = tuple(config_model.locales.keys())
        self._voices = self._build_voices()
        self._model_semaphores: dict[str, asyncio.Semaphore] = {}
        self._models: dict[str, Any] = {}

    async def process(
        self,
        text: str,
        locale: str,
        voice: str,
        input_type: str,
        output_type: str,
    ) -> TTSResult:
        if locale not in self._locales:
            raise InvalidLocaleError(f"Unsupported locale: {locale}", locale=locale)
        if voice not in self._config_model.locales[locale].voices:
            raise InvalidVoiceError(f"Invalid voice: {voice}", locale=locale, voice=voice)
        if input_type not in ("TEXT", "SSML"):
            raise InvalidInputTypeError(f"Invalid input type: {input_type}")
        if output_type != "AUDIO":
            raise InvalidOutputTypeError(f"Invalid output type: {output_type}")

        voice_config = self._config_model.locales[locale].voices[voice]
        model_name = voice_config.model
        model_info = self._config_model.models[model_name]

        if model_name not in self._models:
            model = torch.hub.load(
                repo_or_dir="snakers4/silero-v4",
                model="silero_tts",
                language=model_info.language,
                speaker=model_name,
            )
            self._models[model_name] = model
            self._model_semaphores[model_name] = asyncio.Semaphore(
                self._config.max_concurrent_per_locale
            )

        model = self._models[model_name]
        speaker = voice_config.speaker

        sample_rate = self._config.sample_rate
        if sample_rate > max(model_info.sample_rates):
            sample_rate = max(model_info.sample_rates)

        semaphore = self._model_semaphores[model_name]

        async with semaphore:
            audio = await asyncio.to_thread(model.apply_tts, text, speaker, sample_rate)

        return TTSResult(audio=audio, sample_rate=sample_rate, model=model_name)

    def _build_voices(self) -> tuple[str, ...]:
        voices = []
        for locale, locale_data in self._config_model.locales.items():
            for voice_name, voice_config in locale_data.voices.items():
                voices.append(f"{voice_name} {locale} {voice_config.gender}")
        return tuple(voices)

    def get_locales(self) -> tuple[str, ...]:
        """Return available locales."""
        return self._locales

    def get_voices(self) -> tuple[str, ...]:
        """Return available voices in Mary-TTS format."""
        return self._voices
