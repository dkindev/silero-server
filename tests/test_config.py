from pydantic_settings import YamlConfigSettingsSource

from src.config import Settings


class TestTtsStreaming:
    def test_default_is_true(self):
        """streaming defaults to True (enabled)."""
        settings = Settings()
        assert settings.streaming is True

    def test_env_var_disables_streaming(self, monkeypatch):
        """TTS_STREAMING=false sets streaming to False."""
        monkeypatch.setenv("TTS_STREAMING", "false")
        settings = Settings()
        assert settings.streaming is False

    def test_cli_flag_no_streaming_disables(self, monkeypatch):
        """--no-streaming CLI flag sets streaming to False."""
        monkeypatch.setattr("sys.argv", ["prog", "--no-streaming"])
        settings = Settings()
        assert settings.streaming is False

    def test_cli_flag_streaming_enables(self, monkeypatch):
        """--streaming CLI flag sets streaming to True."""
        monkeypatch.setattr("sys.argv", ["prog", "--streaming"])
        settings = Settings()
        assert settings.streaming is True


class TestTtsUri:
    def test_default_uri(self):
        """uri defaults to tcp://127.0.0.1:10200 (from Field default and config.yml)."""
        settings = Settings()
        assert settings.uri == "tcp://127.0.0.1:10200"

    def test_uri_from_env_var(self, monkeypatch):
        """uri is overridable via TTS_URI environment variable."""
        monkeypatch.setenv("TTS_URI", "tcp://0.0.0.0:10201")
        settings = Settings()
        assert settings.uri == "tcp://0.0.0.0:10201"


class TestTtsZeroconf:
    def test_zeroconf_defaults_to_silero(self):
        """zeroconf defaults to 'silero-tts' (enabled)."""
        settings = Settings()
        assert settings.zeroconf == "silero-tts"

    def test_zeroconf_silero_is_truthy(self):
        """Non-empty zeroconf evaluates as truthy (enabled)."""
        settings = Settings()
        assert settings.zeroconf

    def test_zeroconf_from_env_var(self, monkeypatch):
        """zeroconf is overridable via TTS_ZEROCONF environment variable."""
        monkeypatch.setenv("TTS_ZEROCONF", "my_tts")
        settings = Settings()
        assert settings.zeroconf == "my_tts"


class TestYamlConfigSource:
    def test_config_yml_overrides_defaults(self):
        """config.yml values take priority over Field defaults."""
        settings = Settings()
        assert settings.env_type == "development"
        assert settings.torch.device == "cpu"
        assert settings.torch.num_threads == 4
        assert settings.sample_rate == 48000
        assert settings.max_models == 2

    def test_yaml_source_is_in_priority_chain(self):
        """YamlConfigSettingsSource is present in the priority chain."""
        sources = Settings.settings_customise_sources(Settings, None, None, None, None)
        assert any(
            issubclass(s, YamlConfigSettingsSource)
            if isinstance(s, type)
            else isinstance(s, YamlConfigSettingsSource)
            for s in sources
        )
