import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_tts_torch_device_default():
    """Test that TTS_TORCH_DEVICE defaults to 'cpu'."""
    settings = Settings.model_validate({})
    assert settings.TTS_TORCH_DEVICE == "cpu"


def test_settings_tts_torch_num_threads_default():
    """Test that TTS_TORCH_NUM_THREADS defaults to 4."""
    settings = Settings.model_validate({})
    assert settings.TTS_TORCH_NUM_THREADS == 4


def test_settings_tts_torch_num_interop_threads_default():
    """Test that TTS_TORCH_NUM_INTEROP_THREADS defaults to 1."""
    settings = Settings.model_validate({})
    assert settings.TTS_TORCH_NUM_INTEROP_THREADS == 1


def test_settings_tts_torch_flush_denormal_default():
    """Test that TTS_TORCH_FLUSH_DENORMAL defaults to True."""
    settings = Settings.model_validate({})
    assert settings.TTS_TORCH_FLUSH_DENORMAL is True


def test_tts_torch_num_threads_zero_fails():
    """Test that TTS_TORCH_NUM_THREADS=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_TORCH_NUM_THREADS": 0})


def test_tts_torch_num_interop_threads_zero_fails():
    """Test that TTS_TORCH_NUM_INTEROP_THREADS=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_TORCH_NUM_INTEROP_THREADS": 0})


def test_settings_tts_models_dir_default():
    """Test that TTS_MODELS_DIR defaults to '.models/silero'."""
    settings = Settings.model_validate({})
    assert settings.TTS_MODELS_DIR == ".models/silero"


def test_settings_has_all_tts_fields():
    """Test that Settings has all TTS_* fields with correct defaults."""
    settings = Settings.model_validate({})
    assert hasattr(settings, "TTS_TORCH_DEVICE")
    assert hasattr(settings, "TTS_TORCH_NUM_THREADS")
    assert hasattr(settings, "TTS_TORCH_NUM_INTEROP_THREADS")
    assert hasattr(settings, "TTS_TORCH_FLUSH_DENORMAL")
    assert hasattr(settings, "TTS_SAMPLE_RATE")
    assert hasattr(settings, "TTS_MAX_TEXT_LENGTH")
    assert hasattr(settings, "TTS_ALLOWED_ORIGINS")
    assert hasattr(settings, "TTS_SHUTDOWN_TIMEOUT")
    assert hasattr(settings, "TTS_CONFIG_PATH")
    assert hasattr(settings, "TTS_MAX_MODELS")
    assert hasattr(settings, "TTS_MAX_CONCURRENT_PER_MODEL")
    assert hasattr(settings, "TTS_MODELS_DIR")


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


def test_settings_config_path_default():
    """Test that TTS_CONFIG_PATH defaults to 'silero-to-mary-config.yml'."""
    settings = Settings.model_validate({})
    assert settings.TTS_CONFIG_PATH == "silero-to-mary-config.yml"


def test_settings_max_concurrent_default():
    """Test that TTS_MAX_CONCURRENT_PER_MODEL defaults to 2."""
    settings = Settings.model_validate({})
    assert settings.TTS_MAX_CONCURRENT_PER_MODEL == 2


def test_valid_max_concurrent_values():
    """Test that all valid TTS_MAX_CONCURRENT_PER_MODEL values are accepted."""
    for val in [1, 5, 10]:
        settings = Settings.model_validate({"TTS_MAX_CONCURRENT_PER_MODEL": val})
        assert settings.TTS_MAX_CONCURRENT_PER_MODEL == val


def test_invalid_max_concurrent_zero_fails():
    """Test that TTS_MAX_CONCURRENT_PER_MODEL=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_CONCURRENT_PER_MODEL": 0})


def test_invalid_max_concurrent_negative_fails():
    """Test that negative TTS_MAX_CONCURRENT_PER_MODEL raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_CONCURRENT_PER_MODEL": -1})


def test_invalid_max_concurrent_above_range_fails():
    """Test that TTS_MAX_CONCURRENT_PER_MODEL > 10 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_CONCURRENT_PER_MODEL": 11})


def test_invalid_config_path_nonexistent_fails(tmp_path):
    """Test that non-existent TTS_CONFIG_PATH raises ValidationError."""
    nonexistent = str(tmp_path / "nonexistent.yml")
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_CONFIG_PATH": nonexistent})


def test_settings_max_models_default():
    """Test that TTS_MAX_MODELS defaults to 2."""
    settings = Settings.model_validate({})
    assert settings.TTS_MAX_MODELS == 2


def test_valid_max_models_values():
    """Test that valid TTS_MAX_MODELS values are accepted."""
    for val in [1, 5, 20, 100]:
        settings = Settings.model_validate({"TTS_MAX_MODELS": val})
        assert settings.TTS_MAX_MODELS == val


def test_invalid_max_models_zero_fails():
    """Test that TTS_MAX_MODELS=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_MODELS": 0})


def test_invalid_max_models_negative_fails():
    """Test that negative TTS_MAX_MODELS raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_MAX_MODELS": -1})


def test_valid_device_values():
    """Test that all valid TTS_TORCH_DEVICE values are accepted."""
    for device in ["cpu", "cuda", "xpu"]:
        settings = Settings.model_validate({"TTS_TORCH_DEVICE": device})
        assert settings.TTS_TORCH_DEVICE == device


def test_valid_device_case_insensitive():
    """Test that TTS_TORCH_DEVICE is case-insensitive."""
    for device, expected in [("CPU", "cpu"), ("CUDA", "cuda"), ("XPU", "xpu")]:
        settings = Settings.model_validate({"TTS_TORCH_DEVICE": device})
        assert settings.TTS_TORCH_DEVICE == expected


def test_invalid_device_value_fails():
    """Test that invalid TTS_TORCH_DEVICE value raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings.model_validate({"TTS_TORCH_DEVICE": "vulkan"})


def test_get_settings_importable_from_config():
    """Test that get_settings can be imported from src.config."""
    from src.config import get_settings

    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_settings_is_cached():
    """Test that get_settings returns the same cached instance."""
    from src.config import get_settings

    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
