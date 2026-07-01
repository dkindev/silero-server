from src.tts.preprocessing import RuPlainTextSentenizer, SimpleTextNormalizer


class TestRuSimpleTextSentenizer:
    """Tests for RuSimpleTextSentenizer.text_to_sentences behavior."""

    def test_short_text_returns_single_chunk(self):
        text = "привет мир"
        chunks = list(RuPlainTextSentenizer().text_to_sentences(text, 100))
        assert chunks == ["привет мир"]

    def test_splits_on_sentence_boundary(self):
        text = "Иди сюда. Подожди минутку. Хорошо"
        chunks = list(RuPlainTextSentenizer().text_to_sentences(text, 20))
        assert chunks == ["Иди сюда.", "Подожди минутку.", "Хорошо"]

    def test_razdel_handles_abbreviations(self):
        text = "Он т.е. пришёл. Да"
        chunks = list(RuPlainTextSentenizer().text_to_sentences(text, 17))
        # "т.е." should not trigger a sentence split
        assert chunks == ["Он т.е. пришёл.", "Да"]

    def test_long_sentence_splits_on_comma(self):
        text = "это очень длинное предложение, разбитое запятой, и законченное"
        chunks = list(RuPlainTextSentenizer().text_to_sentences(text, 20))
        assert chunks == [
            "это очень длинное",
            "предложение,",
            "разбитое запятой,",
            "и законченное",
        ]

    def test_hard_splits_giant_word(self):
        text = "супердлинноеслово"
        chunks = list(RuPlainTextSentenizer().text_to_sentences(text, 5))
        assert chunks == ["супер", "длинн", "оесло", "во"]

    def test_strips_unsupported_characters(self):
        text = "привет! мир?"
        normalized = SimpleTextNormalizer().normalize_text(
            text, "абвгдежзийклмнопрстуфхцчшщъыьэюяё "
        )
        chunks = list(RuPlainTextSentenizer().text_to_sentences(normalized, 100))
        assert chunks == ["привет мир"]

    def test_empty_after_normalization_returns_empty(self):
        text = "12345"
        normalized = SimpleTextNormalizer().normalize_text(
            text, "абвгдежзийклмнопрстуфхцчшщъыьэюяё "
        )
        chunks = list(RuPlainTextSentenizer().text_to_sentences(normalized, 100))
        assert chunks == []
