from pydantic_settings import YamlConfigSettingsSource

from src.config import Settings


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
        """zeroconf defaults to 'silero' (enabled)."""
        settings = Settings()
        assert settings.zeroconf == "silero"

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
        assert settings.tts.sample_rate == 48000
        assert settings.tts.max_models == 2

    def test_yaml_source_is_in_priority_chain(self):
        """YamlConfigSettingsSource is present in the priority chain."""
        sources = Settings.settings_customise_sources(Settings, None, None, None, None)
        assert any(
            issubclass(s, YamlConfigSettingsSource)
            if isinstance(s, type)
            else isinstance(s, YamlConfigSettingsSource)
            for s in sources
        )
