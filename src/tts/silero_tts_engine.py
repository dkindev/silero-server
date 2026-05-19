import asyncio
from typing import Any

import torch

from src.tts.exceptions import (
    InvalidInputTypeError,
    InvalidLocaleError,
    InvalidOutputTypeError,
    InvalidVoiceError,
    TTSProcessingError,
)
from src.tts.models import Model, TTSConfig, TTSConfigModel
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
        self._device = self._resolve_device(config.device)

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

        model = self._models.get(model_name) or self._load_model(model_name, model_info)
        speaker = voice_config.speaker

        sample_rate = self._select_sample_rate(self._config.sample_rate, model_info.sample_rates)

        semaphore = self._model_semaphores[model_name]

        async with semaphore:
            audio = await asyncio.to_thread(model.apply_tts, text, speaker, sample_rate)

        return TTSResult(audio=audio, sample_rate=sample_rate, model=model_name)

    def _resolve_device(self, device_str: str) -> torch.device:
        if device_str == "cuda" and not torch.cuda.is_available():
            device_str = "cpu"
        elif device_str == "xpu" and (not hasattr(torch, "xpu") or not torch.xpu.is_available()):
            device_str = "cpu"
        return torch.device(device_str)

    def _load_model(self, model_name: str, model_info: Model) -> Any:
        if not model_info.language:
            raise TTSProcessingError(f"Language isn't specified for model: {model_name}")

        model = torch.hub.load(
            repo_or_dir="snakers4/silero-v4",
            model="silero_tts",
            language=model_info.language,
            speaker=model_name,
        )

        try:
            model.to(self._device)
        except Exception as e:
            raise TTSProcessingError(
                f"Failed to move model '{model_name}' to device '{self._device}': {e}"
            ) from e

        self._models[model_name] = model
        self._model_semaphores[model_name] = asyncio.Semaphore(
            self._config.max_concurrent_per_model
        )
        return model

    def _build_voices(self) -> tuple[str, ...]:
        voices = []
        for locale, locale_data in self._config_model.locales.items():
            for voice_name, voice_config in locale_data.voices.items():
                voices.append(f"{voice_name} {locale} {voice_config.gender}")
        return tuple(voices)

    def _select_sample_rate(self, config_rate: int, supported_rates: list[int]) -> int:
        if not supported_rates:
            return config_rate
        if supported_rates is None:
            return config_rate
        if len(supported_rates) == 1:
            return supported_rates[0]

        max_rate = supported_rates[-1]
        if config_rate > max_rate:
            return max_rate
        min_rate = supported_rates[0]
        if config_rate < min_rate:
            return min_rate

        if config_rate in supported_rates:
            return config_rate

        candidates = [r for r in supported_rates if r < config_rate]
        if candidates:
            return candidates[-1]

        return max_rate

    def get_locales(self) -> tuple[str, ...]:
        """Return available locales."""
        return self._locales

    def get_voices(self) -> tuple[str, ...]:
        """Return available voices in Mary-TTS format."""
        return self._voices
