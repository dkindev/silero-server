import asyncio
import gc
import hashlib
import io
import os
import urllib.request
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import yaml
from loguru import logger
from scipy.io import wavfile

from src.tts.config_storage import SileroTTSConfigStorage
from src.tts.exceptions import TTSEngineError
from src.tts.models import Model, TTSConfig
from src.tts.preprocessing import TextPreprocessor
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


def _run_tts_sync(
    cached_model: CachedModel, text: str, speaker: str, type: str = "TEXT"
) -> torch.Tensor:
    with torch.inference_mode():
        logger.debug(
            "TTS inferencing. Speaker: {speaker}. Sample rate: {sample_rate}. Type: {type}. Text: {text}",
            speaker=speaker,
            sample_rate=cached_model.sample_rate,
            type=type,
            text=text,
        )

        audio = (
            cached_model.model.apply_tts(
                ssml_text=text, speaker=speaker, sample_rate=cached_model.sample_rate
            )
            if type == "SSML"
            else cached_model.model.apply_tts(
                text=text, speaker=speaker, sample_rate=cached_model.sample_rate
            )
        )

        # If it's a GPU, we force the computation thread to synchronize
        # so that the tensor is guaranteed to be formed before exiting the method.
        device_type = audio.device.type
        if device_type == "cuda":
            torch.cuda.synchronize(device=audio.device)
        elif device_type == "xpu":
            torch.xpu.synchronize(device=audio.device)

        logger.debug(
            "TTS has been successfully inferenced on device '{device}'. Tensor shape: [{shape}]",
            device=device_type,
            shape=audio.shape[0],
        )

        return audio


def _chunks_to_wav_bytes(chunks: list[np.ndarray], sample_rate: int) -> io.BytesIO:
    logger.debug("Saving audio chunks to WAV buffer.")

    combined_audio = np.concatenate(chunks)
    pcm_data = (combined_audio * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm_data)
    buffer.seek(0)

    logger.debug("WAV bytes has been successfully saved to the buffer.")

    return buffer


def _clear_cached_model(cached_model):
    del cached_model.model
    del cached_model.semaphore
    del cached_model


def _clear_torch_cache_on_device(device: torch.device):
    # Clearing the PyTorch allocator cache to free up VRAM/RAM
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "xpu":
        torch.xpu.empty_cache()


def _get_models_data(yml_path: str, models_yml_url: str, models_yml_hash: str | None) -> dict:
    def load_yaml() -> dict:
        try:
            with open(yml_path, encoding="utf-8") as f:
                logger.debug("Loading the models configuration file '{path}'.", path=yml_path)
                models_config = yaml.safe_load(f)
                logger.debug("Models configuration loaded.")
                return models_config
        except Exception as e:
            raise TTSEngineError(
                f"Failed to parse the models configuration file: {e}. Delete '{yml_path}' to force a fresh download."
            ) from e

    if os.path.exists(yml_path):
        if models_yml_hash:
            hasher = hashlib.sha256()
            with open(yml_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            local_hash = hasher.hexdigest().lower()

            if local_hash == models_yml_hash:
                return load_yaml()
            else:
                logger.warning(
                    "Models configuration file '{path}' is corrupted or outdated. Redownloading..."
                )
        else:
            logger.debug(
                "Models configuration file hash validation skipped (models_yml_hash is None)."
            )
            return load_yaml()
    else:
        logger.debug(
            "Models configuration file not found at '{path}'.",
            path=yml_path,
        )

    _download_models_yml(yml_path, models_yml_url, models_yml_hash)

    return load_yaml()


def _download_models_yml(file_path: str, models_yml_url: str, models_yml_hash: str | None):
    logger.debug("Attempting to load model configuration from '{url}'.", url=models_yml_url)

    try:
        if not models_yml_hash:
            urllib.request.urlretrieve(models_yml_url, file_path)
            return

        hasher = hashlib.sha256()
        with urllib.request.urlopen(models_yml_url) as response:
            with open(file_path, "wb") as file:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    file.write(chunk)
                    hasher.update(chunk)
    except Exception as e:
        raise TTSEngineError(
            f"Failed to download the models configuration from '{models_yml_url}'."
        ) from e

    downloaded_hash = hasher.hexdigest().lower()
    if downloaded_hash != models_yml_hash:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise TTSEngineError(
            f"Error verifying hash of model configuration file loaded at '{models_yml_url}'."
        )

    logger.debug("Models configuration are saved in the file '{path}'.", path=file_path)


class SileroTTSEngine:
    """TTS engine wrapping Silero TTS library."""

    def __init__(
        self,
        config: TTSConfig,
        storage: SileroTTSConfigStorage,
        text_preprocessor_factory: Callable[[str], TextPreprocessor],
    ):
        self._config = config
        self._storage = storage
        # Using OrderedDict instead of regular dict for LRU logic
        self._cached_models: OrderedDict[str, CachedModel] = OrderedDict()
        self._device = _resolve_device(config.device)
        self._lock: asyncio.Lock | None = None
        self._text_preprocessor_factory = text_preprocessor_factory

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

        text = text.strip()
        if not text:
            raise TTSEngineError("Text is empty or whitespace")

        voice_config = self._storage.get_voice_config(locale, voice)
        model_name = voice_config.model

        logger.info(
            "TTS processing. Text length: {text_length}. Locale: {locale}. Voice: {voice}. Input type: {input_type}. Model: {model_name}.",
            text_length=len(text),
            locale=locale,
            voice=voice,
            input_type=input_type,
            model_name=model_name,
        )

        async with self._get_lock():
            if model_name in self._cached_models:
                logger.debug("Model '{name}' found in cache.", name=model_name)

                # The model is in the cache: move it to the end (it is now the most recent)
                self._cached_models.move_to_end(model_name)
                cached = self._cached_models[model_name]
            else:
                logger.debug("Model '{name}' not found in cache.", name=model_name)

                # The model is not in the cache: check the limit and download the old one if necessary
                self._evict_oldest_model()

                # Load and warm up the model
                cached = await self._warmup_model(model_name)

        text_preprocessor = self._text_preprocessor_factory(locale)
        if not text_preprocessor:
            raise TTSEngineError("Text preprocessor not found for locale: '{locale}'.")

        logger.debug(
            "Text preprocessor '{text_preprocessor}' found for locale '{locale}'.",
            text_preprocessor=text_preprocessor.__class__.__name__,
            locale=locale,
        )

        chunks = (
            text_preprocessor.process_ssml(text, self._config.max_chunk_chars, cached.model.symbols)
            if input_type == "SSML"
            else text_preprocessor.process_text(
                text, self._config.max_chunk_chars, cached.model.symbols
            )
        )
        if not chunks:
            raise TTSEngineError("The text is empty or contains only invalid characters.")

        logger.debug("Chunks count for TTS processing: {chunks_count}", chunks_count=len(chunks))

        speaker = voice_config.speaker

        async def process_chunk(chunk: str):
            async with cached.semaphore:
                tensor = await asyncio.to_thread(_run_tts_sync, cached, chunk, speaker, input_type)

                # Processing ONLY on GPU is currently not supported (No transfer to CPU)
                # audio is located on device 'xpu/cuda'
                # We transfer it to the CPU and convert it into a numpy array.
                try:
                    audio_np = tensor.detach().squeeze().clamp(-1.0, 1.0).cpu().numpy()
                except Exception as e:
                    raise TTSEngineError("Failed to clipping and transfer to 'cpu'.") from e

                return audio_np

        tasks = [process_chunk(chunk) for chunk in chunks]
        audio_chunks = await asyncio.gather(*tasks)
        wav_bytes = await asyncio.to_thread(_chunks_to_wav_bytes, audio_chunks, cached.sample_rate)

        wav_bytes.seek(0, 2)
        buffer_size = wav_bytes.tell()
        wav_bytes.seek(0)

        logger.info(
            "TTS processed. Buffer size: {buffer_size}. Model: {model_name}. Sample rate: {sample_rate}",
            buffer_size=f"{buffer_size / (1024 * 1024):.2f} MB",
            model_name=model_name,
            sample_rate=cached.sample_rate,
        )

        return TTSResult(audio=wav_bytes, sample_rate=cached.sample_rate, model=model_name)

    async def shutdown(self):
        """Clears the model cache and forces VRAM to be released."""
        async with self._get_lock():
            logger.debug(
                "Cleaning engine resources. Models count: {count}.",
                count=len(self._cached_models),
            )

            while self._cached_models:
                _, evicted_model = self._cached_models.popitem()
                _clear_cached_model(evicted_model)
                del evicted_model

            gc.collect()
            _clear_torch_cache_on_device(self._device)

            logger.debug("Engine resources have been cleared.")

    def _get_lock(self) -> asyncio.Lock:
        # Ensures that the lock is created strictly within the running FastAPI Event Loop
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _evict_oldest_model(self):
        """Internal method for removing the least used model from memory."""
        if len(self._cached_models) >= self._config.max_models:
            # delete the first model (the oldest)
            model_name, evicted_model = self._cached_models.popitem(last=False)

            logger.debug("Removing model '{model}' from cache.", model=model_name)

            _clear_cached_model(evicted_model)
            del evicted_model
            gc.collect()
            _clear_torch_cache_on_device(self._device)

            logger.debug("Model '{model}' was removed from cache.", model=model_name)

    def _resolve_model(
        self, language: str, model_name: str
    ) -> tuple[str, list[int], str, dict[str, str]]:
        """Return the local path, sample rates, example text and speaker examples.

        Downloads the Silero models.yml file and the model itself if they are not available locally.
        Raises TTSEngineError on failure.
        """
        models_dir = self._config.models_dir

        lang_dir = os.path.join(models_dir, language)
        os.makedirs(lang_dir, exist_ok=True)

        logger.debug(
            "Trying to resolve model '{model}' with language '{language}'.",
            model=model_name,
            language=language,
        )

        yml_path = os.path.join(models_dir, "models.yml")
        registry = _get_models_data(
            yml_path, self._config.models_yml_url, self._config.models_yml_hash
        )

        tts_models = registry.get("tts_models", {})
        lang_models = tts_models.get(language, {})
        model_entry = lang_models.get(model_name, {})
        latest = model_entry.get("latest", {})
        sample_rates = latest.get("sample_rate", [])
        example_text = latest.get("example", "")
        raw_speakers = latest.get("speakers", {})
        speakers = {name: s.get("example", "") for name, s in raw_speakers.items()}

        model_path = os.path.join(lang_dir, f"{model_name}.pt")
        if os.path.isfile(model_path):
            logger.debug("Model '{model}' found in '{path}'.", model=model_name, path=model_path)
            return model_path, sample_rates, example_text, speakers

        package_url = latest.get("package")
        if not package_url:
            raise TTSEngineError(
                f"Model '{model_name}' for language '{language}' not found in configuration file. "
                f"Delete '{yml_path}' to force a fresh download."
            )

        logger.debug(
            "Model '{model}' not found. Attempting to load from '{url}'.",
            model=model_name,
            url=package_url,
        )

        try:
            torch.hub.download_url_to_file(package_url, model_path)
        except Exception as e:
            if os.path.isfile(model_path):
                os.remove(model_path)
            raise TTSEngineError(
                f"Failed to download model '{model_name}' for language '{language}'."
            ) from e

        logger.debug(
            "Model '{model}' is saved in the file '{path}'.", model=model_name, path=model_path
        )

        return model_path, sample_rates, example_text, speakers

    async def _load_model_async(
        self, model_name: str, model_info: Model
    ) -> tuple[CachedModel, str, dict[str, str]]:
        """Loads the model into the cache and returns the cached model, sample text, and speaker samples."""

        language = model_info.language
        if not language:
            raise TTSEngineError(f"Language isn't specified for Silero model: {model_name}")

        # Move blocking disk reading and heavy PyTorch initialization to a separate thread
        def _sync_load():
            local_path, sample_rates, example_text, speakers = self._resolve_model(
                language, model_name
            )
            try:
                logger.debug(
                    "Loading model '{model}' to '{device}'.",
                    model=model_name,
                    device=self._device.type,
                )

                importer = torch.package.PackageImporter(local_path)
                model = importer.load_pickle("tts_models", "model", map_location=self._device)
                # Ensure the model modules are shifted as well
                model.to(self._device)

                logger.debug(
                    "Model '{model}' loaded to '{device}'.",
                    model=model_name,
                    device=self._device.type,
                )

                return model, sample_rates, example_text, speakers
            except Exception as e:
                raise TTSEngineError(
                    f"Failed to load model '{model_name}' for language '{language}' with path: {local_path}. "
                    f"Try to delete model to force a fresh download."
                ) from e

        model, sample_rates, example_text, speakers = await asyncio.to_thread(_sync_load)

        sample_rate = _select_sample_rate(self._config.sample_rate, sample_rates)
        semaphore = asyncio.Semaphore(self._config.max_concurrent_per_model)
        cached = CachedModel(model, sample_rate, semaphore)
        self._cached_models[model_name] = cached

        logger.debug(
            "Model '{model}' was cached. Sample rate: '{sample_rate}'.",
            model=model_name,
            sample_rate=sample_rate,
        )

        return cached, example_text, speakers

    async def warmup(self):
        """Warm up the models."""
        if self._cached_models:
            return

        async with self._get_lock():
            if self._cached_models:
                return

            models = self._storage.get_models()
            to_warm = [name for name, m in models.items() if m.warmup][: self._config.max_models]

            logger.debug("Models to warm up: {count}.", count=len(to_warm))

            for name in to_warm:
                await self._warmup_model(name)

    async def _warmup_model(self, name: str) -> CachedModel:
        model_info = self._storage.get_model_info(name)
        cached, example_text, speakers = await self._load_model_async(name, model_info)

        if speakers:
            speaker = next(iter(speakers))
            text = speakers[speaker]
        else:
            speaker = cached.model.speakers[0]
            text = example_text

        logger.debug(
            "Model '{model}' is warming up. Speaker: '{speaker}' Text: '{text}'",
            model=name,
            speaker=speaker,
            text=text,
        )

        try:
            await asyncio.to_thread(_run_tts_sync, cached, text, speaker)
            logger.debug("Model '{model}' has been warmed up.", model=name)
        except Exception:
            logger.exception("Failed to warm up the model '{model}'.", model=name)

        return cached

    def get_storage(self) -> SileroTTSConfigStorage:
        """Return the config storage."""
        return self._storage

    def get_input_types(self) -> tuple[str, ...]:
        """Return supported input types."""
        return ("TEXT", "SSML")
