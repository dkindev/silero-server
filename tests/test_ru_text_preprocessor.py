from src.tts.preprocessing import RuTextPreprocessor


class TestRuTextPreprocessor:
    """Tests for RuTextPreprocessor.process_text behavior."""

    def _avail(self):
        return "_.!,-:;?абвгдежзийклмнопрстуфхцчшщъыьэюяё "

    def test_short_text_returns_single_chunk(self):
        text = "привет мир"
        chunks = RuTextPreprocessor().process_text(text, 100, self._avail())
        assert chunks == ["привет мир"]

    def test_splits_on_sentence_boundary(self):
        text = "Иди сюда. Подожди минутку. Хорошо"
        chunks = RuTextPreprocessor().process_text(text, 20, self._avail())
        assert chunks == ["Иди сюда.", "Подожди минутку.", "Хорошо"]

    def test_razdel_handles_abbreviations(self):
        text = "Он т.е. пришёл. Да"
        chunks = RuTextPreprocessor().process_text(text, 18, self._avail())
        # "т.е." should not trigger a sentence split
        assert chunks == ["Он т.е. пришёл.", "Да"]

    def test_long_sentence_splits_on_comma(self):
        text = "это очень длинное предложение, разбитое запятой, и законченное"
        chunks = RuTextPreprocessor().process_text(text, 20, self._avail())
        assert chunks == [
            "это очень длинное",
            "предложение,",
            "разбитое запятой,",
            "и законченное",
        ]

    def test_hard_splits_giant_word(self):
        text = "супердлинноеслово"
        chunks = RuTextPreprocessor().process_text(text, 5, self._avail())
        assert chunks == ["супер", "длинн", "оесло", "во"]

    def test_strips_unsupported_characters(self):
        text = "привет! мир?"
        chunks = RuTextPreprocessor().process_text(text, 100, "абвгдежзийклмнопрстуфхцчшщъыьэюяё ")
        assert chunks == ["привет мир"]

    def test_empty_after_normalization_returns_empty(self):
        text = "12345"
        chunks = RuTextPreprocessor().process_text(text, 100, "абвгдежзийклмнопрстуфхцчшщъыьэюяё ")
        assert chunks == []
