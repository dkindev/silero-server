from src.tts.preprocessing import TextPreprocessor


class TestTextPreprocessorProcessSSML:
    """Tests for TextPreprocessor.process_ssml behavior."""

    def test_valid_ssml_preserves_structure(self):
        text = "<speak>hello world</speak>"
        chunks = TextPreprocessor().process_ssml(text, 100, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == ["<speak>hello world</speak>"]

    def test_invalid_ssml_falls_back_to_text_split(self):
        text = "<speak><p>hello</speak>"
        chunks = TextPreprocessor().process_ssml(text, 100, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == ["<speak>hello</speak>"]

    def test_ssml_splits_long_text_and_reopens_tags(self):
        text = "<speak><p>hello world foo bar baz</p></speak>"
        chunks = TextPreprocessor().process_ssml(text, 10, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == [
            "<speak><p>hello</p></speak>",
            "<speak><p>world foo</p></speak>",
            "<speak><p>bar baz</p></speak>",
        ]


class TestTextPreprocessorProcessText:
    """Tests for TextPreprocessor.process_text behavior."""

    def test_short_text_returns_single_chunk(self):
        text = "hello world"
        available = "abcdefghijklmnopqrstuvwxyz "
        chunks = TextPreprocessor().process_text(text, 100, available)
        assert chunks == ["hello world"]

    def test_long_text_splits_on_sentence_boundary(self):
        text = "first sentence here. second one longer. third one"
        available = "abcdefghijklmnopqrstuvwxyz."
        chunks = TextPreprocessor().process_text(text, 20, available)
        assert chunks == ["first sentence here.", "second one longer.", "third one"]

    def test_long_sentence_splits_on_minor_punctuation(self):
        text = "this is a very long sentence, broken by a comma, and then ended"
        available = "abcdefghijklmnopqrstuvwxyz,"
        chunks = TextPreprocessor().process_text(text, 20, available)
        assert chunks == [
            "this is a very long",
            "sentence,",
            "broken by a comma,",
            "and then ended",
        ]

    def test_splits_by_words_when_no_punctuation(self):
        text = "hello world foo bar"
        chunks = TextPreprocessor().process_text(text, 10, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == ["hello", "world foo", "bar"]

    def test_hard_splits_giant_word(self):
        text = "superlongword"
        chunks = TextPreprocessor().process_text(text, 5, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == ["super", "longw", "ord"]

    def test_strips_unsupported_characters(self):
        text = "hello! world?"
        chunks = TextPreprocessor().process_text(text, 100, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == ["hello world"]

    def test_empty_after_normalization_returns_empty(self):
        text = "12345"
        chunks = TextPreprocessor().process_text(text, 100, "abcdefghijklmnopqrstuvwxyz ")
        assert chunks == []
