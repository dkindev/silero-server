import pytest

from src.tts.models import NormalizationOptions
from src.tts.preprocessing.text_normalizer import PlainTextNormalizer, SsmlNormalizer


class TestPlainTextNormalizer:
    """Tests for PlainTextNormalizer.normalize_text behavior."""

    async def test_normalizes_text_with_all_available_chars(self, normalization_options):
        normalizer = PlainTextNormalizer()
        chunks = ["hello world"]
        result = [
            chunk async for chunk in normalizer.normalize_text(iter(chunks), normalization_options)
        ]
        assert result == ["hello world"]

    async def test_filters_unavailable_characters(self, normalization_options):
        normalizer = PlainTextNormalizer()
        chunks = ["hello @#$ world"]
        result = [
            chunk async for chunk in normalizer.normalize_text(iter(chunks), normalization_options)
        ]
        assert result == ["hello  world"]

    async def test_skips_empty_chunks(self, normalization_options):
        normalizer = PlainTextNormalizer()
        chunks = ["  ", "hello"]
        result = [
            chunk async for chunk in normalizer.normalize_text(iter(chunks), normalization_options)
        ]
        assert result == ["hello"]

    async def test_no_filter_when_silero_model_is_none(self, normalization_options):
        normalizer = PlainTextNormalizer()
        options = NormalizationOptions(
            voice=normalization_options.voice,
            model=normalization_options.model,
            silero_model=None,
        )
        chunks = ["hello @#$ world"]
        result = [chunk async for chunk in normalizer.normalize_text(iter(chunks), options)]
        assert result == ["hello @#$ world"]

    async def test_no_filter_when_model_lacks_symbols(self, normalization_options):
        normalizer = PlainTextNormalizer()
        options = NormalizationOptions(
            voice=normalization_options.voice,
            model=normalization_options.model,
            silero_model=object(),
        )
        chunks = ["hello @#$ world"]
        result = [chunk async for chunk in normalizer.normalize_text(iter(chunks), options)]
        assert result == ["hello @#$ world"]

    async def test_filters_all_chars_when_symbols_empty(self, normalization_options):
        normalizer = PlainTextNormalizer()
        options = NormalizationOptions(
            voice=normalization_options.voice,
            model=normalization_options.model,
            silero_model=type("MockModel", (), {"symbols": ""})(),
        )
        chunks = ["hello world"]
        result = [chunk async for chunk in normalizer.normalize_text(iter(chunks), options)]
        assert result == [" "]

    async def test_raises_type_error_for_none_chunks(self, normalization_options):
        normalizer = PlainTextNormalizer()
        with pytest.raises(TypeError):
            async for _ in normalizer.normalize_text(None, normalization_options):
                pass

    async def test_filtering_is_case_insensitive(self, normalization_options):
        normalizer = PlainTextNormalizer()
        chunks = ["HELLO World"]
        result = [
            chunk async for chunk in normalizer.normalize_text(iter(chunks), normalization_options)
        ]
        assert result == ["HELLO World"]


class TestSsmlNormalizer:
    """Tests for SsmlNormalizer.normalize_text behavior."""

    async def test_preserves_ssml_structure(self, normalization_options):
        normalizer = SsmlNormalizer()
        chunks = ["  <speak>hello world</speak>  "]
        result = [
            chunk async for chunk in normalizer.normalize_text(iter(chunks), normalization_options)
        ]
        assert result == ["<speak>hello world</speak>"]

    async def test_skips_empty_chunks(self, normalization_options):
        normalizer = SsmlNormalizer()
        chunks = ["  ", "<speak>hello</speak>"]
        result = [
            chunk async for chunk in normalizer.normalize_text(iter(chunks), normalization_options)
        ]
        assert result == ["<speak>hello</speak>"]

    async def test_raises_type_error_for_none_chunks(self, normalization_options):
        normalizer = SsmlNormalizer()
        with pytest.raises(TypeError):
            async for _ in normalizer.normalize_text(None, normalization_options):
                pass
