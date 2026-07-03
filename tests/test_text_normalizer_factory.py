import pytest

from src.config import (
    NormalizationPromt,
    NormalizationSettings,
    SsmlNormalizationSettings,
    TextNormalizationSettings,
)
from src.tts.models import NormalizationType, TextFormat
from src.tts.preprocessing import (
    OpenAiTextNormalizer,
    PlainTextNormalizer,
    SsmlNormalizer,
    TextNormalizerFactory,
)
from tests.helpers import make_voice


class TestTextNormalizerFactory:
    """Tests for TextNormalizerFactory.create_text_normalizer behavior."""

    def test_text_simple_returns_plain_text_normalizer(
        self, default_normalization_settings, mock_openai_client
    ):
        factory = TextNormalizerFactory(
            openai_client=mock_openai_client, settings=default_normalization_settings
        )
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.TEXT)
        assert isinstance(result, PlainTextNormalizer)

    def test_ssml_simple_returns_ssml_normalizer(self, mock_openai_client):
        settings = NormalizationSettings(
            ssml=SsmlNormalizationSettings(enabled=True),
        )
        factory = TextNormalizerFactory(openai_client=mock_openai_client, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.SSML)
        assert isinstance(result, SsmlNormalizer)

    def test_text_llm_returns_openai_normalizer(self, mock_openai_client):
        settings = NormalizationSettings(
            text=TextNormalizationSettings(
                type=NormalizationType.LLM,
                promts={
                    "ru_RU": NormalizationPromt(text="normalize", model="gpt-4o-mini"),
                },
            ),
        )
        factory = TextNormalizerFactory(openai_client=mock_openai_client, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.TEXT)
        assert isinstance(result, OpenAiTextNormalizer)

    def test_text_llm_no_prompt_returns_none(self, mock_openai_client):
        settings = NormalizationSettings(
            text=TextNormalizationSettings(
                type=NormalizationType.LLM,
                promts={},
            ),
        )
        factory = TextNormalizerFactory(openai_client=mock_openai_client, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.TEXT)
        assert result is None

    def test_text_llm_no_client_returns_none(self, default_normalization_settings):
        settings = NormalizationSettings(
            text=TextNormalizationSettings(
                type=NormalizationType.LLM,
                promts={
                    "ru_RU": NormalizationPromt(text="normalize", model="gpt-4o-mini"),
                },
            ),
        )
        factory = TextNormalizerFactory(openai_client=None, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.TEXT)
        assert result is None

    def test_raises_type_error_for_none_voice(
        self, default_normalization_settings, mock_openai_client
    ):
        factory = TextNormalizerFactory(
            openai_client=mock_openai_client, settings=default_normalization_settings
        )
        with pytest.raises(TypeError):
            factory.create_text_normalizer(voice=None, format=TextFormat.TEXT)

    def test_text_normalization_disabled_returns_none(self, mock_openai_client):
        settings = NormalizationSettings(
            text=TextNormalizationSettings(enabled=False),
        )
        factory = TextNormalizerFactory(openai_client=mock_openai_client, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.TEXT)
        assert result is None

    def test_ssml_normalization_disabled_returns_none(self, mock_openai_client):
        settings = NormalizationSettings(
            ssml=SsmlNormalizationSettings(enabled=False),
        )
        factory = TextNormalizerFactory(openai_client=mock_openai_client, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.SSML)
        assert result is None

    def test_llm_with_none_promts_returns_none(self, mock_openai_client):
        settings = NormalizationSettings(
            text=TextNormalizationSettings(
                type=NormalizationType.LLM,
                promts=None,
            ),
        )
        factory = TextNormalizerFactory(openai_client=None, settings=settings)
        voice = make_voice(voice_id="v1", name="Test", locale="ru_RU")
        result = factory.create_text_normalizer(voice=voice, format=TextFormat.TEXT)
        assert result is None
