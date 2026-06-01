import asyncio
import gc
import io
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from scipy.io import wavfile

from src.tts.config_storage import SileroTTSConfigStorage
from src.tts.exceptions import TTSEngineError
from src.tts.models import Model, TTSConfig
from src.tts.provider import SileroTTSModelProvider
from src.tts.result import TTSResult


@dataclass
class CachedModel:
    """Bundles a loaded model with its sample rate and concurrency control."""

    model: Any
    sample_rate: int
    semaphore: asyncio.Semaphore


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
        storage: SileroTTSConfigStorage,
        provider: SileroTTSModelProvider,
    ):
        self._config = config
        self._storage = storage
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
        if not self._storage.has_locale(locale):
            raise TTSEngineError(f"Unsupported locale: {locale}")
        if not self._storage.has_voice(locale, voice):
            raise TTSEngineError(f"Invalid voice: {voice}")
        if input_type not in self.get_input_types():
            raise TTSEngineError(f"Invalid input type: {input_type}")

        voice_config = self._storage.get_voice_config(locale, voice)
        model_name = voice_config.model
        model_info = self._storage.get_model_info(model_name)

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

    def get_storage(self) -> SileroTTSConfigStorage:
        """Return the config storage."""
        return self._storage

    def get_input_types(self) -> tuple[str, ...]:
        """Return supported input types."""
        return ("TEXT", "SSML")
