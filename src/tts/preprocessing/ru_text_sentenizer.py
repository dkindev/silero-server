from razdel import sentenize

from src.tts.preprocessing.text_sentenizer import SimpleTextSentenizer


class RuSimpleTextSentenizer(SimpleTextSentenizer):
    """Represents a class for generating sentences from Russian text."""

    def text_to_sentences(self, text: str, max_chunk_chars: int) -> list[str]:
        """Generate a sentences from an simple text."""
        if not text:
            return []

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars cannot be negative")

        if len(text) <= max_chunk_chars:
            return [text]

        sentences = [s.text for s in sentenize(text)]

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
                for chunk in SimpleTextSentenizer.sentenize_by_minor_characters(
                    sentence, max_chunk_chars
                ):
                    pre_chunks.append(chunk)

        return self._assembly_small_chunks(chunks=pre_chunks, max_chunk_chars=max_chunk_chars)
