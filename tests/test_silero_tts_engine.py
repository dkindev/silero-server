import unittest.mock

import pytest

from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, VoiceConfig


class TestSileroTTSEngineInit:
    """Tests for SileroTTSEngine initialization."""

    def test_init_accepts_tts_config_and_config_model(self):
        """Engine should accept TTSConfig and TTSConfigModel."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = SileroTTSEngine(config, config_model)

        assert engine is not None

    def test_init_caches_locales(self):
        """Engine should cache locales at init time."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        locales = engine.get_locales()
        assert isinstance(locales, tuple)
        assert "ru_RU" in locales

    def test_init_caches_voices(self):
        """Engine should cache voices at init time."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        voices = engine.get_voices()
        assert isinstance(voices, tuple)
        assert len(voices) == 1


class TestGetLocales:
    """Tests for get_locales() method."""

    def test_get_locales_returns_tuple(self):
        """get_locales should return a tuple."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = SileroTTSEngine(config, config_model)

        result = engine.get_locales()
        assert isinstance(result, tuple)

    def test_get_locales_returns_locale_strings_from_config(self):
        """get_locales should return locale strings from config."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(voices={})
        locale_en = Locale(voices={})
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru, "en_US": locale_en})

        engine = SileroTTSEngine(config, config_model)

        result = engine.get_locales()
        assert "ru_RU" in result
        assert "en_US" in result
        assert len(result) == 2


class TestGetVoices:
    """Tests for get_voices() method."""

    def test_get_voices_returns_tuple(self):
        """get_voices should return a tuple."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = SileroTTSEngine(config, config_model)

        result = engine.get_voices()
        assert isinstance(result, tuple)

    def test_get_voices_returns_mary_tts_format(self):
        """get_voices should return '{voice} {locale} {gender}' format."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={"aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")}
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        result = engine.get_voices()
        assert "aidar ru_RU male" in result

    def test_get_voices_returns_all_voices_from_all_locales(self):
        """get_voices should include voices from all locales."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={"aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")}
        )
        locale_en = Locale(
            voices={"en_0": VoiceConfig(speaker="en_0", model="v3_en", gender="male")}
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru, "en_US": locale_en})

        engine = SileroTTSEngine(config, config_model)

        result = engine.get_voices()
        assert len(result) == 2
        assert any("aidar" in v for v in result)
        assert any("en_0" in v for v in result)


class TestProcessValidation:
    """Tests for process() validation."""

    @pytest.mark.asyncio
    async def test_process_invalid_locale_raises_invalid_locale_error(self):
        """process() with invalid locale should raise InvalidLocaleError."""
        from src.tts.exceptions import InvalidLocaleError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

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
    async def test_process_invalid_voice_raises_invalid_voice_error(self):
        """process() with invalid voice should raise InvalidVoiceError."""
        from src.tts.exceptions import InvalidVoiceError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

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
    async def test_process_invalid_input_type_raises_invalid_input_type_error(self):
        """process() with invalid input_type should raise InvalidInputTypeError."""
        from src.tts.exceptions import InvalidInputTypeError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        with pytest.raises(InvalidInputTypeError):
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice="silero-v5_5_ru-aidar",
                input_type="INVALID",
                output_type="AUDIO",
            )

    @pytest.mark.asyncio
    async def test_process_invalid_output_type_raises_invalid_output_type_error(self):
        """process() with invalid output_type should raise InvalidOutputTypeError."""
        from src.tts.exceptions import InvalidOutputTypeError
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        with pytest.raises(InvalidOutputTypeError):
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice="silero-v5_5_ru-aidar",
                input_type="TEXT",
                output_type="PHONEMES",
            )

    @pytest.mark.asyncio
    async def test_process_successful_synthesis_returns_tts_result(self):
        """process() with valid params should return TTSResult with audio bytes."""
        from src.tts.result import TTSResult
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        model_config = Model(language="ru", sample_rates=[8000, 24000, 48000])
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = SileroTTSEngine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.hub.load", return_value=mock_model
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
    async def test_process_sample_rate_clamped_to_model_max(self):
        """process() should clamp sample rate to model's max if configured rate exceeds it."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        model_config = Model(language="ru", sample_rates=[8000, 24000])
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = SileroTTSEngine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        calls = []

        def capture_apply_tts(text, speaker, sample_rate):
            calls.append(sample_rate)
            return mock_audio

        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts = capture_apply_tts

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.hub.load", return_value=mock_model
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
    async def test_process_lazy_model_loading(self):
        """process() should load model on first request and cache it."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        model_config = Model(language="ru", sample_rates=[48000])
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = SileroTTSEngine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        load_counter = [0]

        def counting_load(*args, **kwargs):
            load_counter[0] += 1
            return mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.hub.load", side_effect=counting_load
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
    async def test_process_per_model_semaphore_limits_concurrent(self):
        """process() should use per-model semaphores to limit concurrent requests."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        model_config = Model(language="ru", sample_rates=[48000])
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = SileroTTSEngine(config, config_model)

        mock_audio = b"RIFF\x00\x00\x00WAVEfmt "
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.hub.load", return_value=mock_model
        ):
            await engine.process(
                text="hello",
                locale="ru_RU",
                voice="silero-v5_5_ru-aidar",
                input_type="TEXT",
                output_type="AUDIO",
            )

        assert "v5_5_ru" in engine._model_semaphores
        assert engine._model_semaphores["v5_5_ru"]._value == 2


class TestCaching:
    """Tests for caching behavior."""

    def test_get_locales_returns_cached_tuple(self):
        """Repeated get_locales calls should return same object."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(voices={})
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        result1 = engine.get_locales()
        result2 = engine.get_locales()

        assert result1 is result2

    def test_get_voices_returns_cached_tuple(self):
        """Repeated get_voices calls should return same object."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_locale=2)
        locale_ru = Locale(voices={})
        config_model = TTSConfigModel(models={}, locales={"ru_RU": locale_ru})

        engine = SileroTTSEngine(config, config_model)

        result1 = engine.get_voices()
        result2 = engine.get_voices()

        assert result1 is result2
