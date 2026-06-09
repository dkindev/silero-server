import re
import xml.etree.ElementTree as ET

from loguru import logger


class TextPreprocessor:
    def _normalize_text(self, text: str, available_chars: str) -> str:
        normalize_text = text.strip()
        if available_chars:
            joined_pattern = "".join(re.escape(sym) for sym in available_chars)
            pattern = rf"[^{joined_pattern} ]"
            normalize_text = re.sub(pattern, "", normalize_text, flags=re.IGNORECASE)

        return normalize_text

    def process_text(self, text: str, max_chunk_chars: int, available_chars: str) -> list[str]:
        normalize_text = self._normalize_text(text, available_chars)
        sentences = re.split(r"(?<=[.!?\n])\s+", normalize_text)

        pre_chunks = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If the sentence is of normal size, leave it.
            if len(sentence) <= max_chunk_chars:
                pre_chunks.append(sentence)
            else:
                # If the sentence is long, try to cut it into minor characters.
                for chunk in TextPreprocessor.split_by_minor_characters(sentence, max_chunk_chars):
                    pre_chunks.append(chunk)

        # Final assembly of small pieces into optimal chunks up to max_chunk_chars
        final_chunks = []
        current_chunk = []
        current_length = 0

        for item in pre_chunks:
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

    def process_ssml(self, text: str, max_chunk_chars: int, available_chars: str) -> list[str]:
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
            clean_text = re.sub(r"<[^>]+>", "", ssml_text)
            return [
                f"<speak>{chunk}</speak>"
                for chunk in self.process_text(clean_text, max_chunk_chars, available_chars)
            ]

        chunks = self._split_ssml_into_chunks(ssml_text, max_chunk_chars, available_chars)
        validated_chunks = TextPreprocessor.clean_up_chunks(chunks)

        return validated_chunks

    def _split_ssml_into_chunks(
        self, ssml_text: str, max_chunk_chars: int, available_chars: str
    ) -> list[str]:
        raw_tokens = re.split(r"(<[^>]+>)", ssml_text)

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
                parsed_xml_tag = TextPreprocessor.process_xml_tag(token, active_tags_stack)
                if parsed_xml_tag:
                    current_chunk_xml += parsed_xml_tag

            # 2. If the token is the text between the tags
            else:
                if not token.strip():
                    current_chunk_xml += token
                    continue

                text_phrases = self.process_text(token, max_chunk_chars, available_chars)

                for phrase in text_phrases:
                    phrase_len = len(phrase)

                    # If adding a phrase exceeds the chunk size
                    if (
                        current_chunk_text_len + phrase_len > max_chunk_chars
                        and current_chunk_xml.strip()
                    ):
                        chunks.append(
                            TextPreprocessor.process_xml_chunk(current_chunk_xml, active_tags_stack)
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
            chunks.append(TextPreprocessor.process_xml_chunk(current_chunk_xml, active_tags_stack))

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
        tag_match = re.match(r"<([a-zA-Z0-9]+)", token)
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
                exc=e,
            )
            clean_candidate = re.sub(r"<[^>]+>", "", full_chunk_candidate)
            return f"<speak>{clean_candidate}</speak>"

    @staticmethod
    def clean_up_chunks(chunks: list[str]) -> list[str]:
        # Strip trailing whitespace from every chunk's text content
        validated_chunks = []
        for ch in chunks:
            # Strip trailing whitespace from every chunk's text content
            ch = re.sub(r"(\s+)(?=<|</)", "", ch)
            # Final cleanup of empty XML nodes (e.g. <p></p>)
            ch = re.sub(r"<(\w+)[^>]*>\s*</\1>", "", ch)
            if ch.replace("<speak>", "").replace("</speak>", "").strip():
                validated_chunks.append(ch)

        return validated_chunks

    @staticmethod
    def split_by_words(sentence: str, max_chars: int) -> list[str]:
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

    @staticmethod
    def split_by_minor_characters(sentence: str, max_chars: int) -> list[str]:
        pre_chunks = []
        sub_sentences = re.split(r"(?<=[,:\-—;])\s+", sentence)
        for sub in sub_sentences:
            sub = sub.strip()
            if not sub:
                continue

            # if the sentence is still longer than the limit (for example, 500 characters without spaces)
            if len(sub) > max_chars:
                # Forced cutting by words (spaces)
                for chunk in TextPreprocessor.split_by_words(sub, max_chars):
                    pre_chunks.append(chunk)
            else:
                pre_chunks.append(sub)

        return pre_chunks
