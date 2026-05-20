import pytest
import torch

from src.tts.exceptions import TTSProcessingError
from src.tts.provider import SileroTTSModelProvider


class TestGetModelCacheHit:
    """Tests for get_model() when model file already exists on disk."""

    def test_returns_local_path_and_sample_rates_when_model_exists(self, tmp_path):
        """get_model should return the full local path and sample rates when .pt file exists."""
        models_dir = tmp_path / ".models" / "silero"
        ru_dir = models_dir / "ru"
        ru_dir.mkdir(parents=True)

        model_file = ru_dir / "v5_5_ru.pt"
        model_file.write_bytes(b"fake model data")

        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n        sample_rate: [8000, 24000, 48000]\n"
        )

        provider = SileroTTSModelProvider(models_dir=models_dir)
        result = provider.get_model("ru", "v5_5_ru")

        assert result[0] == str(model_file)
        assert result[1] == [8000, 24000, 48000]

    def test_returns_path_for_any_language(self, tmp_path):
        """get_model should work for any language in the registry."""
        models_dir = tmp_path / ".models" / "silero"
        en_dir = models_dir / "en"
        en_dir.mkdir(parents=True)

        model_file = en_dir / "v3_en.pt"
        model_file.write_bytes(b"fake model data")

        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  en:\n    v3_en:\n      latest:\n        package: 'http://x'\n        sample_rate: [8000, 24000, 48000]\n"
        )

        provider = SileroTTSModelProvider(models_dir=models_dir)
        result = provider.get_model("en", "v3_en")

        assert result[0] == str(model_file)

    def test_creates_lang_dir_if_missing(self, tmp_path, monkeypatch):
        """get_model should create the language directory if missing."""
        import urllib.request

        models_dir = tmp_path / ".models" / "silero"

        def mock_urlretrieve(url: str, path: str):
            with open(path, "wb") as f:
                f.write(
                    b"tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n"
                )

        def mock_download(*a, **kw):
            raise RuntimeError("download failed")

        monkeypatch.setattr(urllib.request, "urlretrieve", mock_urlretrieve)
        monkeypatch.setattr(torch.hub, "download_url_to_file", mock_download)

        provider = SileroTTSModelProvider(models_dir=models_dir)

        with pytest.raises(TTSProcessingError):
            provider.get_model("ru", "v5_5_ru")

        assert models_dir.exists()


class TestGetModelModelsYmlDownload:
    """Tests for get_model() downloading models.yml from GitHub."""

    def test_downloads_models_yml_when_missing(self, tmp_path, monkeypatch):
        """get_model should download models.yml from GitHub when not on disk."""
        import urllib.request

        models_dir = tmp_path / ".models" / "silero"
        ru_dir = models_dir / "ru"
        ru_dir.mkdir(parents=True)

        yaml_content = b"""
tts_models:
  ru:
    v5_5_ru:
      latest:
        package: 'https://models.silero.ai/models/tts/ru/v5_5_ru.pt'
        sample_rate: [8000, 24000, 48000]
"""
        downloaded_urls = []

        def mock_urlretrieve(url: str, path: str):
            downloaded_urls.append(url)
            with open(path, "wb") as f:
                f.write(yaml_content)

        monkeypatch.setattr(urllib.request, "urlretrieve", mock_urlretrieve)

        provider = SileroTTSModelProvider(models_dir=models_dir)

        try:
            provider.get_model("ru", "v5_5_ru")
        except TTSProcessingError:
            pass

        assert len(downloaded_urls) == 1
        assert "models.yml" in downloaded_urls[0]
        assert (models_dir / "models.yml").exists()


class TestGetModelMalformedYml:
    """Tests for get_model() error handling."""

    def test_raises_on_malformed_models_yml(self, tmp_path, monkeypatch):
        """get_model should raise TTSProcessingError with delete hint for bad YAML."""
        import urllib.request

        models_dir = tmp_path / ".models" / "silero"
        models_dir.mkdir(parents=True)

        def mock_urlretrieve(url: str, path: str):
            with open(path, "wb") as f:
                f.write(b"tts_models:\n  invalid: [")

        monkeypatch.setattr(urllib.request, "urlretrieve", mock_urlretrieve)

        provider = SileroTTSModelProvider(models_dir=models_dir)

        with pytest.raises(TTSProcessingError) as exc_info:
            provider.get_model("ru", "v5_5_ru")

        assert "Failed to parse models.yml" in str(exc_info.value.message)
        assert "Delete" in str(exc_info.value.message)

    def test_raises_when_model_url_missing_from_registry(self, tmp_path, monkeypatch):
        """get_model should raise TTSProcessingError when model not in registry."""
        import urllib.request

        models_dir = tmp_path / ".models" / "silero"
        models_dir.mkdir(parents=True)

        def mock_urlretrieve(url: str, path: str):
            with open(path, "wb") as f:
                f.write(
                    b"tts_models:\n  ru:\n    other_model:\n      latest:\n        package: 'http://x'\n"
                )

        monkeypatch.setattr(urllib.request, "urlretrieve", mock_urlretrieve)

        provider = SileroTTSModelProvider(models_dir=models_dir)

        with pytest.raises(TTSProcessingError) as exc_info:
            provider.get_model("ru", "v5_5_ru")

        assert "v5_5_ru" in str(exc_info.value.message)
        assert "ru" in str(exc_info.value.message)
        assert "Delete" in str(exc_info.value.message)

    def test_wraps_download_runtime_error_in_tts_processing_error(self, tmp_path, monkeypatch):
        """Download failure should be wrapped in TTSProcessingError."""
        models_dir = tmp_path / ".models" / "silero"
        ru_dir = models_dir / "ru"
        ru_dir.mkdir(parents=True)

        (models_dir / "models.yml").write_bytes(
            b"tts_models:\n  ru:\n    v5_5_ru:\n      latest:\n        package: 'http://x'\n"
        )

        def mock_download(url: str, path: str, *a, **kw):
            raise RuntimeError("Connection reset")

        monkeypatch.setattr(torch.hub, "download_url_to_file", mock_download)

        provider = SileroTTSModelProvider(models_dir=models_dir)

        with pytest.raises(TTSProcessingError) as exc_info:
            provider.get_model("ru", "v5_5_ru")

        assert "Failed to download model" in str(exc_info.value.message)

    def test_raises_for_jit_only_model_without_package(self, tmp_path):
        """get_model should reject models that only have jit key (no package)."""
        models_dir = tmp_path / ".models" / "silero"
        ru_dir = models_dir / "ru"
        ru_dir.mkdir(parents=True)

        yaml_content = b"""
tts_models:
  ru:
    aidar_8khz:
      latest:
        jit: 'https://models.silero.ai/models/tts/ru/v1_aidar_8000.jit'
        sample_rate: 8000
"""
        (models_dir / "models.yml").write_bytes(yaml_content)

        provider = SileroTTSModelProvider(models_dir=models_dir)

        with pytest.raises(TTSProcessingError) as exc_info:
            provider.get_model("ru", "aidar_8khz")

        assert "aidar_8khz" in str(exc_info.value.message)


class TestGetModelDownload:
    """Tests for get_model() downloading .pt model files."""

    def test_downloads_model_directly_to_final_path(self, tmp_path, monkeypatch):
        """get_model should download .pt directly to final path (no temp file)."""
        models_dir = tmp_path / ".models" / "silero"
        ru_dir = models_dir / "ru"
        ru_dir.mkdir(parents=True)

        yaml_content = b"""
tts_models:
  ru:
    v5_5_ru:
      latest:
        package: 'https://models.silero.ai/models/tts/ru/v5_5_ru.pt'
        sample_rate: [8000, 24000, 48000]
"""
        (models_dir / "models.yml").write_bytes(yaml_content)

        download_calls = []

        def mock_download(url: str, path: str, *a, **kw):
            download_calls.append({"url": url, "path": path})
            with open(path, "wb") as f:
                f.write(b"fake model bytes")

        monkeypatch.setattr(torch.hub, "download_url_to_file", mock_download)

        provider = SileroTTSModelProvider(models_dir=models_dir)
        result = provider.get_model("ru", "v5_5_ru")

        assert result[0] == str(ru_dir / "v5_5_ru.pt")
        assert result[1] == [8000, 24000, 48000]

        assert len(download_calls) == 1
        assert download_calls[0]["url"] == "https://models.silero.ai/models/tts/ru/v5_5_ru.pt"
        assert download_calls[0]["path"] == str(ru_dir / "v5_5_ru.pt")

        assert (ru_dir / "v5_5_ru.pt").exists()
