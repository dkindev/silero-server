import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections.abc import Iterator

from loguru import logger

MINOR_CHARACTERS_RE = re.compile(r"(?<=[,:\-—;])\s+")
PUNCTUATIONS_RE = re.compile(r"(?<=[.!?\n])\s+")
WORD_RE = re.compile(r"\S+")


class TextSentenizer(ABC):
    """Represents a class for generating sentences from source text."""

    @abstractmethod
    def text_to_sentences(self, text: str, max_chunk_chars: int) -> Iterator[str]:
        ...


class PlainTextSentenizer(TextSentenizer):
    """Represents a class for generating sentences from plain text."""

    def text_to_sentences(self, text: str, max_chunk_chars: int) -> Iterator[str]:
        """Generate a sentences from an plain text."""
        if not text:
            return

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars cannot be negative or zero")

        if len(text) <= max_chunk_chars:
            yield text
            return

        pre_chunks = PlainTextSentenizer.sentenize_by_punctuations(text, max_chunk_chars)
        yield from self._assembly_small_chunks(chunks=pre_chunks, max_chunk_chars=max_chunk_chars)

    def _assembly_small_chunks(self, chunks: Iterator[str], max_chunk_chars: int) -> Iterator[str]:
        """Assembly of small pieces into optimal chunks up to max_chunk_chars"""
        current_chunk = []
        current_length = 0
        item_length = 0

        for item in chunks:
            item = item.strip()
            if not item:
                continue

            item_length = len(item)

            if current_length + item_length > max_chunk_chars:
                if current_chunk:
                    yield " ".join(current_chunk)
                current_chunk = [item]
                current_length = item_length
            else:
                current_chunk.append(item)
                current_length += item_length + 1

        if current_chunk:
            yield " ".join(current_chunk)

    @staticmethod
    def sentenize_by_punctuations(sentence: str, max_chars: int) -> Iterator[str]:
        last_idx = 0

        for match in PUNCTUATIONS_RE.finditer(sentence):
            chunk = sentence[last_idx : match.start()].strip()
            last_idx = match.end()

            if chunk:
                if len(chunk) <= max_chars:
                    yield chunk
                else:
                    yield from PlainTextSentenizer.sentenize_by_minor_characters(chunk, max_chars)

        last_chunk = sentence[last_idx:].strip()
        if last_chunk:
            if len(last_chunk) <= max_chars:
                yield last_chunk
            else:
                yield from PlainTextSentenizer.sentenize_by_minor_characters(last_chunk, max_chars)

    @staticmethod
    def sentenize_by_minor_characters(sentence: str, max_chars: int) -> Iterator[str]:
        last_idx = 0

        for match in MINOR_CHARACTERS_RE.finditer(sentence):
            chunk = sentence[last_idx : match.start()].strip()
            last_idx = match.end()

            if chunk:
                if len(chunk) <= max_chars:
                    yield chunk
                else:
                    # if the sentence is still longer than the limit (for example, 500 characters without spaces)
                    yield from PlainTextSentenizer.sentenize_by_words(chunk, max_chars)

        last_chunk = sentence[last_idx:].strip()
        if last_chunk:
            if len(last_chunk) <= max_chars:
                yield last_chunk
            else:
                yield from PlainTextSentenizer.sentenize_by_words(last_chunk, max_chars)

    @staticmethod
    def sentenize_by_words(sentence: str, max_chars: int) -> Iterator[str]:
        chunk_start = -1
        chunk_end = -1

        for match in WORD_RE.finditer(sentence):
            w_start, w_end = match.start(), match.end()
            w_len = w_end - w_start

            # If ONE word is longer than the limit (link, token, long hash)
            if w_len > max_chars:
                if chunk_start != -1:
                    yield sentence[chunk_start:chunk_end]
                    chunk_start, chunk_end = -1, -1

                # Let's cut this giant word character by character right here.
                word = match.group()
                for i in range(0, w_len, max_chars):
                    yield word[i : i + max_chars]
                continue

            if chunk_start == -1:
                chunk_start, chunk_end = w_start, w_end
                continue

            potential_len = w_end - chunk_start

            if potential_len > max_chars:
                yield sentence[chunk_start:chunk_end]
                chunk_start, chunk_end = w_start, w_end
            else:
                chunk_end = w_end

        if chunk_start != -1:
            yield sentence[chunk_start:chunk_end]


TAGS_RE = re.compile(r"<[^>]+>")
TAGS_SPLIT_RE = re.compile(r"(<[^>]+>|[^<]+)")
EMPTY_XML_NODES_RE = re.compile(r"<(\w+)[^>]*>\s*</\1>")
OPENING_TAG_RE = re.compile(r"<([a-zA-Z0-9]+)")
TAG_TRAILING_WHITESPACE_RE = re.compile(r"(\s+)(?=<|</)")


class SsmlSentenizer(TextSentenizer):
    """Represents a class for generating sentences from SSML."""

    def __init__(self, text_sentenizer_in_tags: TextSentenizer):
        self._text_sentenizer_in_tags = text_sentenizer_in_tags

    def text_to_sentences(self, text: str, max_chunk_chars: int) -> Iterator[str]:
        """Generate a sentences from an SSML."""
        if not text:
            return

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars cannot be negative or zero")

        ssml_text = text.strip()
        if not ssml_text.startswith("<speak>"):
            ssml_text = f"<speak>{ssml_text}</speak>"

        try:
            # Check the source document for overall validity
            ET.fromstring(ssml_text)
        except ET.ParseError as e:
            logger.warning(
                "SSML isn't valid. Falling back to text splitting. Exception: {exc}", exc=e
            )

            clean_text = TAGS_RE.sub("", ssml_text)
            for chunk in self._text_sentenizer_in_tags.text_to_sentences(
                clean_text, max_chunk_chars
            ):
                yield f"<speak>{chunk}</speak>"

            return

        if len(ssml_text) <= max_chunk_chars:
            yield ssml_text
            return

        yield from self._sentenize_ssml_into_chunks(ssml_text, max_chunk_chars)

    def _sentenize_ssml_into_chunks(self, ssml_text: str, max_chunk_chars: int) -> Iterator[str]:  # noqa: C901
        current_chunk = []
        text_len = 0
        opened_tags = []

        if ssml_text.startswith("<speak>") and ssml_text.endswith("</speak>"):
            ssml_content = ssml_text[7:-8]
        else:
            ssml_content = ssml_text

        for match in TAGS_SPLIT_RE.finditer(ssml_content):
            token = match.group(1)
            if not token:
                continue

            if token.startswith("<"):
                current_chunk.append(token)

                if token.endswith("/>"):
                    continue

                if not token.startswith("</"):
                    tag_match = OPENING_TAG_RE.match(token)
                    if tag_match:
                        opened_tags.append(tag_match.group(1))
                else:
                    tag_match = OPENING_TAG_RE.match(token.replace("/", ""))
                    if tag_match and opened_tags and opened_tags[-1] == tag_match.group(1):
                        opened_tags.pop()

            else:
                if text_len + len(token) <= max_chunk_chars:
                    current_chunk.append(token)
                    text_len += len(token)
                else:
                    prefix_tokens = [f"<{tag}>" for tag in opened_tags]

                    if text_len > 0:
                        yield self._build_valid_chunk(current_chunk, opened_tags)
                        current_chunk = []
                        text_len = 0

                    if len(token) <= max_chunk_chars:
                        current_chunk = prefix_tokens + [token]
                        text_len = len(token)
                    else:
                        for sub_sentence in self._text_sentenizer_in_tags.text_to_sentences(
                            token, max_chunk_chars
                        ):
                            yield self._build_valid_chunk(
                                prefix_tokens + [sub_sentence], opened_tags
                            )

                        opened_tags.clear()
                        current_chunk = prefix_tokens

        if current_chunk and text_len > 0:
            yield self._build_valid_chunk(current_chunk, opened_tags)

    @staticmethod
    def _build_valid_chunk(tokens: list[str], opened_tags: list[str]) -> str:
        """Assembles, cleans up, and wraps a chunk in valid SSML structure."""
        raw_chunk = "".join(tokens)

        if opened_tags:
            closing_str = "".join(f"</{tag}>" for tag in reversed(opened_tags))
            raw_chunk += closing_str

        cleaned = TAG_TRAILING_WHITESPACE_RE.sub("", raw_chunk)
        cleaned = EMPTY_XML_NODES_RE.sub("", cleaned)
        cleaned = cleaned.strip()

        return f"<speak>{cleaned}</speak>"
