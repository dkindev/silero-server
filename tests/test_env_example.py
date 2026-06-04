def test_env_example_has_all_tts_vars():
    """Test that .env.example contains all TTS_* variables with example values."""
    with open(".env.example") as f:
        content = f.read()

    required_vars = [
        "TTS_TORCH_DEVICE",
        "TTS_TORCH_NUM_THREADS",
        "TTS_TORCH_NUM_INTEROP_THREADS",
        "TTS_TORCH_FLUSH_DENORMAL",
        "TTS_SAMPLE_RATE",
        "TTS_MAX_TEXT_LENGTH",
        "TTS_ALLOWED_ORIGINS",
        "TTS_CONFIG_PATH",
        "TTS_MAX_MODELS",
        "TTS_MAX_CONCURRENT_PER_MODEL",
        "TTS_MODELS_DIR",
    ]
    for var in required_vars:
        assert var in content, f".env.example missing {var}"
