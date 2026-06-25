import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

from loguru import logger

MINOR_CHARACTERS_RE = re.compile(r"(?<=[,:\-—;])\s+")
PUNCTUATIONS_RE = re.compile(r"(?<=[.!?\n])\s+")


class TextSentenizer(ABC):
    """Represents a class for generating sentences from source text."""

    @abstractmethod
    def text_to_sentences(self, text: str, max_chunk_chars: int) -> list[str]:
        ...


class SimpleTextSentenizer(TextSentenizer):
    """Represents a class for generating sentences from simple text."""

    def text_to_sentences(self, text: str, max_chunk_chars: int) -> list[str]:
        """Generate a sentences from an simple text."""
        if not text:
            return []

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars cannot be negative")

        if len(text) <= max_chunk_chars:
            return [text]

        pre_chunks = SimpleTextSentenizer.sentenize_by_punctuations(text, max_chunk_chars)
        return self._assembly_small_chunks(chunks=pre_chunks, max_chunk_chars=max_chunk_chars)

    def _assembly_small_chunks(self, chunks: list[str], max_chunk_chars: int) -> list[str]:
        """Assembly of small pieces into optimal chunks up to max_chunk_chars"""
        final_chunks = []
        current_chunk = []
        current_length = 0

        for item in chunks:
            if current_length + len(item) + 1 > max_chunk_chars:
                if current_chunk:
                    final_chunks.append(" ".join(current_chunk))
                current_chunk = [item]
                current_length = len(item)
            else:
                current_chunk.append(item)
                current_length += len(item) + 1

        if current_chunk:
            final_chunks.append(" ".join(current_chunk))

        return [c for c in final_chunks if c.strip()]

    @staticmethod
    def sentenize_by_punctuations(sentence: str, max_chars: int) -> list[str]:
        sentences = PUNCTUATIONS_RE.split(sentence)

        pre_chunks = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If the sentence is of normal size, leave it.
            if len(sentence) <= max_chars:
                pre_chunks.append(sentence)
            else:
                # If the sentence is long, try to cut it into minor characters.
                for chunk in SimpleTextSentenizer.sentenize_by_minor_characters(
                    sentence, max_chars
                ):
                    pre_chunks.append(chunk)

        return pre_chunks

    @staticmethod
    def sentenize_by_minor_characters(sentence: str, max_chars: int) -> list[str]:
        sub_sentences = MINOR_CHARACTERS_RE.split(sentence)

        pre_chunks = []
        for sub in sub_sentences:
            sub = sub.strip()
            if not sub:
                continue

            # if the sentence is still longer than the limit (for example, 500 characters without spaces)
            if len(sub) > max_chars:
                # Forced cutting by words (spaces)
                for chunk in SimpleTextSentenizer.sentenize_by_words(sub, max_chars):
                    pre_chunks.append(chunk)
            else:
                pre_chunks.append(sub)

        return pre_chunks

    @staticmethod
    def sentenize_by_words(sentence: str, max_chars: int) -> list[str]:
        pre_chunks = []
        words = sentence.split(" ")
        current_sub_chunk = []
        current_sub_len = 0

        for word in words:
            # If the word itself is longer than the limit (rare case/link), we cut it character by character
            if len(word) > max_chars:
                if current_sub_chunk:
                    pre_chunks.append(" ".join(current_sub_chunk))
                    current_sub_chunk = []
                    current_sub_len = 0
                # We cut the giant word into pieces strictly according to the limit
                for i in range(0, len(word), max_chars):
                    pre_chunks.append(word[i : i + max_chars])
                continue

            if current_sub_len + len(word) + 1 > max_chars:
                pre_chunks.append(" ".join(current_sub_chunk))
                current_sub_chunk = [word]
                current_sub_len = len(word)
            else:
                current_sub_chunk.append(word)
                current_sub_len += len(word) + 1

        if current_sub_chunk:
            pre_chunks.append(" ".join(current_sub_chunk))

        return pre_chunks


TAGS_RE = re.compile(r"<[^>]+>")
TAGS_SPLIT_RE = re.compile(r"(<[^>]+>)")
EMPTY_XML_NODES_RE = re.compile(r"<(\w+)[^>]*>\s*</\1>")
OPENING_TAG_RE = re.compile(r"<([a-zA-Z0-9]+)")
TAG_TRAILING_WHITESPACE_RE = re.compile(r"(\s+)(?=<|</)")


class SsmlSentenizer(TextSentenizer):
    """Represents a class for generating sentences from SSML."""

    def __init__(self, text_sentenizer_in_tags: TextSentenizer):
        self._text_sentenizer_in_tags = text_sentenizer_in_tags

    def text_to_sentences(self, text: str, max_chunk_chars: int) -> list[str]:
        """Generate a sentences from an SSML."""
        if not text:
            return []

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars cannot be negative")

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
            return [
                f"<speak>{chunk}</speak>"
                for chunk in self._text_sentenizer_in_tags.text_to_sentences(
                    clean_text, max_chunk_chars
                )
            ]

        if len(ssml_text) <= max_chunk_chars:
            return [ssml_text]

        chunks = self._sentenize_ssml_into_chunks(ssml_text, max_chunk_chars)
        validated_chunks = SsmlSentenizer.clean_up_chunks(chunks)

        return validated_chunks

    def _sentenize_ssml_into_chunks(self, ssml_text: str, max_chunk_chars: int) -> list[str]:
        raw_tokens = TAGS_SPLIT_RE.split(ssml_text)

        # Stack for active tags (maintaining LIFO structure)
        # Stores dictionaries: {"tag": "tag_name", "open": "full_opening_string"}
        active_tags_stack = []
        chunks = []

        current_chunk_xml = ""
        current_chunk_text_len = 0

        for token in raw_tokens:
            if not token:
                continue

            # 1. If the token is an XML tag
            if token.startswith("<") and token.endswith(">"):
                parsed_xml_tag = SsmlSentenizer.process_xml_tag(token, active_tags_stack)
                if parsed_xml_tag:
                    current_chunk_xml += parsed_xml_tag

            # 2. If the token is the text between the tags
            else:
                if not token.strip():
                    current_chunk_xml += token
                    continue

                text_phrases = self._text_sentenizer_in_tags.text_to_sentences(
                    token, max_chunk_chars
                )

                for phrase in text_phrases:
                    phrase_len = len(phrase)

                    # If adding a phrase exceeds the chunk size
                    if (
                        current_chunk_text_len + phrase_len > max_chunk_chars
                        and current_chunk_xml.strip()
                    ):
                        chunks.append(
                            SsmlSentenizer.process_xml_chunk(current_chunk_xml, active_tags_stack)
                        )
                        # Reset the buffer and OPEN all the tags from the stack in DIRECT order in a new chunk.
                        current_chunk_xml = ""
                        for atag in active_tags_stack:
                            current_chunk_xml += atag["open"]
                        current_chunk_text_len = 0

                    current_chunk_xml += phrase + " "
                    current_chunk_text_len += phrase_len

        # Write the last remaining chunk
        if current_chunk_xml.strip():
            chunks.append(SsmlSentenizer.process_xml_chunk(current_chunk_xml, active_tags_stack))

        return chunks

    @staticmethod
    def process_xml_tag(token: str, active_tags_stack: list) -> str:
        if token.startswith("<speak") or token == "</speak>":
            return ""

        # Self-closing tag (e.g. <break time="500ms"/>)
        if token.endswith("/>"):
            return token

        # Closing tag (e.g. </prosody> or </s>)
        if token.startswith("</"):
            # Safely pop the LAST open tag from the stack
            if active_tags_stack:
                active_tags_stack.pop()
            return token

        # Opening tag (e.g. <prosody pitch="x-low">)
        tag_match = OPENING_TAG_RE.match(token)
        if tag_match:
            tag_name = tag_match.group(1)
            # Add the tag with its entire opening string to the stack
            active_tags_stack.append({"tag": tag_name, "open": token})
            return token

        return ""

    @staticmethod
    def process_xml_chunk(chunk: str, active_tags_stack: list) -> str:
        # Assemble a candidate chunk: close all tags from the stack in REVERSE order
        for atag in reversed(active_tags_stack):
            chunk += f"</{atag['tag']}>"
        full_chunk_candidate = f"<speak>{chunk}</speak>"

        try:
            ET.fromstring(full_chunk_candidate)
            return full_chunk_candidate
        except ET.ParseError as e:
            # In case of an unexpected structure failure, clear the chunk of tags.
            logger.warning(
                "Chunk validation error for SSML '{ssml_text}'. Clear the chunk of tags. Exception: {exc}",
                ssml_text=full_chunk_candidate,
                exc=str(e),
            )
            clean_candidate = TAGS_RE.sub("", full_chunk_candidate)
            return f"<speak>{clean_candidate}</speak>"

    @staticmethod
    def clean_up_chunks(chunks: list[str]) -> list[str]:
        validated_chunks = []
        for ch in chunks:
            # Strip trailing whitespace from every chunk's text content
            ch = TAG_TRAILING_WHITESPACE_RE.sub("", ch)
            # Final cleanup of empty XML nodes (e.g. <p></p>)
            ch = EMPTY_XML_NODES_RE.sub("", ch)
            if ch.replace("<speak>", "").replace("</speak>", "").strip():
                validated_chunks.append(ch)

        return validated_chunks
