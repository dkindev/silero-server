import unittest.mock

import pytest
import torch

from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, VoiceConfig


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
        from src.tts.silero_tts_engine import create_silero_engine

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

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, str(config_yml))

        assert engine is not None
        assert "ru_RU" in engine.get_locales()

    def test_init_caches_locales(self, tmp_path):
        """Engine should cache locales at init time."""
        from src.tts.silero_tts_engine import create_silero_engine

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
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        locales = engine.get_locales()
        assert isinstance(locales, tuple)
        assert "ru_RU" in locales

    def test_init_caches_voices(self, tmp_path):
        """Engine should cache voices at init time."""
        from src.tts.silero_tts_engine import create_silero_engine

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
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        voices = engine.get_voices()
        assert isinstance(voices, tuple)
        assert len(voices) == 1


class TestGetLocales:
    """Tests for get_locales() method."""

    def test_get_locales_returns_tuple(self, tmp_path):
        """get_locales should return a tuple."""
        from src.tts.silero_tts_engine import create_silero_engine

        config_path = make_config_file(tmp_path, models={}, locales={})
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        result = engine.get_locales()
        assert isinstance(result, tuple)

    def test_get_locales_returns_locale_strings_from_config(self, tmp_path):
        """get_locales should return locale strings from config."""
        from src.tts.silero_tts_engine import create_silero_engine

        config_path = make_config_file(
            tmp_path,
            models={},
            locales={"ru_RU": {"voices": {}}, "en_US": {"voices": {}}},
        )
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        result = engine.get_locales()
        assert "ru_RU" in result
        assert "en_US" in result
        assert len(result) == 2


class TestGetVoices:
    """Tests for get_voices() method."""

    def test_get_voices_returns_tuple(self, tmp_path):
        """get_voices should return a tuple."""
        from src.tts.silero_tts_engine import create_silero_engine

        config_path = make_config_file(tmp_path, models={}, locales={})
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        result = engine.get_voices()
        assert isinstance(result, tuple)

    def test_get_voices_returns_mary_tts_format(self, tmp_path):
        """get_voices should return '{voice} {locale} {gender}' format."""
        from src.tts.silero_tts_engine import create_silero_engine

        config_path = make_config_file(
            tmp_path,
            models={},
            locales={
                "ru_RU": {
                    "voices": {"aidar": {"speaker": "aidar", "model": "v5_5_ru", "gender": "male"}}
                }
            },
        )
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        result = engine.get_voices()
        assert "aidar ru_RU male" in result

    def test_get_voices_returns_all_voices_from_all_locales(self, tmp_path):
        """get_voices should include voices from all locales."""
        from src.tts.silero_tts_engine import create_silero_engine

        config_path = make_config_file(
            tmp_path,
            models={},
            locales={
                "ru_RU": {
                    "voices": {"aidar": {"speaker": "aidar", "model": "v5_5_ru", "gender": "male"}}
                },
                "en_US": {
                    "voices": {"en_0": {"speaker": "en_0", "model": "v3_en", "gender": "male"}}
                },
            },
        )
        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)

        engine = create_silero_engine(config, config_path)

        result = engine.get_voices()
        assert len(result) == 2
        assert any("aidar" in v for v in result)
        assert any("en_0" in v for v in result)


class TestProcessValidation:
    """Tests for process() validation."""

    @pytest.mark.asyncio
    async def test_process_invalid_locale_raises_invalid_locale_error(self, tmp_path):
        """process() with invalid locale should raise InvalidLocaleError."""
        from src.tts.exceptions import InvalidLocaleError
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
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

        engine = create_silero_engine(config, config_path)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                with pytest.raises(InvalidLocaleError) as exc_info:
                    await engine.process(
                        text="hello",
                        locale="invalid_Locale",
                        voice="silero-v5_5_ru-aidar",
                        input_type="TEXT",
                        output_type="AUDIO",
                    )

        assert exc_info.value.locale == "invalid_Locale"

    @pytest.mark.asyncio
    async def test_process_invalid_voice_raises_invalid_voice_error(self, tmp_path):
        """process() with invalid voice should raise InvalidVoiceError."""
        from src.tts.exceptions import InvalidVoiceError
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
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

        engine = create_silero_engine(config, config_path)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                with pytest.raises(InvalidVoiceError) as exc_info:
                    await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="invalid_voice",
                        input_type="TEXT",
                        output_type="AUDIO",
                    )

        assert exc_info.value.voice == "invalid_voice"

    @pytest.mark.asyncio
    async def test_process_invalid_input_type_raises_invalid_input_type_error(self, tmp_path):
        """process() with invalid input_type should raise InvalidInputTypeError."""
        from src.tts.exceptions import InvalidInputTypeError
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
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

        engine = create_silero_engine(config, config_path)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                with pytest.raises(InvalidInputTypeError):
                    await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="silero-v5_5_ru-aidar",
                        input_type="INVALID",
                        output_type="AUDIO",
                    )

    @pytest.mark.asyncio
    async def test_process_invalid_output_type_raises_invalid_output_type_error(self, tmp_path):
        """process() with invalid output_type should raise InvalidOutputTypeError."""
        from src.tts.exceptions import InvalidOutputTypeError
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
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

        engine = create_silero_engine(config, config_path)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                with pytest.raises(InvalidOutputTypeError):
                    await engine.process(
                        text="hello",
                        locale="ru_RU",
                        voice="silero-v5_5_ru-aidar",
                        input_type="TEXT",
                        output_type="PHONEMES",
                    )

    @pytest.mark.asyncio
    async def test_process_successful_synthesis_returns_tts_result(self, tmp_path):
        """process() with valid params should return TTSResult with audio bytes."""
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert isinstance(result, TTSResult)
        assert result.audio == mock_audio
        assert result.sample_rate == 48000
        assert result.model == "v5_5_ru"

    @pytest.mark.asyncio
    async def test_process_sample_rate_clamped_to_model_max(self, tmp_path):
        """process() should clamp sample rate to model's max if configured rate exceeds it."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider,
                "get_model",
                return_value=(str(tmp_path / "model.pt"), [8000, 24000]),
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_below_min_uses_min(self, tmp_path):
        """process() should use min available rate if configured rate is below min."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=8000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider,
                "get_model",
                return_value=(str(tmp_path / "model.pt"), [24000, 48000]),
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_exact_match_uses_config(self, tmp_path):
        """process() should use config rate if it exactly matches available rate."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=24000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider,
                "get_model",
                return_value=(str(tmp_path / "model.pt"), [16000, 24000, 48000]),
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_not_in_list_uses_highest_below(self, tmp_path):
        """process() should use highest available rate below config if config not in list."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=44100, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider,
                "get_model",
                return_value=(str(tmp_path / "model.pt"), [16000, 24000, 48000]),
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_single_element_uses_that_element(self, tmp_path):
        """process() should use single available rate regardless of config value."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [24000])
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 24000
        assert result.sample_rate == 24000

    @pytest.mark.asyncio
    async def test_process_sample_rate_empty_list_uses_config(self, tmp_path):
        """process() should use config rate if model has no sample rates."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 48000
        assert result.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_process_sample_rate_none_uses_config(self, tmp_path):
        """process() should use config rate if model sample rates is None."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert calls[0] == 48000
        assert result.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_process_lazy_model_loading(self, tmp_path):
        """process() should load model on first request and cache it."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        load_counter = [0]
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        def counting_load_pickle(*args, **kwargs):
            load_counter[0] += 1
            return mock_model

        mock_importer.load_pickle = counting_load_pickle

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )
                await engine.process(
                    text="world",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert load_counter[0] == 1

    @pytest.mark.asyncio
    async def test_process_per_model_semaphore_limits_concurrent(self, tmp_path):
        """process() should use per-model semaphores to limit concurrent requests."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert "v5_5_ru" in engine._cached_models
        assert engine._cached_models["v5_5_ru"].semaphore._value == 2


class TestCaching:
    """Tests for caching behavior."""

    def test_get_locales_returns_cached_tuple(self):
        """Repeated get_locales calls should return same object."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        locale_ru = Locale(voices={})
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = create_silero_engine(config, config_model)

        result1 = engine.get_locales()
        result2 = engine.get_locales()

        assert result1 is result2

    def test_get_voices_returns_cached_tuple(self):
        """Repeated get_voices calls should return same object."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        locale_ru = Locale(voices={})
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = create_silero_engine(config, config_model)

        result1 = engine.get_voices()
        result2 = engine.get_voices()

        assert result1 is result2


class TestResolveDevice:
    """Tests for _resolve_device method."""

    def test_resolve_device_cuda_unavailable_falls_back_to_cpu(self):
        """Should return cpu device when cuda is unavailable."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cuda", sample_rate=48000, max_concurrent_per_model=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = create_silero_engine(config, config_model)

        with unittest.mock.patch("torch.cuda.is_available", return_value=False):
            device = engine._resolve_device("cuda")

        assert str(device) == "cpu"

    def test_resolve_device_xpu_unavailable_falls_back_to_cpu(self):
        """Should return cpu device when xpu is unavailable."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="xpu", sample_rate=48000, max_concurrent_per_model=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = create_silero_engine(config, config_model)

        class FakeXpuModule:
            @staticmethod
            def is_available():
                return False

        with unittest.mock.patch.object(torch, "xpu", FakeXpuModule(), create=True):
            device = engine._resolve_device("xpu")

        assert str(device) == "cpu"


class TestLoadModel:
    """Tests for _load_model method."""

    def test_load_model_to_raises_raises_tts_processing_error(self, tmp_path):
        """Should raise TTSProcessingError when model.to() fails."""
        from src.tts.exceptions import TTSProcessingError
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = create_silero_engine(config, config_model)

        mock_model = unittest.mock.MagicMock()
        mock_model.to.side_effect = RuntimeError("device error")
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                with pytest.raises(TTSProcessingError, match="Failed to move model"):
                    engine._load_model("v5_5_ru", Model(language="ru"))

    def test_load_model_success_caches_model(self, tmp_path):
        """Should cache model on successful load."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = create_silero_engine(config, config_model)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                engine._load_model("v5_5_ru", Model(language="ru"))

        assert "v5_5_ru" in engine._cached_models
        assert engine._cached_models["v5_5_ru"].model is mock_model
        mock_model.to.assert_called_once_with(engine._device)


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
    async def test_cached_model_bundles_sample_rate_at_load_time(self, tmp_path):
        """CachedModel should store sample_rate computed at model load time."""
        from src.tts.silero_tts_engine import CachedModel, create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                cached = engine._load_model("v5_5_ru", model_config)

        assert isinstance(cached, CachedModel)
        assert cached.model is mock_model
        assert cached.sample_rate == 48000
        assert cached.semaphore is not None

    @pytest.mark.asyncio
    async def test_engine_uses_cached_model_for_processing(self, tmp_path):
        """process() should use CachedModel from cache."""
        from src.tts.silero_tts_engine import CachedModel, create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                    output_type="AUDIO",
                )

        assert "v5_5_ru" in engine._cached_models
        cached = engine._cached_models["v5_5_ru"]
        assert isinstance(cached, CachedModel)
        assert cached.semaphore is not None
