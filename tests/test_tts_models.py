from dataclasses import FrozenInstanceError

import pytest

from src.tts.exceptions import TTSEngineError
from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, TTSResult, VoiceConfig


class TestModel:
    def test_model_has_name_and_language_fields(self):
        """Model dataclass has name and language fields."""
        model = Model(name="test_model", language="en")
        assert model.name == "test_model"
        assert model.language == "en"

    def test_model_warmup_defaults_to_false(self):
        """Model.warmup defaults to False."""
        model = Model(name="test_model", language="en")
        assert model.warmup is False

    def test_model_warmup_can_be_set_to_true(self):
        """Model(language, warmup=True) sets warmup to True."""
        model = Model(name="test_model", language="en", warmup=True)
        assert model.warmup is True

    def test_model_is_frozen(self):
        """Model dataclass is immutable (frozen)."""
        model = Model(name="test_model", language="en")
        with pytest.raises(FrozenInstanceError):
            model.language = "fr"


class TestVoiceConfig:
    def test_voice_config_has_all_fields(self):
        """VoiceConfig dataclass has voice_name, speaker, model, gender, locale fields."""
        vc = VoiceConfig(
            voice_name="silero-v3_en-en_0",
            speaker="en_0",
            model="v3_en",
            gender="male",
            locale="en_US",
        )
        assert vc.voice_name == "silero-v3_en-en_0"
        assert vc.speaker == "en_0"
        assert vc.model == "v3_en"
        assert vc.gender == "male"
        assert vc.locale == "en_US"

    def test_voice_config_is_frozen(self):
        """VoiceConfig dataclass is immutable (frozen)."""
        vc = VoiceConfig(
            voice_name="silero-v3_en-en_0",
            speaker="en_0",
            model="v3_en",
            gender="male",
            locale="en_US",
        )
        with pytest.raises(FrozenInstanceError):
            vc.speaker = "en_1"


class TestLocale:
    def test_locale_has_name_field(self):
        """Locale dataclass has name field."""
        locale = Locale(name="en_US")
        assert locale.name == "en_US"

    def test_locale_is_frozen(self):
        """Locale dataclass is immutable (frozen)."""
        locale = Locale(name="en_US")
        with pytest.raises(FrozenInstanceError):
            locale.name = "ru_RU"


class TestTTSConfigModel:
    def test_tts_config_model_has_models_locales_and_voices(self):
        """TTSConfigModel dataclass has models list, locales list, voices list."""
        models = [Model(name="v3_en", language="en")]
        locales = [Locale(name="en_US")]
        voices = [
            VoiceConfig(
                voice_name="silero-v3_en-en_0",
                speaker="en_0",
                model="v3_en",
                gender="male",
                locale="en_US",
            )
        ]
        config = TTSConfigModel(models=models, locales=locales, voices=voices)
        assert config.models == models
        assert config.locales == locales
        assert config.voices == voices

    def test_tts_config_model_is_frozen(self):
        """TTSConfigModel dataclass is immutable (frozen)."""
        config = TTSConfigModel(models=[], locales=[], voices=[])
        with pytest.raises(FrozenInstanceError):
            config.models = []


class TestTTSConfig:
    def test_tts_config_has_max_models_field(self):
        """TTSConfig dataclass has max_models field."""
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=5,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=None,
        )
        assert config.max_models == 5

    def test_tts_config_accepts_models_yml_url_and_hash(self):
        """TTSConfig accepts models_yml_url and models_yml_hash."""
        from src.config import Settings

        settings = Settings.model_validate({})
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url=settings.TTS_MODELS_YML_URL,
            models_yml_hash=settings.TTS_MODELS_YML_HASH,
        )
        assert config.models_yml_url == settings.TTS_MODELS_YML_URL
        assert config.models_yml_hash == settings.TTS_MODELS_YML_HASH

    def test_tts_config_models_yml_hash_accepts_none(self):
        """TTSConfig.models_yml_hash accepts None (skip validation)."""
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=None,
        )
        assert config.models_yml_hash is None

    def test_tts_config_is_frozen(self):
        """TTSConfig dataclass is immutable (frozen)."""
        config = TTSConfig(
            device="cpu",
            sample_rate=48000,
            max_models=2,
            max_concurrent_per_model=2,
            max_chunk_chars=48000,
            models_dir=".models/silero",
            models_yml_url="https://example.com/models.yml",
            models_yml_hash=None,
        )
        with pytest.raises(FrozenInstanceError):
            config.max_models = 3


class TestExceptions:
    def test_tts_engine_error_message_only(self):
        """TTSEngineError accepts only message — no locale/voice/status_code."""
        err = TTSEngineError("test error")
        assert str(err) == "test error"
        assert not hasattr(err, "locale")
        assert not hasattr(err, "voice")
        assert not hasattr(err, "status_code")


class TestTTSResult:
    def test_tts_result_has_audio_sample_rate_model(self):
        """TTSResult dataclass has audio, sample_rate, model fields."""
        audio = b"RIFF\x00\x00\x00WAVE"
        result = TTSResult(audio=audio, sample_rate=48000, model="v3_en")
        assert result.audio == audio
        assert result.sample_rate == 48000
        assert result.model == "v3_en"
