import unittest.mock

import pytest
import torch

from src.tts.models import TTSConfig

# ---------------------------------------------------------------------------
# Fixtures — shared by all test files
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_model():
    """Return a MagicMock Silero model with symbols and apply_tts."""
    mock_audio = torch.zeros(1, 48000)
    m = unittest.mock.MagicMock()
    m.symbols = "_.!,-:;?abcdefghijklmnopqrstuvwxyz "
    m.apply_tts.return_value = mock_audio
    return m


@pytest.fixture
def mock_importer(mock_model):
    """Return a MagicMock PackageImporter that returns mock_model."""
    imp = unittest.mock.MagicMock()
    imp.load_pickle.return_value = mock_model
    return imp


@pytest.fixture
def default_tts_config():
    """Return a TTSConfig with sensible defaults for testing."""
    return TTSConfig(
        device="cpu",
        sample_rate=48000,
        max_models=2,
        max_concurrent_per_model=2,
        max_chunk_chars=48000,
        models_dir=".models/silero",
        models_yml_url="https://example.com/models.yml",
        models_yml_hash="",
    )


@pytest.fixture
def mock_package_importer(mock_importer):
    """Patch torch.package.PackageImporter to return mock_importer."""
    with unittest.mock.patch(
        "src.tts.engine.torch.package.PackageImporter",
        return_value=mock_importer,
    ):
        yield
