from collections.abc import Iterator

from razdel import sentenize

from src.tts.preprocessing.text_sentenizer import PlainTextSentenizer


class RuPlainTextSentenizer(PlainTextSentenizer):
    """Represents a class for generating sentences from Russian text."""

    def text_to_sentences(self, text: str, max_chunk_chars: int) -> Iterator[str]:
        """Generate a sentences from an plain text."""
        if not text:
            return

        if max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars cannot be negative or zero")

        if len(text) <= max_chunk_chars:
            yield text
            return

        pre_chunks = RuPlainTextSentenizer.sentenize_by_nlp(
            sentence=text, max_chars=max_chunk_chars
        )
        yield from self._assembly_small_chunks(chunks=pre_chunks, max_chunk_chars=max_chunk_chars)

    @staticmethod
    def sentenize_by_nlp(sentence: str, max_chars: int) -> Iterator[str]:
        for chunk in sentenize(sentence):
            chunk_text = chunk.text.strip()
            if not chunk_text:
                continue

            if len(chunk_text) <= max_chars:
                yield chunk_text
            else:
                # If the sentence is long, try to cut it into minor characters.
                yield from PlainTextSentenizer.sentenize_by_minor_characters(
                    sentence=chunk_text, max_chars=max_chars
                )
