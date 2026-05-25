import asyncio
import gc
import io
from collections import OrderedDict
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


@dataclass
class CachedModel:
    """Bundles a loaded model with its sample rate and concurrency control."""

    model: Any
    sample_rate: int
    semaphore: asyncio.Semaphore


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


def _resolve_device(device_str: str) -> torch.device:
    if device_str == "cuda" and not torch.cuda.is_available():
        device_str = "cpu"
    elif device_str == "xpu" and (not hasattr(torch, "xpu") or not torch.xpu.is_available()):
        device_str = "cpu"
    return torch.device(device_str)


def _run_tts_sync(cached_model: CachedModel, text: str, speaker: str):
    with torch.inference_mode():
        audio = cached_model.model.apply_tts(
            text=text, speaker=speaker, sample_rate=cached_model.sample_rate
        )

        # If it's a GPU, we force the computation thread to synchronize
        # so that the tensor is guaranteed to be formed before exiting the method.
        if audio.device.type in ("cuda", "xpu"):
            if audio.device.type == "cuda":
                torch.cuda.synchronize(device=audio.device)
            elif audio.device.type == "xpu":
                torch.xpu.synchronize(device=audio.device)

        return audio


def _tensor_to_wav_bytes(audio: torch.Tensor, sample_rate: int, device: torch.device) -> io.BytesIO:
    try:
        if device.type == "cpu":
            audio_np = audio.detach().squeeze(0).numpy()
            audio_np = np.clip(audio_np, -1.0, 1.0)
        elif device.type in ("cuda", "xpu"):
            # Processing ONLY on GPU is currently not supported (No transfer to CPU)
            # audio is located on device 'xpu/cuda'
            # We transfer it to the CPU and convert it into a numpy array.
            audio_np = audio.detach().squeeze(0).clamp(-1.0, 1.0).cpu().numpy()
        else:
            raise TTSEngineError(f"Unsupported device: {device.type}")
    except TTSEngineError:
        raise
    except Exception as e:
        raise TTSEngineError(f"Failed to convert tensor to WAV from device '{device.type}'.") from e

    pcm_data = (audio_np * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm_data)
    buffer.seek(0)

    return buffer


def _clear_cached_model(cached_model):
    del cached_model.model
    del cached_model.semaphore
    del cached_model


def _clear_torch_cache_on_device(device: torch.device):
    # Clearing the PyTorch allocator cache to free up VRAM/RAM
    if device == "cuda":
        torch.cuda.empty_cache()
    elif device == "xpu":
        torch.xpu.empty_cache()


class SileroTTSEngine:
    """TTS engine wrapping Silero TTS library."""

    def __init__(
        self,
        config: TTSConfig,
        config_model: TTSConfigModel,
        provider: SileroTTSModelProvider,
    ):
        self._config = config
        self._config_model = config_model
        self._locales = tuple(config_model.locales.keys())
        self._voices = self._build_voices()
        # Using OrderedDict instead of regular dict for LRU logic
        self._cached_models: OrderedDict[str, CachedModel] = OrderedDict()
        self._device = _resolve_device(config.device)
        self._provider = provider
        self._lock: asyncio.Lock | None = None

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

        async with self._get_lock():
            if model_name in self._cached_models:
                # The model is in the cache: move it to the end (it is now the most recent)
                self._cached_models.move_to_end(model_name)
                cached = self._cached_models[model_name]
            else:
                # The model is not in the cache: check the limit and download the old one if necessary
                self._evict_oldest_model()

                # Load a new model
                cached = await self._load_model_async(model_name, model_info)
                # _load_model_async will write it to self._cached_models itself,
                # and it will automatically appear at the end as the most recent one.

        speaker = voice_config.speaker

        async with cached.semaphore:
            audio_tensor = await asyncio.to_thread(_run_tts_sync, cached, text, speaker)

        wav_bytes = await asyncio.to_thread(
            _tensor_to_wav_bytes, audio_tensor, cached.sample_rate, self._device
        )

        return TTSResult(audio=wav_bytes, sample_rate=cached.sample_rate, model=model_name)

    async def shutdown(self):
        """Clears the model cache and forces VRAM to be released."""
        async with self._get_lock():
            while self._cached_models:
                _, evicted_model = self._cached_models.popitem()
                _clear_cached_model(evicted_model)
                del evicted_model

            gc.collect()

            _clear_torch_cache_on_device(self._device)

    def _get_lock(self) -> asyncio.Lock:
        # Ensures that the lock is created strictly within the running FastAPI Event Loop
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _evict_oldest_model(self):
        """Internal method for removing the least used model from memory."""
        if len(self._cached_models) >= self._config.max_models:
            # delete the first model (the oldest)
            _, evicted_model = self._cached_models.popitem(last=False)
            _clear_cached_model(evicted_model)
            del evicted_model

            gc.collect()

            _clear_torch_cache_on_device(self._device)

    async def _load_model_async(self, model_name: str, model_info: Model) -> CachedModel:
        language = model_info.language
        if not language:
            raise TTSEngineError(f"Language isn't specified for Silero model: {model_name}")

        # Move blocking disk reading and heavy PyTorch initialization to a separate thread
        def _sync_load():
            local_path, sample_rates = self._provider.get_model(language, model_name)
            try:
                importer = torch.package.PackageImporter(local_path)
                model = importer.load_pickle("tts_models", "model")
                model.to(self._device)
                return model, sample_rates
            except Exception as e:
                raise TTSEngineError(
                    f"Failed to load model '{model_name}' for language '{language}' with path: {local_path}. "
                    f"Try to delete model to force a fresh download."
                ) from e

        model, sample_rates = await asyncio.to_thread(_sync_load)

        sample_rate = _select_sample_rate(self._config.sample_rate, sample_rates)
        semaphore = asyncio.Semaphore(self._config.max_concurrent_per_model)
        cached = CachedModel(model, sample_rate, semaphore)
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
