from src.tts.preprocessing import PlainTextSentenizer, SimpleTextNormalizer, SsmlSentenizer


class TestSsmlSentenizer:
    """Tests for SsmlSentenizer.text_to_sentences behavior."""

    def test_valid_ssml_preserves_structure(self):
        text = "<speak>hello world</speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 100))
        assert chunks == ["<speak>hello world</speak>"]

    def test_invalid_ssml_falls_back_to_text_split(self):
        text = "<speak><p>hello</speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 100))
        assert chunks == ["<speak>hello</speak>"]

    def test_empty_ssml_return_empty_chunk(self):
        text = "<speak></speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 10))
        assert len(chunks) == 0

    def test_empty_ssml_tag_return_empty_chunk(self):
        text = "<speak><p></p></speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 10))
        assert len(chunks) == 0

    def test_ssml_splits_long_text_and_reopens_tags(self):
        text = "<speak><p>hello world foo bar baz</p></speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 10))
        assert chunks == [
            "<speak><p>hello</p></speak>",
            "<speak><p>world foo</p></speak>",
            "<speak><p>bar baz</p></speak>",
        ]

    def test_nested_tag_not_swallowed_by_skip_closing(self):
        text = "<speak><p>LONGWORDSHERE <s>inner</s> tail</p></speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 10))
        assert chunks == [
            "<speak><p>LONGWORDSH</p></speak>",
            "<speak><p>ERE</p></speak>",
            "<speak><p><s>inner</s> tail</p></speak>",
        ]

    def test_double_nesting_with_overflow_at_outer_level(self):
        text = "<speak><p><s>LONGWORDSHERE inner</s>tail</p></speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 10))
        assert chunks == [
            "<speak><p><s>LONGWORDSH</s></p></speak>",
            "<speak><p><s>ERE inner</s></p></speak>",
            "<speak><p>tail</p></speak>",
        ]

    def test_sibling_tags_after_long_text_overflow(self):
        text = "<speak><p>LONGWORDSHERE <s>inner</s><b>bold</b></p></speak>"
        chunks = list(SsmlSentenizer(PlainTextSentenizer()).text_to_sentences(text, 10))
        assert chunks == [
            "<speak><p>LONGWORDSH</p></speak>",
            "<speak><p>ERE</p></speak>",
            "<speak><p><s>inner</s><b>bold</b></p></speak>",
        ]


class TestSimpleTextSentenizer:
    """Tests for SimpleTextSentenizer.text_to_sentences behavior."""

    def test_short_text_returns_single_chunk(self):
        text = "hello world"
        chunks = list(PlainTextSentenizer().text_to_sentences(text, 100))
        assert chunks == ["hello world"]

    def test_long_text_splits_on_sentence_boundary(self):
        text = "first sentence here. second one longer. third one"
        chunks = list(PlainTextSentenizer().text_to_sentences(text, 20))
        assert chunks == ["first sentence here.", "second one longer.", "third one"]

    def test_long_sentence_splits_on_minor_punctuation(self):
        text = "this is a very long sentence, broken by a comma, and then ended"
        chunks = list(PlainTextSentenizer().text_to_sentences(text, 20))
        assert chunks == [
            "this is a very long",
            "sentence,",
            "broken by a comma,",
            "and then ended",
        ]

    def test_splits_by_words_when_no_punctuation(self):
        text = "hello world foo bar"
        chunks = list(PlainTextSentenizer().text_to_sentences(text, 10))
        assert chunks == ["hello", "world foo", "bar"]

    def test_hard_splits_giant_word(self):
        text = "superlongword"
        chunks = list(PlainTextSentenizer().text_to_sentences(text, 5))
        assert chunks == ["super", "longw", "ord"]

    def test_strips_unsupported_characters(self):
        text = "hello! world?"
        normalized = SimpleTextNormalizer().normalize_text(text, "abcdefghijklmnopqrstuvwxyz ")
        chunks = list(PlainTextSentenizer().text_to_sentences(normalized, 100))
        assert chunks == ["hello world"]

    def test_empty_after_normalization_returns_empty(self):
        text = "12345"
        normalized = SimpleTextNormalizer().normalize_text(text, "abcdefghijklmnopqrstuvwxyz ")
        chunks = list(PlainTextSentenizer().text_to_sentences(normalized, 100))
        assert chunks == []
