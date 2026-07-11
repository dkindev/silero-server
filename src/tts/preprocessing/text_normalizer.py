import re
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator

from src.tts.models import NormalizationOptions


class TextNormalizer(ABC):
    """Represents the class to normalize raw text."""

    @abstractmethod
    def normalize_text(
        self, sentences: Iterator[str], options: NormalizationOptions
    ) -> AsyncIterator[str]:
        """Return a normalized string from raw text."""
        ...


class PlainTextNormalizer(TextNormalizer):
    """Represents the class to normalize plain text."""

    async def normalize_text(
        self, sentences: Iterator[str], options: NormalizationOptions
    ) -> AsyncIterator[str]:
        """Return a normalized string from plain text."""
        if sentences is None:
            raise TypeError("sentences cannot be None")

        available_chars_re = None

        # ignore unavailable symbols
        if options and options.silero_model is not None:
            if hasattr(options.silero_model, "symbols"):
                joined_pattern = "".join(re.escape(sym) for sym in options.silero_model.symbols)
                available_chars_re = rf"[^{joined_pattern} ]"

        for sentence in sentences:
            normalized_sentence = sentence.strip()
            if not normalized_sentence:
                continue

            if available_chars_re:
                normalized_sentence = re.sub(
                    available_chars_re, "", normalized_sentence, flags=re.IGNORECASE
                )

            yield normalized_sentence


class SsmlNormalizer(TextNormalizer):
    """Represents the class to normalize SSML."""

    async def normalize_text(
        self, sentences: Iterator[str], options: NormalizationOptions
    ) -> AsyncIterator[str]:
        """Return a normalized SSML from raw SSML string."""
        if sentences is None:
            raise TypeError("sentences cannot be None")

        for sentence in sentences:
            normalized_sentence = sentence.strip()
            if not normalized_sentence:
                continue

            yield normalized_sentence
