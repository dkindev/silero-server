import pytest

from src.tts.text import preprocess_text


@pytest.mark.parametrize(
    ("text", "input_type", "expected"),
    [
        ("hello", "TEXT", "hello"),
        ("", "TEXT", ""),
        ("hello world", "TEXT", "hello world"),
        ("< mary>", "TEXT", "< mary>"),
    ],
)
def test_text_input_passthrough(text, input_type, expected):
    """TEXT input type returns text unchanged."""
    assert preprocess_text(text, input_type) == expected


@pytest.mark.parametrize(
    ("text", "input_type", "expected"),
    [
        ("<speak>hello</speak>", "SSML", "hello"),
        ("hello <break/> world", "SSML", "hello world"),
        ("<speak>hello <break/> world</speak>", "SSML", "hello world"),
        ("<a><b>text</b></a>", "SSML", "text"),
        ("hello", "SSML", "hello"),
        ("", "SSML", ""),
        ("no tags", "SSML", "no tags"),
    ],
)
def test_ssml_strips_xml_tags(text, input_type, expected):
    """SSML input type strips XML tags, preserving text content."""
    assert preprocess_text(text, input_type) == expected


@pytest.mark.parametrize(
    ("text", "input_type"),
    [
        ("anything", "RAWMARYXML"),
        ("", "RAWMARYXML"),
        ("<speak>hello</speak>", "RAWMARYXML"),
    ],
)
def test_rawmaryxml_returns_none(text, input_type):
    """RAWMARYXML input type returns None (caller should emit 400)."""
    assert preprocess_text(text, input_type) is None
