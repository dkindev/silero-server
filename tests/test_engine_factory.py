import io
import unittest.mock

import pytest
import torch

from src.tts.exceptions import TTSEngineError
from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, VoiceConfig
from src.tts.result import TTSResult


class TestFactoryFunction:
    """Tests for create_silero_engine() factory function."""

    def test_returns_engine_instance(self):
        """create_silero_engine should return a SileroTTSEngine instance."""
        from src.tts.silero_tts_engine import SileroTTSEngine, create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = create_silero_engine(config, config_model)

        assert isinstance(engine, SileroTTSEngine)

    def test_engine_has_provider(self):
        """Engine created by factory should have provider injected."""
        from src.tts.provider import SileroTTSModelProvider
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        config_model = TTSConfigModel(models={}, locales={})

        engine = create_silero_engine(config, config_model)

        assert hasattr(engine, "_provider")
        assert isinstance(engine._provider, SileroTTSModelProvider)


class TestLoadModelWithPackageImporter:
    """Tests for _load_model() using torch.package.PackageImporter."""

    def test_load_model_uses_package_importer(self, tmp_path):
        """_load_model should load via torch.package.PackageImporter."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_model = unittest.mock.MagicMock()
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter"
        ) as mock_pkg_class:
            mock_pkg_class.return_value = mock_importer

            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(tmp_path / "model.pt"), [48000])
            ):
                cached = engine._load_model("v5_5_ru", model_config)

        mock_pkg_class.assert_called_once_with(str(tmp_path / "model.pt"))
        mock_importer.load_pickle.assert_called_once_with("tts_models", "model")
        assert cached.model is mock_model
        assert cached.sample_rate == 48000

    def test_load_model_raises_tts_processing_error_on_corrupt_file(self, tmp_path):
        """Corrupt .pt file should raise TTSEngineError on load."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        model_path = tmp_path / "corrupt.pt"
        model_path.write_bytes(b"corrupt data")

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter"
        ) as mock_pkg_class:
            mock_pkg_class.side_effect = RuntimeError("Invalid package")

            with unittest.mock.patch.object(
                engine._provider, "get_model", return_value=(str(model_path), [48000])
            ):
                with pytest.raises(TTSEngineError):
                    engine._load_model("v5_5_ru", model_config)

        assert model_path.exists()


class TestProcessWithProvider:
    """Tests for process() using the provider instead of torch.hub.load."""

    @pytest.mark.asyncio
    async def test_process_uses_provider_for_model_path(self, tmp_path):
        """process() should call provider.get_model to resolve model path."""
        from src.tts.silero_tts_engine import create_silero_engine

        config = TTSConfig(device="cpu", sample_rate=48000, max_concurrent_per_model=2)
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        engine = create_silero_engine(config, config_model)

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        provider_calls = []

        def capture_get_model(language, model_name):
            provider_calls.append((language, model_name))
            return (str(tmp_path / "model.pt"), [48000])

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.torch.package.PackageImporter",
            return_value=mock_importer,
        ):
            with unittest.mock.patch.object(
                engine._provider, "get_model", side_effect=capture_get_model
            ):
                result = await engine.process(
                    text="hello",
                    locale="ru_RU",
                    voice="silero-v5_5_ru-aidar",
                    input_type="TEXT",
                )

        assert ("ru", "v5_5_ru") in provider_calls
        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, io.BytesIO)
        assert result.audio.read().startswith(b"RIFF")
