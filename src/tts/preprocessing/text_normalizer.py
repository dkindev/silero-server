import re
from abc import ABC, abstractmethod


class TextNormalizer(ABC):
    """Represents the class to normalize raw text."""

    @abstractmethod
    def normalize_text(self, text: str, available_chars: str | None = None) -> str:
        """Return a normalized string from raw text."""
        ...


class SimpleTextNormalizer(TextNormalizer):
    """Represents the class to normalize simple text."""

    def normalize_text(self, text: str, available_chars: str | None = None) -> str:
        """Return a normalized string from raw text."""
        normalized_text = text.strip()
        if not normalized_text:
            return normalized_text

        if available_chars:
            joined_pattern = "".join(re.escape(sym) for sym in available_chars)
            pattern = rf"[^{joined_pattern} ]"
            normalized_text = re.sub(pattern, "", normalized_text, flags=re.IGNORECASE)

        return normalized_text


class SsmlNormalizer(TextNormalizer):
    """Represents the class to normalize SSML."""

    def normalize_text(self, text: str, available_chars: str | None = None) -> str:
        """Return a normalized SSML from raw SSML string."""
        return text.strip()
