from src.tts.models import Locale, TTSConfig, TTSConfigModel, VoiceConfig


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
