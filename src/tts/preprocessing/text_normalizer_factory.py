from collections.abc import Callable

from loguru import logger
from openai import AsyncOpenAI

from src.config import BaseNormalizationSettings, NormalizationSettings
from src.tts.config_storage import SileroTTSConfigStorage
from src.tts.models import (
    OpenAiNormalizationConfig,
    TextFormat,
    Voice,
    VoiceNormalization,
)
from src.tts.preprocessing import (
    OpenAiTextNormalizer,
    PlainTextNormalizer,
    SsmlNormalizer,
    TextNormalizer,
)


class TextNormalizerFactory:
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        settings: NormalizationSettings,
        storage: SileroTTSConfigStorage,
    ):
        self._settings = settings
        self._storage = storage
        self._openai_client = openai_client

        def _create_openai_normalizer(
            voice: Voice,
            voice_normalization: VoiceNormalization,
            settings: BaseNormalizationSettings,
        ) -> TextNormalizer:
            if self._openai_client is None:
                return None

            promt = (
                self._storage.get_promt(promt_id=voice_normalization.promt_id)
                if voice_normalization is not None
                else None
            )

            if promt is not None:
                promt_text = promt.text
                promt_model = promt.model
            else:
                if settings.promts is None:
                    return None

                default_promt = settings.promts.get(voice.locale)
                if default_promt is None:
                    return None

                promt_text = default_promt.text
                promt_model = default_promt.model

            return OpenAiTextNormalizer(
                client=self._openai_client,
                config=OpenAiNormalizationConfig(
                    timeout=self._settings.timeout,
                    max_concurrent_chunks_per_request=self._settings.max_concurrent_chunks_per_request,
                    default_model=promt_model,
                    default_promt=promt_text,
                ),
            )

        self._builders: dict[
            str, Callable[[Voice, VoiceNormalization, BaseNormalizationSettings], TextNormalizer]
        ] = {
            # key: "{locale}__{text_format}__{normalization_type}"
            "default__text__simple": lambda v, vn, s: PlainTextNormalizer(),
            "default__ssml__simple": lambda v, vn, s: SsmlNormalizer(),
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
        return self._create_text_normalizer(
            voice=voice,
            format=format,
            default_normalization_enabled=settings.enabled,
            settings=settings,
        )

    def _create_ssml_normalizer_factory(self, voice: Voice, format: TextFormat) -> TextNormalizer:
        settings = self._settings.ssml
        return self._create_text_normalizer(
            voice=voice,
            format=format,
            default_normalization_enabled=settings.enabled,
            settings=settings,
        )

    def _create_text_normalizer(
        self,
        voice: Voice,
        format: TextFormat,
        default_normalization_enabled: bool,
        settings: BaseNormalizationSettings,
    ) -> TextNormalizer:
        voice_normalization = self._storage.get_voice_normalization(
            voice_id=voice.id, text_format=format
        )
        if voice_normalization is not None:
            if not voice_normalization.enabled:
                return None

            type = voice_normalization.type
        else:
            if not default_normalization_enabled:
                return None

            type = settings.type

        builder = self._builders.get(f"{voice.locale}__{format.value}__{type.value}")
        if builder is None:
            builder = self._builders.get(f"default__{format.value}__{type.value}")

        if builder is None:
            logger.warning(
                "Text normalizer not found in factory. Locale: {locale}. Format: {format}. Type: {type}",
                locale=voice.locale,
                format=format.value,
                type=type.value,
            )
            return None

        return builder(voice, voice_normalization, settings)

    def create_text_normalizer(self, voice: Voice, format: TextFormat) -> TextNormalizer:
        if voice is None:
            raise TypeError("voice cannot be None")

        factory = self._factories.get(f"{voice.locale}__{format.value}")
        if factory is None:
            factory = self._factories.get(f"default__{format.value}")

        return factory(voice, format)
