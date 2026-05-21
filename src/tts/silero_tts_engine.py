import asyncio
import io
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import yaml
from scipy.io import wavfile

from src.tts.exceptions import TTSEngineError
from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, VoiceConfig
from src.tts.provider import SileroTTSModelProvider
from src.tts.result import TTSResult


def _load_config_model(config_path: str) -> TTSConfigModel:
    """Load TTS configuration from YAML file."""
    with open(config_path) as f:
        data = yaml.safe_load(f)

    models = {}
    for name, m in data.get("models", {}).items():
        models[name] = Model(language=m["language"])

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


def _select_sample_rate(config_rate: int, supported_rates: list[int]) -> int:
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


def _tensor_to_wav_bytes(audio: torch.Tensor, sample_rate: int, device: torch.device) -> bytes:
    try:
        if device.type == "cpu":
            audio_np = audio.squeeze().detach().numpy()
            audio_np = np.clip(audio_np, -1.0, 1.0)
        elif device.type in ("cuda", "xpu"):
            # Processing ONLY on GPU is currently not supported (No transfer to CPU)
            # audio is located on device 'xpu/cuda'
            # We transfer it to the CPU and convert it into a numpy array.
            audio_np = audio.squeeze().clamp(-1.0, 1.0).cpu().numpy()
        else:
            raise TTSEngineError(f"Unsupported device: {device.type}")
    except TTSEngineError:
        raise
    except Exception as e:
        raise TTSEngineError(f"Failed to convert tensor to WAV from device '{device.type}'.") from e

    pcm_data = (audio_np * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm_data)
    return buffer.getvalue()


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
    ) -> TTSResult:
        if not self.has_locale(locale):
            raise TTSEngineError(f"Unsupported locale: {locale}")
        if not self.has_voice(locale, voice):
            raise TTSEngineError(f"Invalid voice: {voice}")
        if input_type not in self.get_input_types():
            raise TTSEngineError(f"Invalid input type: {input_type}")

        voice_config = self._config_model.locales[locale].voices[voice]
        model_name = voice_config.model
        model_info = self._config_model.models[model_name]

        cached = self._cached_models.get(model_name) or self._load_model(model_name, model_info)
        speaker = voice_config.speaker

        async with cached.semaphore:
            audio_tensor = await asyncio.to_thread(
                cached.model.apply_tts, text, speaker=speaker, sample_rate=cached.sample_rate
            )

        wav_bytes = _tensor_to_wav_bytes(audio_tensor, cached.sample_rate, self._device)
        return TTSResult(audio=wav_bytes, sample_rate=cached.sample_rate, model=model_name)

    def _resolve_device(self, device_str: str) -> torch.device:
        if device_str == "cuda" and not torch.cuda.is_available():
            device_str = "cpu"
        elif device_str == "xpu" and (not hasattr(torch, "xpu") or not torch.xpu.is_available()):
            device_str = "cpu"
        return torch.device(device_str)

    def _load_model(self, model_name: str, model_info: Model) -> CachedModel:
        language = model_info.language
        if not language:
            raise TTSEngineError(f"Language isn't specified for Silero model: {model_name}")

        local_path, sample_rates = self._provider.get_model(language, model_name)

        try:
            importer = torch.package.PackageImporter(local_path)
            model = importer.load_pickle("tts_models", "model")
        except Exception as e:
            raise TTSEngineError(
                f"Failed to load model '{model_name}' for language '{language}' with path: {local_path}. "
                f"Delete model to force a fresh download."
            ) from e

        try:
            model.to(self._device)
        except Exception as e:
            raise TTSEngineError(f"Failed to move model to device: '{self._device.type}'") from e

        sample_rate = _select_sample_rate(self._config.sample_rate, sample_rates)
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

    def has_locale(self, locale: str) -> bool:
        """Return True if the locale is configured."""
        return locale in self._locales

    def has_voice(self, locale: str, voice_name: str) -> bool:
        """Return True if the voice exists for the given locale."""
        return (
            locale in self._config_model.locales
            and voice_name in self._config_model.locales[locale].voices
        )

    def get_input_types(self) -> tuple[str, ...]:
        """Return supported input types."""
        return ("TEXT", "SSML")

    def get_locales(self) -> tuple[str, ...]:
        """Return available locales."""
        return self._locales

    def get_voices(self) -> tuple[str, ...]:
        """Return available voices in Mary-TTS format."""
        return self._voices


def create_silero_engine(
    config: TTSConfig,
    config_path_or_model: str | TTSConfigModel,
) -> SileroTTSEngine:
    """Create a SileroTTSEngine with a SileroTTSModelProvider."""
    if isinstance(config_path_or_model, str):
        config_model = _load_config_model(config_path_or_model)
    else:
        config_model = config_path_or_model
    provider = SileroTTSModelProvider()
    return SileroTTSEngine(config=config, config_model=config_model, provider=provider)
