import asyncio
from dataclasses import dataclass
from typing import Any

import torch

from src.tts.exceptions import (
    InvalidInputTypeError,
    InvalidLocaleError,
    InvalidOutputTypeError,
    InvalidVoiceError,
    TTSProcessingError,
)
from src.tts.models import Model, TTSConfig, TTSConfigModel, select_sample_rate
from src.tts.provider import SileroTTSModelProvider
from src.tts.result import TTSResult


@dataclass
class CachedModel:
    """Bundles a loaded model with its sample rate and concurrency control."""

    model: Any
    sample_rate: int
    semaphore: asyncio.Semaphore


class SileroTTSEngine:
    """TTS engine wrapping Silero TTS library."""

    def __init__(
        self,
        config: TTSConfig,
        config_model: TTSConfigModel,
        provider: "SileroTTSModelProvider",
    ):
        self._config = config
        self._config_model = config_model
        self._locales = tuple(config_model.locales.keys())
        self._voices = self._build_voices()
        self._cached_models: dict[str, CachedModel] = {}
        self._device = self._resolve_device(config.device)
        self._provider = provider

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

        cached = self._cached_models.get(model_name) or self._load_model(model_name, model_info)
        speaker = voice_config.speaker

        async with cached.semaphore:
            audio = await asyncio.to_thread(
                cached.model.apply_tts, text, speaker, cached.sample_rate
            )

        return TTSResult(audio=audio, sample_rate=cached.sample_rate, model=model_name)

    def _resolve_device(self, device_str: str) -> torch.device:
        if device_str == "cuda" and not torch.cuda.is_available():
            device_str = "cpu"
        elif device_str == "xpu" and (not hasattr(torch, "xpu") or not torch.xpu.is_available()):
            device_str = "cpu"
        return torch.device(device_str)

    def _load_model(self, model_name: str, model_info: Model) -> CachedModel:
        language = model_info.language
        if not language:
            raise TTSProcessingError(f"Language isn't specified for Silero model: {model_name}")

        local_path = self._provider.get_model_path(language, model_name)

        try:
            importer = torch.package.PackageImporter(local_path)
            model = importer.load_pickle("tts_models", "model")
        except Exception as e:
            raise TTSProcessingError(
                f"Failed to load model '{model_name}' for language '{language}' with path: {local_path}. "
                f"Delete model to force a fresh download."
            ) from e

        try:
            model.to(self._device)
        except Exception as e:
            raise TTSProcessingError(
                f"Failed to move model to device: '{self._device.type}'"
            ) from e

        sample_rate = select_sample_rate(self._config.sample_rate, model_info.sample_rates)
        semaphore = asyncio.Semaphore(self._config.max_concurrent_per_model)

        cached = CachedModel(model=model, sample_rate=sample_rate, semaphore=semaphore)
        self._cached_models[model_name] = cached
        return cached

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


def create_silero_engine(
    config: TTSConfig,
    config_model: TTSConfigModel,
) -> SileroTTSEngine:
    """Create a SileroTTSEngine with a SileroTTSModelProvider."""
    from src.tts.provider import SileroTTSModelProvider

    provider = SileroTTSModelProvider()
    return SileroTTSEngine(config=config, config_model=config_model, provider=provider)
