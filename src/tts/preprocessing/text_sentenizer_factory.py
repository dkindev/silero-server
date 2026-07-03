from loguru import logger

from src.tts.models import TextFormat, Voice
from src.tts.preprocessing import (
    PlainTextSentenizer,
    RuPlainTextSentenizer,
    SsmlSentenizer,
    TextSentenizer,
)


class TextSentenizerFactory:
    def __init__(self):
        self._builders: dict[str, type[TextSentenizer]] = {
            # key: "{locale}__{text_format}"
            "default__text": PlainTextSentenizer,
            "default__ssml": lambda: SsmlSentenizer(text_sentenizer_in_tags=PlainTextSentenizer()),
            "ru_RU__text": RuPlainTextSentenizer,
            "ru_RU__ssml": lambda: SsmlSentenizer(text_sentenizer_in_tags=RuPlainTextSentenizer()),
        }

    def create_text_sentenizer(self, voice: Voice, format: TextFormat) -> TextSentenizer:
        if voice is None:
            raise TypeError("voice cannot be None")

        builder = self._builders.get(f"{voice.locale}__{format.value}")

        if builder is None:
            builder = self._builders.get(f"default__{format.value}")

        if builder is None:
            logger.warning(
                "Text sentenizer not found in factory. Locale: {locale}. Format: {format}",
                locale=voice.locale,
                format=format.value,
            )
            return None

        return builder()
