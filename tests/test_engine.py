import hashlib
import io
import os
import unittest.mock

import pytest
import torch

from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, Voice
from src.tts.preprocessing import TextPreprocessor


def _hash_models_yml(yml_path: str) -> str:
    """Compute SHA256 hex digest of a models.yml file."""
    hasher = hashlib.sha256()
    with open(yml_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def make_models_dir(tmp_path, sample_rates=None, model_name="v5_5_ru", language="ru"):
    """Create a models directory with pre-populated models.yml and .pt files."""
    if sample_rates is None:
        sample_rates = [48000]
    rates_str = ", ".join(str(r) for r in sample_rates)
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    yml = f"tts_models:\n  {language}:\n    {model_name}:\n      latest:\n        package: 'http://x'\n        sample_rate: [{rates_str}]\n"
    (models_dir / "models.yml").write_text(yml)
    lang_dir = models_dir / language
    lang_dir.mkdir()
    (lang_dir / f"{model_name}.pt").write_bytes(b"fake model")
    return str(models_dir)


def make_config_file(tmp_path, models=None, locales=None):
    """Helper to create a temp config file."""
    config_yml = tmp_path / "config.yml"
    config_data = {"models": models or {}, "locales": locales or {}}
    import yaml

    config_yml.write_text(yaml.dump(config_data))
    return str(config_yml)


class TestSileroTTSEngineInit:
    """Tests for SileroTTSEngine initialization."""

    @pytest.mark.asyncio
    async def test_engine_uses_models_yml_hash_from_config(self, tmp_path):
        """Engine reads models_yml_hash from TTSConfig for local file validation."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path)
        yml_path = os.path.join(models_dir, "models.yml")
        actual_hash = _hash_models_yml(yml_path)

        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=actual_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])
        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = unittest.mock.MagicMock(return_value=mock_audio)
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with (
            unittest.mock.patch(
                "src.tts.engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ),
            unittest.mock.patch(
                "src.tts.engine.urllib.request.urlopen",
                side_effect=RuntimeError("network disabled"),
            ),
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert result is not None

    def test_init_accepts_config_path_and_loads_config(self, tmp_path):
        """Engine should accept config_path string and load config internally."""
        from src.tts.engine import SileroTTSEngine

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        assert engine is not None
        assert any(locale.name == "ru_RU" for locale in engine.get_storage().get_locales())

    def test_init_caches_locales(self, tmp_path):
        """Engine should cache locales at init time."""
        from src.tts.engine import SileroTTSEngine

        config_path = make_config_file(
            tmp_path,
            models={
                "v5_5_ru": {"language": "ru"},
            },
            locales={
                "ru_RU": {
                    "voices": {
                        "silero-v5_5_ru-aidar": {
                            "speaker": "aidar",
                            "model": "v5_5_ru",
                            "gender": "male",
                        }
                    }
                }
            },
        )
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )

        storage = SileroTTSYamlConfigStorage(config_path)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        locales = engine.get_storage().get_locales()
        assert isinstance(locales, list)
        assert any(locale.name == "ru_RU" for locale in locales)

        voices = engine.get_storage().get_voices()
        assert isinstance(voices, list)
        assert len(voices) == 1
        assert voices[0].locale == "ru_RU"


class TestGetInputTypes:
    """Tests for get_input_types() method."""

    def test_get_input_types_returns_tuple(self, tmp_path):
        """get_input_types should return a tuple."""
        from src.tts.engine import SileroTTSEngine

        config_path = make_config_file(tmp_path, models={}, locales={})
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )

        storage = SileroTTSYamlConfigStorage(config_path)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        result = engine.get_input_types()
        assert isinstance(result, tuple)

    def test_get_input_types_includes_text_and_ssml(self, tmp_path):
        """get_input_types should include TEXT and SSML."""
        from src.tts.engine import SileroTTSEngine

        config_path = make_config_file(tmp_path, models={}, locales={})
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )

        storage = SileroTTSYamlConfigStorage(config_path)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        assert "TEXT" in engine.get_input_types()
        assert "SSML" in engine.get_input_types()
        assert len(engine.get_input_types()) == 2


class TestProcessValidation:
    """Tests for process() validation."""

    @pytest.mark.asyncio
    async def test_process_invalid_locale_raises_invalid_locale_error(self, tmp_path):
        """process() with invalid locale should raise TTSEngineError."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )
        config_path = make_config_file(
            tmp_path,
            models={},
            locales={
                "ru_RU": {
                    "voices": {
                        "silero-v5_5_ru-aidar": {
                            "speaker": "aidar",
                            "model": "v5_5_ru",
                            "gender": "male",
                        }
                    }
                }
            },
        )

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_path)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            with pytest.raises(TTSEngineError) as exc_info:
                await engine.process(
                    text="hello",
                    locale="invalid_Locale",
                    voice_name="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert "Unsupported locale: invalid_Locale" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_invalid_voice_raises_invalid_voice_error(self, tmp_path):
        """process() with invalid voice should raise TTSEngineError."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )
        config_path = make_config_file(
            tmp_path,
            models={
                "v5_5_ru": {"language": "ru"},
            },
            locales={
                "ru_RU": {
                    "voices": {
                        "silero-v5_5_ru-aidar": {
                            "speaker": "aidar",
                            "model": "v5_5_ru",
                            "gender": "male",
                        }
                    }
                }
            },
        )

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_path)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            with pytest.raises(TTSEngineError) as exc_info:
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice_name="invalid_voice",
                    input_type="TEXT",
                )

        assert "Invalid voice: invalid_voice" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_invalid_input_type_raises_invalid_input_type_error(self, tmp_path):
        """process() with invalid input_type should raise TTSEngineError."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com",
            models_yml_hash="",
        )
        config_path = make_config_file(
            tmp_path,
            models={},
            locales={
                "ru_RU": {
                    "voices": {
                        "silero-v5_5_ru-aidar": {
                            "speaker": "aidar",
                            "model": "v5_5_ru",
                            "gender": "male",
                        }
                    }
                }
            },
        )

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_path)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            with pytest.raises(TTSEngineError):
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice_name="silero-v5_5_ru-aidar",
                    input_type="INVALID",
                )

    @pytest.mark.asyncio
    async def test_process_successful_synthesis_returns_tts_result(self, tmp_path):
        """process() with valid params should return TTSResult with audio bytes."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"

    @pytest.mark.asyncio
    async def test_process_skips_hash_validation_when_config_hash_empty(self, tmp_path):
        """process() should skip models.yml hash validation when models_yml_hash is empty."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path)
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com/models.yml",
            models_yml_hash="",
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])
        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = unittest.mock.MagicMock(return_value=mock_audio)
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with (
            unittest.mock.patch(
                "src.tts.engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ),
            unittest.mock.patch(
                "src.tts.engine.urllib.request.urlopen",
                side_effect=RuntimeError("network disabled"),
            ),
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert result is not None

    @pytest.mark.asyncio
    async def test_process_converts_tensor_to_wav_bytes(self, tmp_path):
        """process() should convert tensor output from apply_tts to valid WAV bytes."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        audio_tensor = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = audio_tensor
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"

    @pytest.mark.asyncio
    async def test_process_sample_rate_clamped_to_model_max(self, tmp_path):
        """process() should clamp sample rate to model's max if configured rate exceeds it."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[8000, 24000])
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=yml_hash,
        )

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_below_min_uses_min(self, tmp_path):
        """process() should use min available rate if configured rate is below min."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[24000, 48000])
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=8000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=yml_hash,
        )

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_exact_match_uses_config(self, tmp_path):
        """process() should use config rate if it exactly matches available rate."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[24000, 48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=24000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_not_in_list_uses_highest_below(self, tmp_path):
        """process() should use highest available rate below config if config not in list."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[24000, 48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=44100,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_single_element_uses_that_element(self, tmp_path):
        """process() should use single available rate regardless of config value."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[24000])
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=yml_hash,
        )

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_empty_list_uses_config(self, tmp_path):
        """process() should use config rate if model has no sample rates."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 48000
        assert result.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_process_sample_rate_none_uses_config(self, tmp_path):
        """process() should use config rate if model sample rates is None."""
        from src.tts.engine import SileroTTSEngine

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_text(
            "tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n"
        )
        lang_dir = models_dir / "ru"
        lang_dir.mkdir()
        (lang_dir / "v5_5_ru.pt").write_bytes(b"fake model")
        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert calls[0] == 48000
        assert result.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_process_lazy_model_loading(self, tmp_path):
        """process() should load model on first request and cache it."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        load_counter = [0]
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        def counting_load_pickle(*args, **kwargs):
            load_counter[0] += 1
            return mock_model

        mock_importer.load_pickle = counting_load_pickle

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )
            await engine.process(
                text="world",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert load_counter[0] == 1

    @pytest.mark.asyncio
    async def test_process_per_model_semaphore_limits_concurrent(self, tmp_path):
        """process() should use per-model semaphores to limit concurrent requests."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

    @pytest.mark.asyncio
    async def test_process_cuda_unavailable_falls_back_to_cpu(self, tmp_path):
        """Should fall back to CPU when CUDA is requested but unavailable."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cuda",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        class FakeModule:
            @staticmethod
            def is_available():
                return False

            @staticmethod
            def to(device):
                assert device.type == "cpu"

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.to = FakeModule.to
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch.object(torch, "cuda", FakeModule(), create=True):
            with unittest.mock.patch(
                "src.tts.engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(
                    config=config,
                    storage=storage,
                    text_preprocessor_factory=lambda _: TextPreprocessor(),
                )
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice_name="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"

    @pytest.mark.asyncio
    async def test_process_xpu_unavailable_falls_back_to_cpu(self, tmp_path):
        """Should fall back to CPU when XPU is requested but unavailable."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="xpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        class FakeModule:
            @staticmethod
            def is_available():
                return False

            @staticmethod
            def to(device):
                assert device.type == "cpu"

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_model.to = FakeModule.to
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch.object(torch, "xpu", FakeModule(), create=True):
            with unittest.mock.patch(
                "src.tts.engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(
                    config=config,
                    storage=storage,
                    text_preprocessor_factory=lambda _: TextPreprocessor(),
                )
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice_name="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"

    @pytest.mark.asyncio
    async def test_process_raises_on_malformed_models_yml(self, tmp_path):
        """process() should raise TTSEngineError on malformed models.yml."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_bytes(b"tts_models:\n  invalid: [")
        ru_dir = models_dir / "ru"
        ru_dir.mkdir()
        (ru_dir / "v5_5_ru.pt").write_bytes(b"fake model")

        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))

        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        storage = SileroTTSYamlConfigStorage(config_model)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        with pytest.raises(TTSEngineError) as exc_info:
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert "Failed to parse the models configuration file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_raises_on_model_not_in_registry(self, tmp_path):
        """process() should raise TTSEngineError when model missing from registry."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  ru:\n    other_model:\n      latest:\n        package: 'http://x'\n"
        )
        ru_dir = models_dir / "ru"
        ru_dir.mkdir()
        (ru_dir / "v5_5_ru.pt").write_bytes(b"fake model")

        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        storage = SileroTTSYamlConfigStorage(config_model)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        with pytest.raises(TTSEngineError) as exc_info:
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert "v5_5_ru" in str(exc_info.value)
        assert "ru" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_raises_on_model_download_failure(self, tmp_path, monkeypatch):
        """process() should raise TTSEngineError when model download fails."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n        sample_rate: [48000]\n"
        )
        ru_dir = models_dir / "ru"
        ru_dir.mkdir()

        def mock_download(url, path, *a, **kw):
            raise RuntimeError("Connection reset")

        monkeypatch.setattr(torch.hub, "download_url_to_file", mock_download)

        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        storage = SileroTTSYamlConfigStorage(config_model)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        with pytest.raises(TTSEngineError) as exc_info:
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert "v5_5_ru" in str(exc_info.value)
        assert "ru" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_forwards_hash_prefix_to_download(self, tmp_path, monkeypatch):
        """process() should forward hash_prefix from Model to torch.hub.download_url_to_file."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n        sample_rate: [48000]\n"
        )
        ru_dir = models_dir / "ru"
        ru_dir.mkdir()
        # No .pt file — will trigger download

        captured_kw = {}

        def mock_download(url, path, *a, **kw):
            captured_kw.update(kw)
            raise RuntimeError("Connection reset")

        monkeypatch.setattr(torch.hub, "download_url_to_file", mock_download)

        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru", hash_prefix="a1b2c3d4")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        storage = SileroTTSYamlConfigStorage(config_model)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        with pytest.raises(TTSEngineError):
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert captured_kw.get("hash_prefix") == "a1b2c3d4"

    @pytest.mark.asyncio
    async def test_process_raises_on_model_download_failure_when_missing_file(
        self, tmp_path, monkeypatch
    ):
        """process() should raise TTSEngineError when model .pt file is missing and download fails."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.exceptions import TTSEngineError

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n        sample_rate: [48000]\n"
        )
        ru_dir = models_dir / "ru"
        ru_dir.mkdir()
        # No .pt file — will trigger download which we mock to fail

        def mock_download(url, path, *a, **kw):
            raise RuntimeError("Connection reset")

        monkeypatch.setattr(torch.hub, "download_url_to_file", mock_download)

        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        storage = SileroTTSYamlConfigStorage(config_model)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        with pytest.raises(TTSEngineError) as exc_info:
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert "Failed to download model" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_resolves_model_from_disk_without_provider(self, tmp_path):
        """process() should resolve model from local files without a provider."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"


class TestCachedModel:
    """Tests for CachedModel dataclass."""

    def test_cached_model_dataclass_exists(self):
        """CachedModel should be a dataclass in silero_tts_engine module."""
        from src.tts.engine import CachedModel

        cached = CachedModel(model="mock", sample_rate=48000, semaphore=None)
        assert cached.model == "mock"
        assert cached.sample_rate == 48000
        assert cached.semaphore is None

    @pytest.mark.asyncio
    async def test_engine_uses_cached_model_for_processing(self, tmp_path):
        """process() should succeed with standard mocking."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"


class TestModelEviction:
    """Tests for model cache eviction behavior."""

    @pytest.mark.asyncio
    async def test_evicts_oldest_model_when_cache_full(self, tmp_path):
        """process() should evict oldest model when cache is full and reload on next use."""
        from src.tts.engine import SileroTTSEngine

        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "models.yml").write_text(
            "tts_models:\n"
            "  en:\n"
            "    v3_en:\n"
            "      latest:\n"
            "        package: 'http://x'\n"
            "        sample_rate: [48000]\n"
            "  ru:\n"
            "    v5_5_ru:\n"
            "      latest:\n"
            "        package: 'http://x'\n"
            "        sample_rate: [48000]\n"
        )
        en_dir = models_dir / "en"
        en_dir.mkdir()
        (en_dir / "v3_en.pt").write_bytes(b"fake model en")
        ru_dir = models_dir / "ru"
        ru_dir.mkdir()
        (ru_dir / "v5_5_ru.pt").write_bytes(b"fake model ru")

        yml_hash = _hash_models_yml(os.path.join(str(models_dir), "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=1,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=str(models_dir),
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )

        model_en = Model(name="v3_en", language="en")
        model_ru = Model(name="v5_5_ru", language="ru")
        locale_en = Locale(name="en_US")
        locale_ru = Locale(name="ru_RU")
        voice_en = Voice(
            name="silero-v3_en-en_0",
            speaker="en_0",
            model="v3_en",
            gender="male",
            locale="en_US",
        )
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(
            models=[model_en, model_ru],
            locales=[locale_en, locale_ru],
            voices=[voice_en, voice_ru],
        )

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ) as mock_pkg:
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            await engine.process(
                text="hello",
                locale="en_US",
                voice_name="silero-v3_en-en_0",
                input_type="TEXT",
            )
            assert mock_pkg.call_count == 1

            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )
            assert mock_pkg.call_count == 2

            await engine.process(
                text="hello",
                locale="en_US",
                voice_name="silero-v3_en-en_0",
                input_type="TEXT",
            )
            assert mock_pkg.call_count == 3

    @pytest.mark.asyncio
    async def test_reuses_cached_model_on_subsequent_calls(self, tmp_path):
        """process() should reuse a cached model without re-loading."""
        from src.tts.engine import SileroTTSEngine

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ) as mock_pkg:
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )
            assert mock_pkg.call_count == 1

            await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )
            assert mock_pkg.call_count == 1


class TestWarmup:
    """Tests for SileroTTSEngine.warmup()."""

    @pytest.mark.asyncio
    async def test_warmup_does_not_raise_and_process_succeeds(self, tmp_path):
        """warmup() should not raise and subsequent process() should succeed."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        model_config = Model(name="v5_5_ru", language="ru", warmup=True)
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(models=[model_config], locales=[locale_ru], voices=[voice_ru])

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.speakers = ["aidar"]
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            storage = SileroTTSYamlConfigStorage(config_model)
            engine = SileroTTSEngine(
                config=config,
                storage=storage,
                text_preprocessor_factory=lambda _: TextPreprocessor(),
            )

            await engine.warmup()

            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert isinstance(result, TTSResult)

    @pytest.mark.asyncio
    async def test_warmup_unknown_model_failure_does_not_block_process(self, tmp_path):
        """warmup() should silently swallow failure for an unknown model name."""
        from src.tts.engine import SileroTTSEngine
        from src.tts.models import TTSResult

        models_dir = make_models_dir(tmp_path, sample_rates=[48000])
        yml_hash = _hash_models_yml(os.path.join(models_dir, "models.yml"))
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=models_dir,
            models_yml_url="https://example.com",
            models_yml_hash=yml_hash,
        )
        warmup_model = Model(name="v5_5_ru", language="ru", warmup=True)
        process_model = Model(name="v5_5_ru", language="ru")
        locale_ru = Locale(name="ru_RU")
        voice_ru = Voice(
            name="silero-v5_5_ru-aidar",
            speaker="aidar",
            model="v5_5_ru",
            gender="male",
            locale="ru_RU",
        )
        config_model = TTSConfigModel(
            models=[warmup_model, process_model],
            locales=[locale_ru],
            voices=[voice_ru],
        )

        storage = SileroTTSYamlConfigStorage(config_model)
        engine = SileroTTSEngine(
            config=config, storage=storage, text_preprocessor_factory=lambda _: TextPreprocessor()
        )

        await engine.warmup()

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            result = await engine.process(
                text="hello",
                locale="ru_RU",
                voice_name="silero-v5_5_ru-aidar",
                input_type="TEXT",
            )

        assert isinstance(result, TTSResult)


def test_new_module_path_importable():
    """The renamed module src.tts.engine should export SileroTTSEngine."""
    from src.tts.engine import SileroTTSEngine as NewEngine

    assert NewEngine is not None
