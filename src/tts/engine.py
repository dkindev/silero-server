import asyncio
import gc
import hashlib
import os
import urllib.request
from collections import OrderedDict
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import yaml
from loguru import logger

from src.tts.config_storage import SileroTTSConfigStorage
from src.tts.exceptions import TTSEngineError
from src.tts.models import Model, NormalizationOptions, TextFormat, TTSConfig, TTSResult, Voice
from src.tts.preprocessing import TextNormalizerFactory, TextSentenizerFactory

BYTES_PER_SAMPLE = 2
CHANNELS = 1


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
    cached_model: CachedModel, text: str, speaker: str, text_format: TextFormat = TextFormat.TEXT
) -> torch.Tensor:
    with torch.inference_mode():
        logger.debug(
            "Synthesizing TTS. Speaker: {speaker}. Sample rate: {sample_rate}. Type: {type}. Text: {text}",
            speaker=speaker,
            sample_rate=cached_model.sample_rate,
            type=text_format.value,
            text=text,
        )

        audio = (
            cached_model.model.apply_tts(
                ssml_text=text, speaker=speaker, sample_rate=cached_model.sample_rate
            )
            if text_format == TextFormat.SSML
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
            "TTS synthesized on device '{device}'. Tensor shape: [{shape}]",
            device=device_type,
            shape=audio.shape[0],
        )

        return audio


async def _process_chunk(
    chunk: str, cached_model: CachedModel, voice: Voice, text_format: TextFormat
) -> TTSResult:
    async with cached_model.semaphore:
        tensor = await asyncio.to_thread(
            _run_tts_sync, cached_model, chunk, voice.speaker, text_format
        )

        try:
            audio_np = tensor.detach().squeeze().clamp(-1.0, 1.0).cpu().numpy()
        except Exception as e:
            raise TTSEngineError("Failed to clipping and transfer to 'cpu'") from e

        return TTSResult(
            audio=(audio_np * 32767).astype(np.int16).tobytes(),
            sample_rate=cached_model.sample_rate,
            model=voice.model,
            bytes_per_sample=BYTES_PER_SAMPLE,
            channels=CHANNELS,
        )


def _clear_cached_model(cached_model: CachedModel):
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
                logger.debug("Loading the models configuration file '{path}'", path=yml_path)
                models_config = yaml.safe_load(f)
                logger.debug("Models configuration loaded")
                return models_config
        except Exception as e:
            raise TTSEngineError(
                f"Failed to parse the models configuration file: {e}. Delete '{yml_path}' to force a fresh download"
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
                "Models configuration file hash validation skipped (models_yml_hash is None)"
            )
            return load_yaml()
    else:
        logger.debug(
            "Models configuration file not found at '{path}'",
            path=yml_path,
        )

    logger.debug("Attempting to load model configuration from '{url}'", url=models_yml_url)
    _download_models_yml(yml_path, models_yml_url, models_yml_hash)
    logger.debug("Models configuration are saved in the file '{path}'", path=yml_path)

    return load_yaml()


def _download_models_yml(file_path: str, models_yml_url: str, models_yml_hash: str | None):
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
            f"Failed to download the models configuration from '{models_yml_url}'"
        ) from e

    downloaded_hash = hasher.hexdigest().lower()
    if downloaded_hash != models_yml_hash:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise TTSEngineError(
            f"Error verifying hash of model configuration file loaded at '{models_yml_url}'"
        )


class SileroTTSEngine:
    """TTS engine wrapping Silero TTS library."""

    def __init__(
        self,
        config: TTSConfig,
        storage: SileroTTSConfigStorage,
        text_sentenizer_factory: TextSentenizerFactory,
        text_normalizer_factory: TextNormalizerFactory,
    ):
        self._config = config
        self._storage = storage
        # Using OrderedDict instead of regular dict for LRU logic
        self._cached_models: OrderedDict[str, CachedModel] = OrderedDict()
        self._device = _resolve_device(config.device)
        self._lock: asyncio.Lock | None = None
        self._text_sentenizer_factory = text_sentenizer_factory
        self._text_normalizer_factory = text_normalizer_factory

    async def synthesize_pcm_chunks(
        self,
        text: str,
        voice_id: str,
        text_format: TextFormat,
    ) -> AsyncIterator[TTSResult]:
        if text_format not in self.get_supported_text_formats():
            raise TTSEngineError(f"Invalid text format: {text_format}")

        text = text.strip()
        if not text:
            raise TTSEngineError("Text is empty or whitespace")

        voice = self._storage.get_voice(voice_id)
        if voice is None:
            raise TTSEngineError(f"Unsupported voice: {voice_id}")

        model = self._storage.get_model(voice.model)
        if model is None:
            raise TTSEngineError(f"Unsupported model: {voice.model}")

        logger.info(
            "Synthesizing TTS. Text length: {text_length}. Voice: {voice_id}. Text format: {text_format}. Model: {model_name}",
            text_length=len(text),
            voice_id=voice_id,
            text_format=text_format.value,
            model_name=model.name,
        )

        cached = await self._get_tts_model(model)

        text_sentenizer = self._text_sentenizer_factory.create_text_sentenizer(
            voice=voice, format=text_format
        )
        if text_sentenizer is None:
            raise TTSEngineError(
                f"Text sentenizer not found for '{voice.locale}' locale and '{text_format.value}' format"
            )

        logger.debug(
            "Convert text into sentences using '{text_sentenizer}'",
            text_sentenizer=text_sentenizer.__class__.__name__,
        )

        sentences = text_sentenizer.text_to_sentences(
            text=text, max_chunk_chars=self._config.max_chunk_chars
        )

        text_normalizer = (
            self._text_normalizer_factory.create_text_normalizer(voice=voice, format=text_format)
            if self._text_normalizer_factory is not None
            else None
        )
        if text_normalizer is None:
            for sentence in sentences:
                yield await _process_chunk(
                    chunk=sentence, cached_model=cached, voice=voice, text_format=text_format
                )
        else:
            logger.debug(
                "Normalize text using '{text_normalizer}'",
                text_normalizer=text_normalizer.__class__.__name__,
            )

            chunks = text_normalizer.normalize_text(
                chunks=sentences,
                options=NormalizationOptions(voice=voice, model=model, silero_model=cached.model),
            )

            async for chunk in chunks:
                yield await _process_chunk(
                    chunk=chunk, cached_model=cached, voice=voice, text_format=text_format
                )

    async def shutdown(self):
        """Clears the model cache and forces VRAM to be released."""
        if not self._cached_models:
            return

        async with self._get_lock():
            if not self._cached_models:
                return

            logger.info(
                "Cleaning engine resources. Models count: {count}",
                count=len(self._cached_models),
            )

            while self._cached_models:
                _, evicted_model = self._cached_models.popitem()
                _clear_cached_model(evicted_model)
                del evicted_model

            gc.collect()
            _clear_torch_cache_on_device(self._device)

            logger.info("Engine resources have been cleared")

    async def _get_tts_model(self, model: Model) -> CachedModel:
        async with self._get_lock():
            if model.name in self._cached_models:
                logger.debug("Model '{name}' found in cache", name=model.name)

                # The model is in the cache: move it to the end (it is now the most recent)
                self._cached_models.move_to_end(model.name)
                cached = self._cached_models[model.name]
            else:
                logger.debug("Model '{name}' not found in cache", name=model.name)

                # The model is not in the cache: check the limit and download the old one if necessary
                self._evict_oldest_model()

                # Load and warm up the model
                cached = await self._warmup_tts_model(model)

        return cached

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _evict_oldest_model(self):
        """Internal method for removing the least used model from memory."""
        if len(self._cached_models) >= self._config.max_models:
            # delete the first model (the oldest)
            model_name, evicted_model = self._cached_models.popitem(last=False)

            logger.debug("Removing model '{model}' from cache", model=model_name)

            _clear_cached_model(evicted_model)
            del evicted_model
            gc.collect()
            _clear_torch_cache_on_device(self._device)

            logger.debug("Model '{model}' was removed from cache", model=model_name)

    def _resolve_tts_model(self, model: Model) -> tuple[str, list[int], str, dict[str, str]]:
        """Return the local path, sample rates, example text and speaker examples.

        Downloads the Silero models.yml file and the model itself if they are not available locally.
        Raises TTSEngineError on failure.
        """
        logger.debug(
            "Trying to resolve model '{model}'",
            model=model.name,
        )

        language = model.language
        if not language:
            raise TTSEngineError(f"Language isn't specified for Silero model: {model.name}")

        models_dir = self._config.models_dir

        lang_dir = os.path.join(models_dir, language)
        os.makedirs(lang_dir, exist_ok=True)

        yml_path = os.path.join(models_dir, "models.yml")
        registry = _get_models_data(
            yml_path, self._config.models_yml_url, self._config.models_yml_hash
        )

        tts_models = registry.get("tts_models", {})
        lang_models = tts_models.get(language, {})
        model_entry = lang_models.get(model.name, {})
        latest = model_entry.get("latest", {})
        sample_rates = latest.get("sample_rate", [])
        example_text = latest.get("example", "")
        raw_speakers = latest.get("speakers", {})
        speakers = {name: s.get("example", "") for name, s in raw_speakers.items()}

        model_path = os.path.join(lang_dir, f"{model.name}.pt")
        if os.path.isfile(model_path):
            logger.debug(
                "Model '{model}' found at path '{path}'", model=model.name, path=model_path
            )
            return model_path, sample_rates, example_text, speakers

        package_url = latest.get("package")
        if not package_url:
            raise TTSEngineError(
                f"Model '{model.name}' for language '{language}' not found in configuration file. "
                f"Delete '{yml_path}' to force a fresh download"
            )

        logger.debug(
            "Model '{model}' not found. Attempting to load from '{url}'",
            model=model.name,
            url=package_url,
        )

        try:
            torch.hub.download_url_to_file(package_url, model_path, hash_prefix=model.hash_prefix)
        except Exception as e:
            if os.path.isfile(model_path):
                os.remove(model_path)
            raise TTSEngineError(
                f"Failed to download model '{model.name}' for language '{language}'"
            ) from e

        logger.debug(
            "Model '{model}' is saved in the file '{path}'", model=model.name, path=model_path
        )

        return model_path, sample_rates, example_text, speakers

    async def _load_tts_model_async(self, model: Model) -> tuple[CachedModel, str, dict[str, str]]:
        """Loads the model into the cache and returns the cached model, sample text, and speaker samples."""

        # Move blocking disk reading and heavy PyTorch initialization to a separate thread
        def _sync_load():
            local_path, sample_rates, example_text, speakers = self._resolve_tts_model(model)
            try:
                logger.debug(
                    "Loading model '{model}' to '{device}'",
                    model=model.name,
                    device=self._device.type,
                )

                importer = torch.package.PackageImporter(local_path)
                pt_model = importer.load_pickle("tts_models", "model", map_location=self._device)
                # Ensure the model modules are shifted as well
                pt_model.to(self._device)

                logger.debug(
                    "Model '{model}' loaded to '{device}'",
                    model=model.name,
                    device=self._device.type,
                )

                return pt_model, sample_rates, example_text, speakers
            except Exception as e:
                raise TTSEngineError(
                    f"Failed to load model '{model.name}' with path: {local_path}. "
                    f"Try to delete model to force a fresh download"
                ) from e

        tts_model, sample_rates, example_text, speakers = await asyncio.to_thread(_sync_load)

        sample_rate = _select_sample_rate(self._config.sample_rate, sample_rates)
        semaphore = asyncio.Semaphore(self._config.max_concurrent_per_model)
        cached = CachedModel(tts_model, sample_rate, semaphore)
        self._cached_models[model.name] = cached

        logger.debug(
            "Model '{model}' was cached. Sample rate: '{sample_rate}'",
            model=model.name,
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

            logger.info("Warming up engine")

            models = self._storage.get_models()
            to_warm = [model for model in models if model.warmup][: self._config.max_models]

            logger.debug("Models to warm up: {count}", count=len(to_warm))

            for model in to_warm:
                await self._warmup_tts_model(model)

            logger.info("Engine has been warmed up")

    async def _warmup_tts_model(self, model: Model) -> CachedModel:
        cached, example_text, speakers = await self._load_tts_model_async(model)

        if speakers:
            speaker = next(iter(speakers))
            text = speakers[speaker]
        else:
            speaker = cached.model.speakers[0]
            text = example_text

        logger.debug(
            "Model '{model}' is warming up. Speaker: '{speaker}' Text: '{text}'",
            model=model.name,
            speaker=speaker,
            text=text,
        )

        try:
            await asyncio.to_thread(_run_tts_sync, cached, text, speaker)
            logger.debug("Model '{model}' has been warmed up.", model=model.name)
        except Exception:
            logger.exception("Failed to warm up the model '{model}'", model=model.name)

        return cached

    def get_storage(self) -> SileroTTSConfigStorage:
        """Return the config storage."""
        return self._storage

    def get_supported_text_formats(self) -> tuple[TextFormat, ...]:
        """Return supported text formats."""
        return tuple(TextFormat)
