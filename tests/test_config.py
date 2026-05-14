import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_has_all_tts_fields():
    """Test that Settings has all 5 required TTS_* fields with correct defaults."""
    settings = Settings.model_validate({})
    assert hasattr(settings, "TTS_DEVICE")
    assert hasattr(settings, "TTS_SAMPLE_RATE")
    assert hasattr(settings, "TTS_MAX_TEXT_LENGTH")
    assert hasattr(settings, "TTS_ALLOWED_ORIGINS")
    assert hasattr(settings, "TTS_SHUTDOWN_TIMEOUT")


def test_settings_tts_device_default():
    """Test that TTS_DEVICE defaults to 'cpu'."""
    settings = Settings.model_validate({})
    assert settings.TTS_DEVICE == "cpu"


def test_settings_sample_rate_default():
    """Test that TTS_SAMPLE_RATE defaults to 48000."""
    settings = Settings.model_validate({})
    assert settings.TTS_SAMPLE_RATE == 48000


def test_settings_max_text_length_default():
    """Test that TTS_MAX_TEXT_LENGTH defaults to 1000."""
    settings = Settings.model_validate({})
    assert settings.TTS_MAX_TEXT_LENGTH == 1000


def test_settings_allowed_origins_default():
    """Test that TTS_ALLOWED_ORIGINS defaults to '*'."""
    settings = Settings.model_validate({})
    assert settings.TTS_ALLOWED_ORIGINS == "*"


def test_settings_shutdown_timeout_default():
    """Test that TTS_SHUTDOWN_TIMEOUT defaults to 10."""
    settings = Settings.model_validate({})
    assert settings.TTS_SHUTDOWN_TIMEOUT == 10


def test_settings_tts_device_renamed():
    """Test that old tts_device name raises ValidationError (breaking change)."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"tts_device": "cpu"})


def test_invalid_sample_rate_fails():
    """Test that invalid TTS_SAMPLE_RATE values raise ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_SAMPLE_RATE": 44100})


def test_invalid_shutdown_timeout_zero_fails():
    """Test that TTS_SHUTDOWN_TIMEOUT=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_SHUTDOWN_TIMEOUT": 0})


def test_invalid_shutdown_timeout_negative_fails():
    """Test that negative TTS_SHUTDOWN_TIMEOUT raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_SHUTDOWN_TIMEOUT": -1})


def test_valid_sample_rates():
    """Test that all valid TTS_SAMPLE_RATE values are accepted."""
    for rate in [8000, 16000, 22050, 24000, 48000]:
        settings = Settings.model_validate({"TTS_SAMPLE_RATE": rate})
        assert settings.TTS_SAMPLE_RATE == rate


def test_valid_shutdown_timeout():
    """Test that valid TTS_SHUTDOWN_TIMEOUT values are accepted."""
    for timeout in [1, 5, 10, 30, 60]:
        settings = Settings.model_validate({"TTS_SHUTDOWN_TIMEOUT": timeout})
        assert settings.TTS_SHUTDOWN_TIMEOUT == timeout


def test_settings_has_all_seven_tts_fields():
    """Test that Settings has all 7 required TTS_* fields with correct defaults."""
    settings = Settings.model_validate({})
    assert hasattr(settings, "TTS_DEVICE")
    assert hasattr(settings, "TTS_SAMPLE_RATE")
    assert hasattr(settings, "TTS_MAX_TEXT_LENGTH")
    assert hasattr(settings, "TTS_ALLOWED_ORIGINS")
    assert hasattr(settings, "TTS_SHUTDOWN_TIMEOUT")
    assert hasattr(settings, "TTS_CONFIG_PATH")
    assert hasattr(settings, "TTS_MAX_CONCURRENT_PER_LOCALE")


def test_settings_config_path_default():
    """Test that TTS_CONFIG_PATH defaults to 'silero-to-mary-config.yml'."""
    settings = Settings.model_validate({})
    assert settings.TTS_CONFIG_PATH == "silero-to-mary-config.yml"


def test_settings_max_concurrent_default():
    """Test that TTS_MAX_CONCURRENT_PER_LOCALE defaults to 2."""
    settings = Settings.model_validate({})
    assert settings.TTS_MAX_CONCURRENT_PER_LOCALE == 2


def test_valid_max_concurrent_values():
    """Test that all valid TTS_MAX_CONCURRENT_PER_LOCALE values are accepted."""
    for val in [1, 5, 10]:
        settings = Settings.model_validate({"TTS_MAX_CONCURRENT_PER_LOCALE": val})
        assert settings.TTS_MAX_CONCURRENT_PER_LOCALE == val


def test_invalid_max_concurrent_zero_fails():
    """Test that TTS_MAX_CONCURRENT_PER_LOCALE=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_CONCURRENT_PER_LOCALE": 0})


def test_invalid_max_concurrent_negative_fails():
    """Test that negative TTS_MAX_CONCURRENT_PER_LOCALE raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_CONCURRENT_PER_LOCALE": -1})


def test_invalid_max_concurrent_above_range_fails():
    """Test that TTS_MAX_CONCURRENT_PER_LOCALE > 10 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_CONCURRENT_PER_LOCALE": 11})


def test_invalid_config_path_nonexistent_fails(tmp_path):
    """Test that non-existent TTS_CONFIG_PATH raises ValidationError."""
    nonexistent = str(tmp_path / "nonexistent.yml")
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_CONFIG_PATH": nonexistent})
