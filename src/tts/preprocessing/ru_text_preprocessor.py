from razdel import sentenize

from src.tts.preprocessing.text_preprocessor import TextPreprocessor


class RuTextPreprocessor(TextPreprocessor):
    def process_text(self, text: str, max_chars: int, available_chars: str) -> list[str]:
        normalize_text = self._normalize_text(text, available_chars)
        sentences = [s.text for s in sentenize(normalize_text)]

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
                for chunk in TextPreprocessor.split_by_minor_characters(sentence, max_chars):
                    pre_chunks.append(chunk)

        # Final assembly of small pieces into optimal chunks up to max_chars
        final_chunks = []
        current_chunk = []
        current_length = 0

        for item in pre_chunks:
            if current_length + len(item) + 1 > max_chars:
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
