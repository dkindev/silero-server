from dataclasses import FrozenInstanceError

import pytest

from src.tts.exceptions import TTSEngineError
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

    def test_tts_result_is_mutable(self):
        """TTSResult dataclass is mutable (not frozen)."""
        result = TTSResult(audio=b"test", sample_rate=24000, model="v3_en")
        result.sample_rate = 48000
        assert result.sample_rate == 48000
