from dataclasses import FrozenInstanceError

import pytest

from src.tts.exceptions import (
    InvalidInputTypeError,
    InvalidLocaleError,
    InvalidOutputTypeError,
    InvalidVoiceError,
    TTSEngineError,
    TTSProcessingError,
)
from src.tts.models import Locale, Model, TTSConfigModel, VoiceConfig
from src.tts.result import TTSResult


class TestModel:
    def test_model_has_language_field(self):
        """Model dataclass has language field."""
        model = Model(language="en")
        assert model.language == "en"

    def test_model_is_frozen(self):
        """Model dataclass is immutable (frozen)."""
        model = Model(language="en")
        with pytest.raises(FrozenInstanceError):
            model.language = "fr"


class TestVoiceConfig:
    def test_voice_config_has_all_fields(self):
        """VoiceConfig dataclass has speaker, model, gender fields."""
        vc = VoiceConfig(speaker="en_0", model="v3_en", gender="male")
        assert vc.speaker == "en_0"
        assert vc.model == "v3_en"
        assert vc.gender == "male"

    def test_voice_config_is_frozen(self):
        """VoiceConfig dataclass is immutable (frozen)."""
        vc = VoiceConfig(speaker="en_0", model="v3_en", gender="male")
        with pytest.raises(FrozenInstanceError):
            vc.speaker = "en_1"


class TestLocale:
    def test_locale_has_voices_dict(self):
        """Locale dataclass has voices dict field."""
        voices = {"silero-v3_en-en_0": VoiceConfig(speaker="en_0", model="v3_en", gender="male")}
        locale = Locale(voices=voices)
        assert locale.voices == voices

    def test_locale_is_frozen(self):
        """Locale dataclass is immutable (frozen)."""
        locale = Locale(voices={})
        with pytest.raises(FrozenInstanceError):
            locale.voices = {}


class TestTTSConfigModel:
    def test_tts_config_model_has_models_and_locales(self):
        """TTSConfigModel dataclass has models and locales dicts."""
        models = {"v3_en": Model(language="en")}
        locales = {"en_US": Locale(voices={})}
        config = TTSConfigModel(models=models, locales=locales)
        assert config.models == models
        assert config.locales == locales

    def test_tts_config_model_is_frozen(self):
        """TTSConfigModel dataclass is immutable (frozen)."""
        config = TTSConfigModel(models={}, locales={})
        with pytest.raises(FrozenInstanceError):
            config.models = {}


class TestExceptions:
    def test_tts_engine_error_base(self):
        """TTSEngineError can be raised with message."""
        err = TTSEngineError("test error")
        assert err.message == "test error"
        assert str(err) == "test error"

    def test_tts_engine_error_with_locale_and_voice(self):
        """TTSEngineError accepts optional locale and voice."""
        err = TTSEngineError("invalid locale", locale="en_XX", voice="voice1")
        assert err.locale == "en_XX"
        assert err.voice == "voice1"

    def test_invalid_locale_error_is_tts_engine_error(self):
        """InvalidLocaleError inherits from TTSEngineError."""
        err = InvalidLocaleError("Locale not found", locale="en_XX")
        assert isinstance(err, TTSEngineError)
        assert err.status_code == 400

    def test_invalid_voice_error_has_400_status(self):
        """InvalidVoiceError has status code 400."""
        err = InvalidVoiceError("Voice not found", locale="en_US", voice="invalid")
        assert err.status_code == 400

    def test_invalid_input_type_error_has_400_status(self):
        """InvalidInputTypeError has status code 400."""
        err = InvalidInputTypeError("Invalid input type")
        assert err.status_code == 400

    def test_invalid_output_type_error_has_406_status(self):
        """InvalidOutputTypeError has status code 406."""
        err = InvalidOutputTypeError("Invalid output type")
        assert err.status_code == 406

    def test_tts_processing_error_has_500_status(self):
        """TTSProcessingError has status code 500."""
        err = TTSProcessingError("Processing failed")
        assert err.status_code == 500


class TestTTSResult:
    def test_tts_result_has_audio_sample_rate_model(self):
        """TTSResult dataclass has audio, sample_rate, model fields."""
        audio = b"RIFF\x00\x00\x00WAVE"
        result = TTSResult(audio=audio, sample_rate=48000, model="v3_en")
        assert result.audio == audio
        assert result.sample_rate == 48000
        assert result.model == "v3_en"

    def test_tts_result_is_mutable(self):
        """TTSResult dataclass is mutable (not frozen)."""
        result = TTSResult(audio=b"test", sample_rate=24000, model="v3_en")
        result.sample_rate = 48000
        assert result.sample_rate == 48000
