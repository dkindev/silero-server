from typing import Literal


def preprocess_text(text: str, input_type: Literal["TEXT", "SSML", "RAWMARYXML"]) -> str | None:
    if input_type == "RAWMARYXML":
        return None
    if input_type == "TEXT":
        return text
    if input_type == "SSML":
        return _extract_text_from_ssml(text)
    return text


def _extract_text_from_ssml(text: str) -> str:
    from html.parser import HTMLParser

    class _TextExtractor(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self._parts: list[str] = []

        def handle_data(self, data: str) -> None:
            if self._parts:
                self._parts.append(" ")
            self._parts.append(data)

        def get_text(self) -> str:
            return "".join(self._parts)

    parser = _TextExtractor()
    parser.feed(text)
    return parser.get_text()
