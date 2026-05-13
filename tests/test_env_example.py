def test_env_example_has_all_tts_vars():
    """Test that .env.example contains all 5 TTS_* variables with example values."""
    with open(".env.example") as f:
        content = f.read()

    required_vars = [
        "TTS_DEVICE",
        "TTS_SAMPLE_RATE",
        "TTS_MAX_TEXT_LENGTH",
        "TTS_ALLOWED_ORIGINS",
        "TTS_SHUTDOWN_TIMEOUT",
    ]
    for var in required_vars:
        assert var in content, f".env.example missing {var}"
