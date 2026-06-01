import io
import unittest.mock

import pytest
import torch

from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.models import Locale, Model, TTSConfig, TTSConfigModel, VoiceConfig
from src.tts.provider import SileroTTSModelProvider
from src.tts.result import TTSResult


class TestFactoryFunction:
    """Tests for direct SileroTTSEngine construction."""

    def test_returns_engine_instance(self):
        """Direct construction should return a SileroTTSEngine instance."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        config_model = TTSConfigModel(models={}, locales={})
        storage = SileroTTSYamlConfigStorage(config_model)
        provider = SileroTTSModelProvider()

        engine = SileroTTSEngine(config=config, storage=storage, provider=provider)

        assert isinstance(engine, SileroTTSEngine)

    def test_engine_has_provider(self):
        """Engine should have provider injected."""
        from src.tts.provider import SileroTTSModelProvider
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        config_model = TTSConfigModel(models={}, locales={})
        storage = SileroTTSYamlConfigStorage(config_model)
        provider = SileroTTSModelProvider()

        engine = SileroTTSEngine(config=config, storage=storage, provider=provider)

        assert hasattr(engine, "_provider")
        assert isinstance(engine._provider, SileroTTSModelProvider)


class TestProcessWithProvider:
    """Tests for process() using the provider instead of torch.hub.load."""

    @pytest.mark.asyncio
    async def test_process_uses_provider_for_model_path(self, tmp_path):
        """process() should call provider.get_model to resolve model path."""
        from src.tts.silero_tts_engine import SileroTTSEngine

        config = TTSConfig(
            device="cpu", sample_rate=48000, max_models=2, max_concurrent_per_model=2
        )
        model_config = Model(language="ru")
        locale_ru = Locale(
            voices={
                "silero-v5_5_ru-aidar": VoiceConfig(speaker="aidar", model="v5_5_ru", gender="male")
            }
        )
        config_model = TTSConfigModel(
            models={"v5_5_ru": model_config}, locales={"ru_RU": locale_ru}
        )

        mock_audio = torch.zeros(1, 48000)
        mock_model = unittest.mock.MagicMock()
        mock_model.apply_tts.return_value = mock_audio
        mock_importer = unittest.mock.MagicMock()
        mock_importer.load_pickle.return_value = mock_model

        provider_calls = []

        def capture_get_model(language, model_name):
            provider_calls.append((language, model_name))
            return (str(tmp_path / "model.pt"), [48000])

        mock_provider = unittest.mock.MagicMock()
        mock_provider.get_model.side_effect = capture_get_model

        with unittest.mock.patch(
            "src.tts.silero_tts_engine.SileroTTSModelProvider",
            return_value=mock_provider,
        ):
            with unittest.mock.patch(
                "src.tts.silero_tts_engine.torch.package.PackageImporter",
                return_value=mock_importer,
            ):
                storage = SileroTTSYamlConfigStorage(config_model)
                engine = SileroTTSEngine(config=config, storage=storage, provider=mock_provider)

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
