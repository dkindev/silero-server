from collections.abc import Callable

from loguru import logger
from openai import AsyncOpenAI

from src.config import BaseNormalizationSettings, NormalizationSettings
from src.tts.models import OpenAiNormalizationConfig, TextFormat, Voice
from src.tts.preprocessing import (
    OpenAiTextNormalizer,
    PlainTextNormalizer,
    SsmlNormalizer,
    TextNormalizer,
)


class TextNormalizerFactory:
    def __init__(self, openai_client: AsyncOpenAI, settings: NormalizationSettings):
        self._settings = settings

        def _create_openai_normalizer(
            voice: Voice, settings: BaseNormalizationSettings
        ) -> TextNormalizer:
            if openai_client is None:
                return None

            if settings.promts is None:
                return None

            default_promt = settings.promts.get(voice.locale)
            if default_promt is None:
                return None

            return OpenAiTextNormalizer(
                client=openai_client,
                config=OpenAiNormalizationConfig(
                    timeout=self._settings.timeout,
                    max_concurrent_chunks_per_request=self._settings.max_concurrent_chunks_per_request,
                    default_model=default_promt.model,
                    default_promt=default_promt.text,
                ),
            )

        self._builders: dict[str, Callable[[Voice, BaseNormalizationSettings], TextNormalizer]] = {
            # key: "{locale}__{text_format}__{normalization_type}"
            "default__text__simple": lambda v, s: PlainTextNormalizer(),
            "default__ssml__simple": lambda v, s: SsmlNormalizer(),
            "default__text__llm": _create_openai_normalizer,
            "default__ssml__llm": _create_openai_normalizer,
        }

        self._factories: dict[str, Callable[[Voice, TextFormat], TextNormalizer]] = {
            # key: "{locale}__{text_format}"
            "default__text": self._create_text_normalizer_factory,
            "default__ssml": self._create_ssml_normalizer_factory,
        }

    def _create_text_normalizer_factory(self, voice: Voice, format: TextFormat) -> TextNormalizer:
        settings = self._settings.text
        if not settings.enabled:
            return None

        return self._create_text_normalizer(voice=voice, format=format, settings=settings)

    def _create_ssml_normalizer_factory(self, voice: Voice, format: TextFormat) -> TextNormalizer:
        settings = self._settings.ssml
        if not settings.enabled:
            return None

        return self._create_text_normalizer(voice=voice, format=format, settings=settings)

    def _create_text_normalizer(
        self, voice: Voice, format: TextFormat, settings: BaseNormalizationSettings
    ) -> TextNormalizer:
        factory = self._builders.get(f"{voice.locale}__{format.value}__{settings.type.value}")
        if factory is None:
            factory = self._builders.get(f"default__{format.value}__{settings.type.value}")

        if factory is None:
            logger.warning(
                "Text normalizer not found in factory. Locale: {locale}. Format: {format}. Type: {type}",
                locale=voice.locale,
                format=format.value,
                type=settings.type.value,
            )
            return None

        return factory(voice, settings)

    def create_text_normalizer(self, voice: Voice, format: TextFormat) -> TextNormalizer:
        if voice is None:
            raise TypeError("voice cannot be None")

        factory = self._factories.get(f"{voice.locale}__{format.value}")
        if factory is None:
            factory = self._factories.get(f"default__{format.value}")

        return factory(voice, format)
