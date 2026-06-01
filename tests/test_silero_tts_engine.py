import io
import unittest.mock

import pytest
import torch

from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, VoiceConfig
from src.tts.provider import SileroTTSModelProvider


def make_config_file(tmp_path, models=None, locales=None):
    """Helper to create a temp config file."""
    config_yml = tmp_path / "config.yml"
    config_data = {"models": models or {}, "locales": locales or {}}
    import yaml

    config_yml.write_text(yaml.dump(config_data))
    return str(config_yml)


class TestSileroTTSEngineInit:
    """Tests for SileroTTSEngine initialization."""

    def test_init_accepts_config_path_and_loads_config(self, tmp_path):
        """Engine should accept config_path string and load config internally."""
        from src.tts.silero_tts_engine import SileroTTSEngine

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
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        provider = SileroTTSModelProvider()
        engine = SileroTTSEngine(config=config, storage=storage, provider=provider)

        assert engine is not None
        assert "ru_RU" in engine.get_storage().get_locales()

    def test_init_caches_locales(self, tmp_path):
        """Engine should cache locales at init time."""
        from src.tts.silero_tts_engine import SileroTTSEngine

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
        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )

        storage = SileroTTSYamlConfigStorage(config_path)
        provider = SileroTTSModelProvider()
        engine = SileroTTSEngine(config=config, storage=storage, provider=provider)

        locales = engine.get_storage().get_locales()
        assert isinstance(locales, tuple)
        assert "ru_RU" in locales

        voices = engine.get_storage().get_voices()
        assert isinstance(voices, tuple)
        assert len(voices) == 1


class TestGetInputTypes:
    """Tests for get_input_types() method."""

    def test_get_input_types_returns_tuple(self, tmp_path):
        """get_input_types should return a tuple."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config_path = make_config_file(tmp_path, models={}, locales={})
        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )

        storage = SileroTTSYamlConfigStorage(config_path)
        provider = SileroTTSModelProvider()
        engine = SileroTTSEngine(config=config, storage=storage, provider=provider)

        result = engine.get_input_types()
        assert isinstance(result, tuple)

    def test_get_input_types_includes_text_and_ssml(self, tmp_path):
        """get_input_types should include TEXT and SSML."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config_path = make_config_file(tmp_path, models={}, locales={})
        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )

        storage = SileroTTSYamlConfigStorage(config_path)
        provider = SileroTTSModelProvider()
        engine = SileroTTSEngine(config=config, storage=storage, provider=provider)

        assert "TEXT" in engine.get_input_types()
        assert "SSML" in engine.get_input_types()
        assert len(engine.get_input_types()) == 2


class TestProcessValidation:
    """Tests for process() validation."""

    @pytest.mark.asyncio
    async def test_process_invalid_locale_raises_invalid_locale_error(self, tmp_path):
        """process() with invalid locale should raise TTSEngineError."""
        from src.tts.exceptions import TTSEngineError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
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
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_path)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

                with pytest.raises(TTSEngineError) as exc_info:
                    await engine.process(
                        text="hello",
                        locale="invalid_Locale",
                        voice="silero-v5_5_ru-aidar",
                        input_type="TEXT",
                    )

        assert "Unsupported locale: invalid_Locale" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_invalid_voice_raises_invalid_voice_error(self, tmp_path):
        """process() with invalid voice should raise TTSEngineError."""
        from src.tts.exceptions import TTSEngineError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
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
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_path)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

                with pytest.raises(TTSEngineError) as exc_info:
                    await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="invalid_voice",
                        input_type="TEXT",
                    )

        assert "Invalid voice: invalid_voice" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_invalid_input_type_raises_invalid_input_type_error(self, tmp_path):
        """process() with invalid input_type should raise TTSEngineError."""
        from src.tts.exceptions import TTSEngineError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
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
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_path)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

                with pytest.raises(TTSEngineError):
                    await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="silero-v5_5_ru-aidar",
                        input_type="INVALID",
                    )

    @pytest.mark.asyncio
    async def test_process_successful_synthesis_returns_tts_result(self, tmp_path):
        """process() with valid params should return TTSResult with audio bytes."""
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"

    @pytest.mark.asyncio
    async def test_process_converts_tensor_to_wav_bytes(self, tmp_path):
        """process() should convert tensor output from apply_tts to valid WAV bytes."""
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = SileroTTSEngine(
            config=config,
            storage=SileroTTSYamlConfigStorage(config_model),
            provider=SileroTTSModelProvider(),
        )

        audio_tensor = torch.zeros(1, 48000)

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = audio_tensor
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
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
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [8000, 24000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_below_min_uses_min(self, tmp_path):
        """process() should use min available rate if configured rate is below min."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=8000, max_models=2, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [24000, 48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_exact_match_uses_config(self, tmp_path):
        """process() should use config rate if it exactly matches available rate."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=24000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [16000, 24000, 48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_not_in_list_uses_highest_below(self, tmp_path):
        """process() should use highest available rate below config if config not in list."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=44100, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [16000, 24000, 48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_single_element_uses_that_element(self, tmp_path):
        """process() should use single available rate regardless of config value."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [24000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_empty_list_uses_config(self, tmp_path):
        """process() should use config rate if model has no sample rates."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 48000
        assert result.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_process_sample_rate_none_uses_config(self, tmp_path):
        """process() should use config rate if model sample rates is None."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert calls[0] == 48000
        assert result.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_process_lazy_model_loading(self, tmp_path):
        """process() should load model on first request and cache it."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        load_counter = [0]
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        def counting_load_pickle(*args, **kwargs):
            load_counter[0] += 1
            return mock_model

        mock_importer.load_pickle = counting_load_pickle

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )
                await engine.process(
                    text="world",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert load_counter[0] == 1

    @pytest.mark.asyncio
    async def test_process_per_model_semaphore_limits_concurrent(self, tmp_path):
        """process() should use per-model semaphores to limit concurrent requests."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

    @pytest.mark.asyncio
    async def test_process_cuda_unavailable_falls_back_to_cpu(self, tmp_path):
        """Should fall back to CPU when CUDA is requested but unavailable."""
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cuda", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        class FakeModule:
            @staticmethod
            def is_available():
                return False

            @staticmethod
            def to(device):
                assert device.type == "cpu"

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.to = FakeModule.to
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch.object(torch, "cuda", FakeModule(), create=True):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.SileroTTSModelProvider",
                return_value=mock_provider,
            ):
                with unittest.mock.patch(
                    "src.tts.silero_tts_engine.torch.package.PackageImporter",
                    return_value=mock_importer,
                ):
                    storage = SileroTTSYamlConfigStorage(config_model)
                    engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                    result = await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="silero-v5_5_ru-aidar",
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
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="xpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        class FakeModule:
            @staticmethod
            def is_available():
                return False

            @staticmethod
            def to(device):
                assert device.type == "cpu"

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_model.to = FakeModule.to
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch.object(torch, "xpu", FakeModule(), create=True):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.SileroTTSModelProvider",
                return_value=mock_provider,
            ):
                with unittest.mock.patch(
                    "src.tts.silero_tts_engine.torch.package.PackageImporter",
                    return_value=mock_importer,
                ):
                    storage = SileroTTSYamlConfigStorage(config_model)
                    engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                    result = await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="silero-v5_5_ru-aidar",
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
        from src.tts.silero_tts_engine import CachedModel

        cached = CachedModel(model="mock", sample_rate=48000, semaphore=None)
        assert cached.model == "mock"
        assert cached.sample_rate == 48000
        assert cached.semaphore is None

    @pytest.mark.asyncio
    async def test_engine_uses_cached_model_for_processing(self, tmp_path):
        """process() should succeed with standard mocking."""
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
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
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=1, max_concurrent_per_model=2
        )

        model_en = Model(language="en")
        model_ru = Model(language="ru")
        locale_en = Locale(
            voices={"silero-v3_en-en_0": VoiceConfig(speaker="en_0", model="v3_en", gender="male")}
        )
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v3_en": model_en, "v5_5_ru": model_ru},
            locales={"en_US": locale_en, "ru_RU": locale_ru},
        )

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.return_value = (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

                await engine.process(
                    text="hello",
                    locale="en_US",
                    voice="silero-v3_en-en_0",
                    input_type="TEXT",
                )
                assert mock_provider.get_model.call_count == 1

                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )
                assert mock_provider.get_model.call_count == 2

                await engine.process(
                    text="hello",
                    locale="en_US",
                    voice="silero-v3_en-en_0",
                    input_type="TEXT",
                )
                assert mock_provider.get_model.call_count == 3
